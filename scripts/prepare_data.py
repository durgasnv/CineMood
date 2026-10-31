#!/usr/bin/env python3
"""Acquire, clean and export CineMood research data using only Python's stdlib."""
import argparse
import collections
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import tarfile
import tempfile
import unicodedata
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "cornell_polarity_v2.tar.gz": "https://www.cs.cornell.edu/people/pabo/movie-review-data/review_polarity.tar.gz",
    "iitp_hindi_kaggle.zip": "https://www.kaggle.com/api/v1/datasets/download/warcoder/iit-patna-movie-reviews-hindi",
}
THRESHOLD = 0.90


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, payload):
    """Publish complete bytes without leaving a partially written file on failure."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def acquire_sources(root, download=False):
    """Require the checked-in lock and validate downloads before caching them."""
    lock_path = root / "data/source_lock.json"
    if not lock_path.exists():
        raise ValueError("Missing data/source_lock.json; restore the reviewed source lock before preparing data")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if not isinstance(lock, dict) or set(lock) != set(SOURCES):
        raise ValueError("Source lock must contain exactly the configured source archives")
    fingerprints = {}
    for filename, url in SOURCES.items():
        expected = lock[filename]
        if (not isinstance(expected, dict) or expected.get("url") != url
                or not isinstance(expected.get("bytes"), int) or expected["bytes"] <= 0
                or not isinstance(expected.get("sha256"), str) or len(expected["sha256"]) != 64
                or any(c not in "0123456789abcdef" for c in expected["sha256"])):
            raise ValueError(f"Invalid source lock entry for {filename}")
    for filename, url in SOURCES.items():
        path = root / "data/raw" / filename
        expected = lock[filename]
        missing = not path.exists()
        if missing:
            if not download:
                raise ValueError(f"Missing {path}; run with --download or follow docs/data_preparation.md")
            with urllib.request.urlopen(url, timeout=60) as response:
                payload = response.read()
        else:
            payload = path.read_bytes()
        actual = {"url": url, "sha256": digest(payload), "bytes": len(payload)}
        if actual != expected:
            raise ValueError(f"Source hash or size changed for {filename}; unverified data was not accepted")
        if missing:
            atomic_write(path, payload)
        fingerprints[filename] = actual
    return fingerprints


def normalize(text):
    return " ".join(unicodedata.normalize("NFC", text).split())


def tokenize(text):
    """Preserve combining marks and negation; delimit punctuation without ASCII-only regexes."""
    text = unicodedata.normalize("NFC", text).replace("’", "'")
    chars = []
    for char in text:
        category = unicodedata.category(char)
        chars.append(char if category[0] in "LMN" or char == "'" or char in "\u200c\u200d" else " ")
    return [word for token in "".join(chars).split() if (word := token.strip("'\u200c\u200d"))
            and any(unicodedata.category(c)[0] in "LN" for c in word)]


def load_records():
    records = {"en": [], "hi": []}
    with tarfile.open(ROOT / "data/raw/cornell_polarity_v2.tar.gz") as archive:
        for member in sorted(archive.getmembers(), key=lambda item: item.name):
            parts = Path(member.name).parts
            if member.isfile() and member.name.endswith(".txt") and "txt_sentoken" in parts:
                label = {"pos": "positive", "neg": "negative"}[parts[-2]]
                records["en"].append({"id": member.name, "split": "source_cv_tag",
                                      "label": label, "text": archive.extractfile(member).read().decode("utf-8")})
    with zipfile.ZipFile(ROOT / "data/raw/iitp_hindi_kaggle.zip") as archive:
        for split in ("train", "valid", "test"):
            name = f"iitp-movie-reviews/hi/hi-{split}.csv"
            for line, row in enumerate(csv.reader(io.StringIO(archive.read(name).decode("utf-8-sig"))), 1):
                if len(row) != 2 or row[0] not in {"positive", "negative", "neutral"}:
                    raise ValueError(f"Unexpected source schema at {name}:{line}")
                records["hi"].append({"id": f"{name}:{line}", "split": split,
                                      "label": row[0], "text": row[1]})
    return records


def near_pairs(records):
    """Exact Jaccard >= .90 join via globally ordered prefixes, for >=20-token texts.

    Prefix length n-ceil(.9*n)+1 guarantees candidate coverage for the specified
    set similarity. Five-token shingles are compared, not edit distance.
    """
    sets = []
    for record in records:
        words = tokenize(record["text"].casefold())
        sets.append({tuple(words[i:i+5]) for i in range(len(words)-4)} if len(words) >= 20 else set())
    freq = collections.Counter(shingle for shingles in sets for shingle in shingles)
    index = collections.defaultdict(list)
    pairs = []
    for i, shingles in enumerate(sets):
        if not shingles:
            continue
        ordered = sorted(shingles, key=lambda shingle: (freq[shingle], shingle))
        prefix = ordered[:len(shingles)-math.ceil(THRESHOLD*len(shingles))+1]
        candidates = {j for shingle in prefix for j in index[shingle]}
        for j in sorted(candidates):
            other = sets[j]
            if min(len(shingles), len(other)) / max(len(shingles), len(other)) < THRESHOLD:
                continue
            overlap = len(shingles & other)
            similarity = overlap / (len(shingles) + len(other) - overlap)
            if similarity >= THRESHOLD:
                pairs.append((j, i, round(similarity, 6)))
        for shingle in prefix:
            index[shingle].append(i)
    return pairs


def clean(records):
    dropped = []
    exact = collections.defaultdict(list)
    for record in records:
        record = dict(record, text=normalize(record["text"]))
        if record["label"] not in {"positive", "negative"}:
            dropped.append({"id": record["id"], "reason": "nonbinary_label"})
        elif not tokenize(record["text"]):
            dropped.append({"id": record["id"], "reason": "empty_or_no_word_tokens"})
        else:
            exact[" ".join(tokenize(record["text"])).casefold()].append(record)
    # Keep conflicting exact groups in the similarity graph. Removing them first
    # would let an almost identical, ambiguously labelled neighbor survive.
    exact_groups = list(exact.values())
    unique = [group[0] for group in exact_groups]
    pairs = near_pairs(unique)
    parent = list(range(len(unique)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for left, right, _ in pairs:
        parent[find(right)] = find(left)
    groups = collections.defaultdict(list)
    for i in range(len(unique)):
        groups[find(i)].append(i)
    result = []
    for indices in groups.values():
        conflict = len({record["label"] for i in indices for record in exact_groups[i]}) > 1
        if not conflict:
            result.append(unique[indices[0]])
        for i in indices:
            for offset, record in enumerate(exact_groups[i]):
                if conflict:
                    reason = "exact_conflicting_labels" if len(indices) == 1 else "near_conflicting_labels"
                elif i == indices[0] and offset == 0:
                    continue
                else:
                    reason = "exact_duplicate" if offset else "near_duplicate"
                dropped.append({"id": record["id"], "reason": reason})
    return result, dropped, [{"left": unique[a]["id"], "right": unique[b]["id"], "jaccard": score}
                             for a, b, score in pairs]


def arff_quote(text):
    return "'" + text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r") + "'"


def write_outputs(language, records):
    target = ROOT / "data/processed"
    # Finish serialization before publishing any file, and replace each file
    # atomically so an interrupted write cannot truncate a previous export.
    with tempfile.TemporaryDirectory(dir=target) as temporary:
        staging = Path(temporary)
        _write_outputs(staging, language, records)
        for path in staging.iterdir():
            os.replace(path, target / path.name)


def _write_outputs(target, language, records):
    with (target / f"{language}_reviews.arff").open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(f"@relation cinemood_{language}\n\n@attribute review string\n@attribute sentiment {{negative,positive}}\n\n@data\n")
        for record in records:
            stream.write(f"{arff_quote(' '.join(tokenize(record['text'])))},{record['label']}\n")
    with (target / f"{language}_reviews.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["review", "sentiment"])
        writer.writerows((" ".join(tokenize(r["text"])), r["label"]) for r in records)
    # Sidecar is for traceability only. Never load it as classifier attributes.
    with (target / f"{language}_metadata.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["row_1based", "source_id", "source_split", "review_language", "text_sha256"])
        writer.writerows((i, r["id"], r["split"], language, digest(r["text"].encode())) for i, r in enumerate(records, 1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Download missing source archives for research use")
    args = parser.parse_args()
    for folder in ("data/raw", "data/processed", "reports"):
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    try:
        fingerprints = acquire_sources(ROOT, args.download)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    summary = {"sources": fingerprints, "languages": {}, "near_duplicate_threshold": THRESHOLD}
    audit = {}
    prepared = {}
    for language, records in load_records().items():
        cleaned, dropped, pairs = clean(records)
        counts = collections.Counter(r["label"] for r in cleaned)
        if min(counts.get(label, 0) for label in ("negative", "positive")) < 10:
            raise ValueError(f"Insufficient class support for 10 folds: {language}")
        prepared[language] = cleaned
        lengths = sorted(len(tokenize(r["text"])) for r in cleaned)
        summary["languages"][language] = {
            "raw_records": len(records), "raw_labels": dict(collections.Counter(r["label"] for r in records)),
            "source_splits": dict(collections.Counter(r["split"] for r in records)),
            "clean_records": len(cleaned), "clean_labels": dict(counts),
            "dropped_by_reason": dict(collections.Counter(r["reason"] for r in dropped)),
            "near_duplicate_pairs_found": len(pairs),
            "tokens_min_median_max": [lengths[0], lengths[len(lengths)//2], lengths[-1]],
            "ten_fold_class_support": True,
        }
        audit[language] = {"dropped": dropped, "near_duplicate_pairs": pairs}
    # Validate every language before overwriting any existing exports.
    for language, cleaned in prepared.items():
        write_outputs(language, cleaned)
        summary["languages"][language]["arff_sha256"] = digest((ROOT / f"data/processed/{language}_reviews.arff").read_bytes())
    atomic_write(ROOT / "reports/data_summary.json", (json.dumps(summary, indent=2) + "\n").encode("utf-8"))
    atomic_write(ROOT / "reports/local_audit.json", (json.dumps(audit, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(summary["languages"], indent=2))


if __name__ == "__main__":
    main()

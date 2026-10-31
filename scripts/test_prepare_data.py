"""Regression checks for data loss, label conflicts and duplicate leakage."""
import itertools
import csv
import io
import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch
import prepare_data
from prepare_data import SOURCES, acquire_sources, clean, digest, near_pairs, normalize, tokenize, write_outputs


def record(text, label="positive", source="test"):
    return {"id": source, "text": text, "label": label, "split": "test"}


class PreparationTests(unittest.TestCase):
    def test_scripts_and_negation(self):
        self.assertEqual(tokenize("यह फ़िल्म अच्छी नहीं है।"), ["यह", "फ़िल्म", "अच्छी", "नहीं", "है"])
        self.assertEqual(tokenize("I don’t like it! Not good."), ["I", "don't", "like", "it", "Not", "good"])
        self.assertEqual(tokenize("తెలుగు సినిమా బాగుంది! தமிழ் படம் நன்று।"),
                         ["తెలుగు", "సినిమా", "బాగుంది", "தமிழ்", "படம்", "நன்று"])

    def test_exact_conflicts_excluded_not_arbitrarily_relabelled(self):
        kept, dropped, _ = clean([record("Good film", source="a"), record("Good  film", "negative", "b"),
                                  record("fine movie", source="c"), record("fine movie", source="d"),
                                  record("neutral review", "neutral", "e"), record("!!!", source="f")])
        self.assertEqual([r["id"] for r in kept], ["c"])
        self.assertEqual(len(dropped), 5)

    def test_punctuation_variants_cannot_leak_as_duplicate_inputs(self):
        kept, dropped, _ = clean([record("Good film!", source="a"), record("good film.", source="b")])
        self.assertEqual([r["id"] for r in kept], ["a"])
        self.assertEqual(dropped, [{"id": "b", "reason": "exact_duplicate"}])

    def test_prefix_join_matches_brute_force(self):
        rng = random.Random(42)
        base = [f"word{i}" for i in range(140)]
        texts = []
        for _ in range(25):
            words = base.copy()
            for index in rng.sample(range(len(words)), rng.randrange(0, 9)):
                words[index] = "replacement"
            texts.append(" ".join(words))
        rows = [record(text, source=str(i)) for i, text in enumerate(texts)]
        sets = [{tuple(text.split()[k:k+5]) for k in range(len(text.split())-4)} for text in texts]
        expected = {(a, b) for a, b in itertools.combinations(range(len(rows)), 2)
                    if len(sets[a] & sets[b]) / len(sets[a] | sets[b]) >= .9}
        self.assertTrue(expected)
        self.assertEqual({(a, b) for a, b, _ in near_pairs(rows)}, expected)

    def test_near_duplicate_label_conflict_and_idempotence(self):
        text = " ".join(f"token{i}" for i in range(100))
        rows = [record(text, source="a"), record(text + " ending", "negative", "b")]
        kept, dropped, _ = clean(rows)
        self.assertEqual(kept, [])
        self.assertTrue(all(r["reason"] == "near_conflicting_labels" for r in dropped))
        self.assertEqual(normalize(normalize(" good\n film ")), "good film")

    def test_exact_conflict_propagates_to_near_duplicate_neighbors(self):
        text = " ".join(f"token{i}" for i in range(100))
        rows = [record(text, source="a"), record(text, "negative", "b"),
                record(text + " ending", source="c")]
        kept, dropped, pairs = clean(rows)
        self.assertEqual(kept, [])
        self.assertEqual({r["id"] for r in dropped}, {"a", "b", "c"})
        self.assertTrue(pairs)

    def test_export_preserves_text_labels_and_source_alignment(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "data/processed"
            target.mkdir(parents=True)
            rows = [record("I don’t like it!", "negative", "a"), record("फ़िल्म अच्छी है।", source="b")]
            with patch.object(prepare_data, "ROOT", root):
                write_outputs("hi", rows)
            with (target / "hi_reviews.csv").open(encoding="utf-8") as stream:
                data = list(csv.DictReader(stream))
            self.assertEqual(data, [{"review": "I don't like it", "sentiment": "negative"},
                                    {"review": "फ़िल्म अच्छी है", "sentiment": "positive"}])
            with (target / "hi_metadata.csv").open(encoding="utf-8") as stream:
                metadata = list(csv.DictReader(stream))
            self.assertEqual([r["source_id"] for r in metadata], ["a", "b"])
            self.assertEqual([r["row_1based"] for r in metadata], ["1", "2"])
            self.assertEqual(metadata[0]["text_sha256"], digest(rows[0]["text"].encode("utf-8")))
            arff = (target / "hi_reviews.arff").read_text(encoding="utf-8")
            self.assertIn("'I don\\'t like it',negative", arff)

    def test_serialization_failure_preserves_existing_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "data/processed"
            target.mkdir(parents=True)
            existing = target / "en_reviews.arff"
            existing.write_text("previous export", encoding="utf-8")

            def fail(staging, *args):
                (staging / "en_reviews.arff").write_text("partial export", encoding="utf-8")
                raise OSError("simulated serialization failure")

            with patch.object(prepare_data, "ROOT", root), patch.object(prepare_data, "_write_outputs", side_effect=fail):
                with self.assertRaises(OSError):
                    write_outputs("en", [])
            self.assertEqual(existing.read_text(encoding="utf-8"), "previous export")
            self.assertEqual(list(target.iterdir()), [existing])

    def test_later_language_failure_does_not_replace_earlier_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "data/processed"
            target.mkdir(parents=True)
            existing = target / "en_reviews.arff"
            existing.write_text("previous export", encoding="utf-8")
            rows = {"en": [record(f"review {i} {label}", label, str(i))
                           for label in ("positive", "negative") for i in range(10)],
                    "hi": [record("बहुत अच्छी फ़िल्म")]}
            with (patch.object(prepare_data, "ROOT", root), patch("sys.argv", ["prepare_data.py"]),
                  patch.object(prepare_data, "acquire_sources", return_value={}),
                  patch.object(prepare_data, "load_records", return_value=rows)):
                with self.assertRaisesRegex(ValueError, "Insufficient class support"):
                    prepare_data.main()
            self.assertEqual(existing.read_text(encoding="utf-8"), "previous export")


class AcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "data/raw").mkdir(parents=True)
        self.payload = b"test archive contents"
        self.lock = {name: {"url": url, "sha256": digest(self.payload), "bytes": len(self.payload)}
                     for name, url in SOURCES.items()}
        self.save_lock()

    def save_lock(self):
        (self.root / "data/source_lock.json").write_text(json.dumps(self.lock), encoding="utf-8")

    def test_missing_or_incomplete_lock_never_trusts_downloads(self):
        with patch("prepare_data.urllib.request.urlopen") as fetch:
            self.lock.pop(next(iter(SOURCES)))
            self.save_lock()
            with self.assertRaisesRegex(ValueError, "exactly"):
                acquire_sources(self.root, download=True)
            (self.root / "data/source_lock.json").unlink()
            with self.assertRaisesRegex(ValueError, "Missing data/source_lock"):
                acquire_sources(self.root, download=True)
            fetch.assert_not_called()

    def test_bad_response_is_not_cached(self):
        with patch("prepare_data.urllib.request.urlopen", return_value=io.BytesIO(b"<html>login</html>")):
            with self.assertRaisesRegex(ValueError, "hash or size changed"):
                acquire_sources(self.root, download=True)
        self.assertEqual(list((self.root / "data/raw").iterdir()), [])

    def test_verified_downloads_are_reusable_offline(self):
        with patch("prepare_data.urllib.request.urlopen", side_effect=lambda *a, **kw: io.BytesIO(self.payload)) as fetch:
            self.assertEqual(acquire_sources(self.root, download=True), self.lock)
            self.assertEqual(fetch.call_count, len(SOURCES))
        with patch("prepare_data.urllib.request.urlopen") as fetch:
            self.assertEqual(acquire_sources(self.root), self.lock)
            fetch.assert_not_called()

    def test_corrupt_cached_archive_is_rejected(self):
        name = next(iter(SOURCES))
        (self.root / "data/raw" / name).write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError, "hash or size changed"):
            acquire_sources(self.root)


if __name__ == "__main__":
    unittest.main()

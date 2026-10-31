# Dataset source register

Sources checked and archives acquired on 2026-10-31. Raw and derived review text stays local and is excluded from Git. The repository provides acquisition code, file hashes, aggregate statistics, and reproduction instructions rather than redistributing the corpora.

## Selected datasets

| Item | English | Hindi |
| --- | --- | --- |
| Dataset used | Cornell sentiment polarity dataset v2.0, June 2004 | Kaggle mirror named IIT Patna Movie Reviews Hindi |
| Primary source | [Pang and Lee's distribution page](https://www.cs.cornell.edu/people/pabo/movie-review-data/) | [IIT Patna research resources](https://www.iitp.ac.in/~ai-nlp-ml/resources.html) |
| Actual download | [review_polarity.tar.gz](https://www.cs.cornell.edu/people/pabo/movie-review-data/review_polarity.tar.gz) | [Kaggle mirror by warcoder](https://www.kaggle.com/datasets/warcoder/iit-patna-movie-reviews-hindi), using its public download endpoint |
| Input format | One UTF-8-decodable text file per review in `pos` and `neg` directories | Headerless UTF-8 CSV: label, review; separate train, valid, and test files |
| Observed records | 2,000 | 3,100 |
| Observed source labels | 1,000 positive; 1,000 negative | 1,285 positive; 948 negative; 867 neutral |
| Unit | Processed review documents | Mixed short passages and long reviews; not uniformly complete reviews |
| Label mapping | `pos` → `positive`; `neg` → `negative` | Preserve `positive` and `negative`; exclude `neutral` |
| Use terms | Source distributes this version for sentiment experiments and requests citation of the dataset version. No explicit general redistribution license was found in the archive README. | IIT Patna states research use with citation. The mirror does not establish broader rights; use locally for this college research project. |
| Attribution | Bo Pang and Lillian Lee, *A Sentimental Education: Sentiment Analysis Using Subjectivity Summarization Based on Minimum Cuts*, ACL 2004. [Paper](https://www.cs.cornell.edu/people/pabo/html-mincuts.html) | Md Shad Akhtar, Ayush Kumar, Asif Ekbal, Pushpak Bhattacharyya, *A Hybrid Deep Learning Architecture for Sentiment Analysis*, COLING 2016, pp. 482–493. [Paper](https://aclanthology.org/C16-1047/) |

The Hindi mirror README attributes the data to IIT Patna, but its 3,100 three-class records differ from the original paper's MovieH table: 2,152 four-class records. Its exact transformation history is not supplied. Cite the original work **and** identify the actual mirror and hashes; do not describe these files as a verified copy of the paper's experiment. The original source currently offers a dataset request form. The script does not submit that form.

The English archive README says labels were obtained through automatic rating extraction and notes possible residual rating expressions. These are source labels, not fresh human annotations by the CineMood team.

Exact archive sizes, URLs, and SHA-256 hashes are recorded in [source_lock.json](../data/source_lock.json). The downloader rejects archives whose contents no longer match those hashes.

## Coverage beyond English cinema

The Hindi records contain discussion of Indian films, including `चेन्नई एक्सप्रेस` (Chennai Express) and `क्वीन` (Queen). These references are evidence of coverage beyond English cinema; they are not a complete title inventory. [Zee's broadcaster description](https://www.zee.com/in-the-news/zee-cinema-red-chillies-celebrate-3-years-of-chennai-express-on-7th-august-at-9-pm/) places Chennai Express in Hindi cinema, and [Apple's Queen listing](https://tv.apple.com/gb/movie/queen/umc.cmc.6llfe33ltrg6mczd2u7k5eakd) lists Hindi audio.

For source-level traceability, retained Hindi record `hi-train.csv:1606` mentions Chennai Express, and `hi-train.csv:2045` discusses Queen's protagonist Rani, played by Kangana Ranaut. Row numbers are logical CSV record numbers, not physical text lines. The metadata sidecar links these IDs to exported rows.

Neither selected input supplies a consistent movie-language field. Do not infer that every Hindi-language review concerns a Hindi-language movie. Full per-movie or per-industry coverage cannot be measured from the available metadata. Telugu, Tamil, Malayalam, and Kannada cinema remain eligible for future data collection, but are not claimed as independently verified coverage in this delivery.

## Other sources considered

| Source | Decision |
| --- | --- |
| [AI4Bharat public classification bundle](https://github.com/AI4Bharat/indicnlp_corpus#publicly-available-classification-datasets) | Documents IIT Patna reviews and preserves original dataset licenses, but its linked Google Storage archive returned HTTP 403 during acquisition. The bundle was not used. |
| IIT Patna original request form | Keep as the preferred route for obtaining the original version if needed; no personal information was submitted and no request was sent. |

No synthetic or translated reviews were added to the training data.

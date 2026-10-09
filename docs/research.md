# Research and project selection

Research checked on 9 October 2026. This project addresses inspectable split
integrity in local workflows. It does not introduce a new deduplication algorithm.

Primary sources:

- [From Data Leak to Secret Misses](https://arxiv.org/abs/2601.22946) studies how duplicated code contexts affect secret-detector evaluation.
- [Soft Contamination Means Benchmarks Test Shallow Generalization](https://arxiv.org/abs/2602.12413) examines direct and semantic benchmark overlap; lexical-only checks cannot cover all of its contamination cases.
- [DataTrove](https://github.com/huggingface/datatrove) provides reusable processing and deduplication pipelines.
- [Data-Juicer](https://github.com/datajuicer/data-juicer) provides broader foundation-model data processing.
- [datasketch MinHash LSH](https://ekzhu.com/datasketch/lsh.html) documents approximate candidate retrieval and its recall tradeoffs.
- [Hugging Face dataset streaming](https://huggingface.co/docs/datasets/main/stream) documents bounded iteration and Hub loading.

Practitioner discussions:

- [Hacker News: Fast Semantic Text Deduplication](https://news.ycombinator.com/item?id=42674627).
- [Reddit: Fast Semantic Text Deduplication](https://www.reddit.com/r/MachineLearning/comments/1i0cd4n/p_fast_semantic_text_deduplication/).

These discussions are qualitative context, not evidence of adoption or measured
market demand. Existing tools already address overlap and split construction.
Holdout Ledger's design choice is to keep audit evidence, holdout-preserving
repair, full-source fingerprints, and revision-level gates in one small local
workbench. That focus is an engineering judgment rather than a novelty claim.

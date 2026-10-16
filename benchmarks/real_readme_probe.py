"""Pinned real-document text probe. NEVER requests participant-level data files.

Reads README pages from two public CC0 OpenNeuro repository commits. There are no
human-annotated true labels; report overlap counts ONLY, not precision/recall.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.request import urlopen

from holdout_ledger import AuditConfig, Record, audit

SOURCES = (
    (
        "ds004131",
        "693ce9a1caf909c19ddf1d497e3bce805e78db60",
        "https://github.com/OpenNeuroDatasets/ds004131/blob/"
        "693ce9a1caf909c19ddf1d497e3bce805e78db60/README",
    ),
    (
        "ds005752",
        "f6c800b5f9fb5990683c86d278cb3e944c93f8b0",
        "https://github.com/OpenNeuroDatasets/ds005752/blob/"
        "f6c800b5f9fb5990683c86d278cb3e944c93f8b0/README",
    ),
)


def extract_paragraphs(document: str, limit: int = 12) -> list[str]:
    candidates = [" ".join(part.split()) for part in re.split(r"\n\s*\n", document)]
    return [text for text in candidates if 100 <= len(text) <= 800 and not text.startswith("|")][
        :limit
    ]


def probe(fetcher, limit: int = 12) -> dict:
    rows: list[Record] = []
    receipts: list[dict] = []
    for index, (name, revision, source_link) in enumerate(SOURCES):
        text = fetcher(name, revision)
        if "Creative Commons Zero (CC0)" not in text:
            raise ValueError(f"{name}: upstream README does not contain expected CC0 statement")
        paragraphs = extract_paragraphs(text, limit)
        if len(paragraphs) < 2:
            raise ValueError(f"{name}: not enough qualifying source paragraphs")
        receipts.append(
            {
                "repository": f"OpenNeuroDatasets/{name}",
                "commit_sha": revision,
                "source_url": source_link,
                "license_statement": "Creative Commons Zero (CC0) v1.0 in README",
                "source_readme_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "paragraphs_audited": len(paragraphs),
            }
        )
        for j, paragraph in enumerate(paragraphs):
            rows.append(
                Record(
                    id=f"{name}-para-{j:02}",
                    text=paragraph,
                    split="train" if index == 0 else "test",
                    metadata={"source": name, "source_paragraph": j},
                )
            )
    report = audit(rows, AuditConfig(mode="exhaustive", include_text=False))
    return {
        "schema_version": 1,
        "experiment_type": "unlabeled real-source OpenNeuro README paragraph overlap probe",
        "sources": receipts,
        "total_paragraphs": len(rows),
        "dataset_sha256": report.dataset_sha256,
        "audit_sha256": report.report_sha256,
        "config": report.config.model_dump(),
        "cross_split_clusters": report.summary.cross_split_clusters,
        "cross_split_records": report.summary.cross_split_records,
        "reported_exact_edges": report.summary.exact_edges,
        "reported_lexical_near_edges": report.summary.near_edges,
        "candidates_verified": report.summary.candidates_verified,
        "interpretation": (
            "Real, public CC0 README text; split assignment by source repository "
            "is artificial. No participant-level files or private data are read. "
            "These two README documents describe related NIMH resources and are "
            "not independent external validation cases. Without independent "
            "human-labeled matches, all sensitivity, specificity and real-world "
            "false-positive/false-negative rates are UNKNOWN."
        ),
    }


def fetch_readme(name: str, revision: str) -> str:
    url = f"https://raw.githubusercontent.com/OpenNeuroDatasets/{name}/{revision}/README"
    with urlopen(url, timeout=30) as response:
        data = response.read(100_001)
        if len(data) > 100_000:
            raise ValueError("source README exceeds 100 kB")
    return data.decode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("real-readme-probe.json"))
    args = parser.parse_args()
    result = probe(fetch_readme)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

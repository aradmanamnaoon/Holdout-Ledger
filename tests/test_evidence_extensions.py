"""Evidence-scope tests for synthetic baselines and real-source README probe."""

import pytest

from benchmarks.baseline_comparison import (
    baseline_ids,
    compare_seed,
    summarize,
    wilson_interval,
)
from benchmarks.benchmark import corpus
from benchmarks.real_readme_probe import SOURCES, extract_paragraphs, probe


def test_baselines_have_expected_and_different_scopes() -> None:
    rows, positives, negatives = corpus(60, 3, 8, 42)
    found = baseline_ids(rows)
    assert found["normalized_exact"] <= positives
    assert found["declared_group"] <= positives
    assert found["normalized_exact"] | found["declared_group"] == found["exact_or_group"]
    assert not found["exact_or_group"] & negatives
    assert len(found["normalized_exact"]) == 3
    assert len(found["declared_group"]) == 3


def test_wilson_bounds_and_undefined_cases() -> None:
    assert wilson_interval(0, 0) is None
    assert wilson_interval(0, 10)[0] == 0
    assert wilson_interval(10, 10)[1] == 1
    assert 0 < wilson_interval(5, 10)[0] < wilson_interval(5, 10)[1] < 1


def test_same_input_comparator_smoke_and_uncertainty() -> None:
    run = compare_seed(48, 3, 8, 42)
    assert run["metrics"]["exhaustive_lexical_group"]["false_negatives"] == 0
    assert run["metrics"]["lsh_lexical_group"]["false_negatives"] == 0
    assert run["metrics"]["lsh_lexical_group"]["false_positives"] == 0
    assert run["lsh_near_edge_recall_vs_exhaustive"] == 1.0
    assert run["metrics"]["normalized_exact"]["true_positives"] == 3
    assert run["metrics"]["declared_group"]["true_positives"] == 3
    result = summarize([run])
    assert result["lsh_lexical_group"]["pooled_counts"]["true_negatives"] == 8
    assert result["normalized_exact"]["pooled_counts"]["false_negatives"] == 6


def test_extract_does_not_emit_empty_or_table_lines() -> None:
    content = (
        "# Heading\n\n"
        + "A valid independent neuroscience experiment summary with enough"
        + " characters and repeated context for a non-identifying text probe.\n\n"
        + "| a | b | " + "x" * 100 + "\n\n"
        + "A second independent section discusses acquisition standards for"
        + " research volunteers without listing respondent records.\n\n"
    )
    paragraphs = extract_paragraphs(content)
    assert len(paragraphs) == 2
    assert not any(text.startswith("|") for text in paragraphs)


def test_readme_probe_uses_only_pinned_readme_text_and_no_accuracy_claim() -> None:
    docs = {
        name: (
            "This dataset is licensed under the Creative Commons Zero (CC0) v1.0 License.\n\n"
            "Description of a cognitive experiment protocol and recording method "
            "in a public non-participant README paragraph.\n\n"
            "Detailed summary of neuroscience data collection procedures and "
            "cross-session analysis methods in a second README paragraph."
        )
        for name, _, _ in SOURCES
    }
    seen = []

    def fake_fetch(name: str, revision: str) -> str:
        seen.append((name, revision))
        return docs[name]

    result = probe(fake_fetch)
    assert len(seen) == len(SOURCES)
    assert all(len(revision) == 40 for _, revision in seen)
    assert result["total_paragraphs"] >= 4
    assert "precision" not in result
    assert "UNKNOWN" in result["interpretation"]
    assert all("source_readme_sha256" in row for row in result["sources"])


def test_readme_probe_fails_closed_without_license_evidence() -> None:
    def not_licensed(name: str, revision: str) -> str:
        return "Research description not licensed.\n\n" + "text " * 30

    with pytest.raises(ValueError, match="expected CC0"):
        probe(not_licensed)

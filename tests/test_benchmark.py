"""Synthetic benchmark oracle tests: positive, negative, determinism, and failure controls."""

import pytest

from benchmarks.benchmark import confusion, corpus, run_once
from holdout_ledger.text import jaccard, shingles


def test_generated_fixture_contains_positive_and_negative_holdouts() -> None:
    rows, positives, negatives = corpus(size=48, injected=3, negatives=8, seed=42)
    assert len(rows) == 48 + 9 + 8
    assert len(positives) == 9
    assert len(negatives) == 8
    assert not positives & negatives
    by_id = {row.id: row for row in rows}
    assert all(by_id[key].split == "test" for key in positives | negatives)
    assert sum(by_id[key].group_id is not None for key in positives) == 3
    assert len({by_id[key].id for key in positives | negatives}) == 17


def test_hard_negatives_are_below_lexical_threshold() -> None:
    size, injected, negatives = 48, 3, 8
    rows, _, _ = corpus(size, injected, negatives, 42)
    by_id = {row.id: row for row in rows}
    for i in range(negatives // 2):
        source = by_id[f"train-{3 * injected + i:06d}"]
        hard = by_id[f"test-negative-{i:06d}"]
        assert jaccard(shingles(source.text, 3), shingles(hard.text, 3)) < 0.8
        assert hard.group_id is None


def test_false_positive_and_false_negative_controls() -> None:
    _, positives, negatives = corpus(48, 3, 8, 42)
    perfect = confusion(positives, positives, negatives)
    assert perfect["true_positives"] == 9
    assert perfect["true_negatives"] == 8
    assert perfect["false_positive_rate"] == 0.0
    assert perfect["precision"] == 1.0

    label_every_test = confusion(positives | negatives, positives, negatives)
    assert label_every_test["false_positives"] == 8
    assert label_every_test["false_positive_rate"] == 1.0
    assert label_every_test["precision"] < 1.0

    label_no_test = confusion(set(), positives, negatives)
    assert label_no_test["false_negatives"] == 9
    assert label_no_test["recall"] == 0.0
    assert label_no_test["precision"] is None


def test_unlabeled_flagged_ids_are_rejected() -> None:
    with pytest.raises(ValueError, match="partition"):
        confusion({"unlabeled"}, {"positive"}, {"negative"})
    with pytest.raises(ValueError, match="partition"):
        confusion(set(), {"same"}, {"same"})


@pytest.mark.parametrize("mode", ["exhaustive", "lsh"])
def test_small_seeded_detector_smoke(mode: str) -> None:
    result = run_once(size=60, injected=3, negatives=8, seed=42, mode=mode)
    counts = result["counts_and_metrics"]
    assert counts["true_positives"] == 9
    assert counts["false_negatives"] == 0
    assert counts["false_positives"] == 0
    assert counts["true_negatives"] == 8
    assert counts["false_positive_rate"] == 0
    assert result["method"] == mode


def test_repeated_run_has_stable_input_and_report_hashes() -> None:
    first = run_once(48, 3, 8, seed=43, mode="exhaustive")
    repeat = run_once(48, 3, 8, seed=43, mode="exhaustive")
    changed_seed = run_once(48, 3, 8, seed=44, mode="exhaustive")
    assert first["dataset_sha256"] == repeat["dataset_sha256"]
    assert first["report_sha256"] == repeat["report_sha256"]
    assert first["dataset_sha256"] != changed_seed["dataset_sha256"]
    assert first["counts_and_metrics"] == repeat["counts_and_metrics"]


@pytest.mark.parametrize("args", [(8, 3, 8), (48, 0, 8), (48, 3, 0)])
def test_reject_bad_corpus_contract(args: tuple[int, int, int]) -> None:
    with pytest.raises(ValueError, match="require"):
        corpus(*args)

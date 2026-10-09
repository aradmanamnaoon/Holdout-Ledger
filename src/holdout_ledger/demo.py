"""Synthetic records designed to demonstrate independent failure classes."""

from .models import Record


def demo_records() -> list[Record]:
    """All examples are invented; none are medical records or scraped content."""
    payloads = [
        (
            "train-exact",
            "train",
            "The deployment guide says retry failed requests with a bounded budget.",
            "safe",
            None,
        ),
        (
            "test-exact",
            "test",
            "  THE DEPLOYMENT GUIDE SAYS RETRY FAILED REQUESTS WITH A BOUNDED BUDGET.  ",
            "safe",
            None,
        ),
        (
            "train-near",
            "train",
            "the model server validates every incoming request and records each latency "
            "measurement before returning the structured prediction to the client",
            "service",
            None,
        ),
        (
            "validation-near",
            "validation",
            "the model server validates every incoming request and records each latency "
            "measurement before returning the structured prediction to the caller",
            "service",
            None,
        ),
        ("train-group", "train", "A red kite circles above the trees.", "bird", "session-17"),
        ("test-group", "test", "A quiet lake reflects the evening sky.", "water", "session-17"),
        (
            "train-conflict",
            "train",
            "The review describes a disappointing product.",
            "positive",
            None,
        ),
        (
            "train-conflict-copy",
            "train",
            "the review describes a disappointing product.",
            "negative",
            None,
        ),
        ("train-fa", "train", "مدل برای پردازش داده های فارسی طراحی شده است", "nlp", None),
        ("test-fa", "test", "مدل برای پردازش داده های فارسی طراحی شده است", "nlp", None),
        (
            "train-clean",
            "train",
            "Database checkpoints allow recovery after a crash.",
            "storage",
            None,
        ),
        (
            "test-clean",
            "test",
            "Wind turbines convert moving air into electricity.",
            "energy",
            None,
        ),
        ("train-blank", "train", "   ", None, None),
        ("train-short", "train", "Hello", "greeting", None),
    ]
    return [
        Record.model_validate(dict(id=key, split=split, text=text, label=label, group_id=group))
        for key, split, text, label, group in payloads
    ]

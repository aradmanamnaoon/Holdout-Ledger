"""Strict, versioned contracts. IDs are globally unique across input splits."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

Split = Literal["train", "validation", "test"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class Record(Contract):
    """Text plus optional entity and label metadata; no patient data is required."""

    id: str = Field(min_length=1, max_length=200)
    text: str = Field(max_length=100_000)
    split: Split
    label: str | None = Field(default=None, max_length=200)
    group_id: str | None = Field(default=None, min_length=1, max_length=200)
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def meaningful_id(self) -> Self:
        if not self.id.strip():
            raise ValueError("record ID must not be whitespace")
        return self


class AuditConfig(Contract):
    """LSH finds candidates; exact Jaccard verifies each reported near match."""

    normalization: Literal["unicode", "persian"] = "unicode"
    threshold: float = Field(default=0.8, ge=0.3, le=1.0, allow_inf_nan=False)
    candidate_threshold: float = Field(default=0.5, gt=0, lt=1, allow_inf_nan=False)
    word_ngram: int = Field(default=3, ge=1, le=10)
    num_perm: int = Field(default=128, ge=32, le=512)
    seed: int = Field(default=42, ge=0, le=2**32 - 1)
    mode: Literal["auto", "exhaustive", "lsh"] = "auto"
    exhaustive_limit: int = Field(default=1000, ge=1, le=3000)
    max_records: int = Field(default=100_000, ge=1, le=1_000_000)
    max_edges: int = Field(default=200_000, ge=1, le=2_000_000)
    max_candidates: int = Field(default=2_000_000, ge=1, le=20_000_000)
    include_text: bool = False

    @model_validator(mode="after")
    def candidate_bound(self) -> Self:
        if self.candidate_threshold > self.threshold:
            raise ValueError("candidate_threshold must not exceed threshold")
        return self


class Edge(Contract):
    """A graph witness, not an exhaustive list of every equivalent pair."""

    left: str
    right: str
    kind: Literal["exact", "near", "group"]
    score: float | None
    cross_split: bool


class Member(Contract):
    id: str
    split: Split
    label: str | None
    text_preview: str | None = None


class Cluster(Contract):
    """Connected components can contain indirect matches through other records."""

    id: str
    members: list[Member]
    cross_split: bool
    reasons: list[str]


class Conflict(Contract):
    """Differing labels for normalized-exact text; entities can have multiple labels."""

    record_ids: list[str]
    labels: list[str]


class Summary(Contract):
    records: int
    split_counts: dict[str, int]
    clusters: int
    cross_split_clusters: int
    cross_split_records: int
    exposed_holdout_ids: list[str]
    exposed_holdout_fraction: float
    exact_edges: int
    near_edges: int
    group_edges: int
    label_conflicts: int
    blank_record_ids: list[str]
    short_record_ids: list[str]
    candidates_verified: int


class AuditReport(Contract):
    schema_version: Literal[1] = 1
    dataset_sha256: str
    report_sha256: str
    config: AuditConfig
    method: Literal["exhaustive", "lsh"]
    environment: dict[str, str]
    summary: Summary
    edges: list[Edge]
    clusters: list[Cluster]
    label_conflicts: list[Conflict]
    warnings: list[str]


class Removal(Contract):
    record_id: str
    cluster_id: str
    protected_split: Split
    reason: str


class RepairPlan(Contract):
    schema_version: Literal[1] = 1
    dataset_sha256: str
    report_sha256: str
    config: AuditConfig
    removals: list[Removal]
    original_records: int
    retained_records: int
    preserved_test_records: int
    protected_order: list[str] = Field(default_factory=lambda: ["test", "validation", "train"])
    warnings: list[str]


class GatePolicy(Contract):
    max_cross_split_records: int = Field(default=0, ge=0)
    max_label_conflicts: int = Field(default=0, ge=0)
    max_blank_records: int = Field(default=0, ge=0)


class GateResult(Contract):
    passed: bool
    violations: list[str]


class ReportDelta(Contract):
    baseline_sha256: str
    current_sha256: str
    new_exposed_holdout_ids: list[str]
    resolved_holdout_ids: list[str]
    record_delta: int
    cross_split_record_delta: int
    label_conflict_delta: int
    regression: bool

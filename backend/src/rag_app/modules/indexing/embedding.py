"""Framework-free embedding profiles, bounded batch plans, and vector validation.

This module is the domain seam between chunking/query construction and any
embedding provider adapter.  It uses only the Python standard library, opens
no network connection, performs no retries, and never puts input text,
endpoints, or credentials into an error message.

An :class:`EmbeddingProfile` is immutable and must state its dimension,
tokenizer, preprocessing, normalization, purpose, and every per-item and
per-batch limit explicitly.  :func:`plan_embedding_batches` losslessly packs
exact caller inputs into deterministic batches.
:func:`validate_embedding_results` is the only accepted path for provider
vectors: it binds the response to the exact profile and plan, rejects malformed
ordinals and values, and applies the profile's L2 policy with a scale-safe
algorithm.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import hashlib
import json
import math
import re
from typing import Final, Literal, Protocol


EmbeddingPurpose = Literal["query", "document"]
EmbeddingNormalization = Literal["l2", "none"]

# Domain safety bounds, not provider assumptions.  A verified profile must
# still state its real dimension and limits; nothing here supplies a default.
MAX_DIMENSION: Final = 65_536
MAX_LIMIT: Final = 2_147_483_647
MAX_IDENTIFIER_CHARS: Final = 128
MAX_EVIDENCE_CHARS: Final = 512
MAX_PREFIX_BYTES: Final = 256
MAX_PLAN_ITEMS: Final = 1_000_000

_PURPOSES: Final = frozenset({"query", "document"})
_NORMALIZATIONS: Final = frozenset({"l2", "none"})
_IDENTIFIER_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/@+-]*\Z")
_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")

MESSAGES: Final[dict[str, str]] = {
    "EMBEDDING_PROFILE_INVALID": "The embedding profile is invalid.",
    "EMBEDDING_PROFILE_UNVERIFIED": "The embedding profile is not verified for dispatch.",
    "EMBEDDING_PURPOSE_MISMATCH": "The embedding purpose is invalid or does not match the profile.",
    "EMBEDDING_SPACE_MISMATCH": "Query and document profiles do not share one vector space.",
    "EMBEDDING_INPUT_INVALID": "The embedding input is invalid.",
    "EMBEDDING_ITEM_LIMIT_EXCEEDED": (
        "An embedding input exceeds a per-item token or byte limit."
    ),
    "EMBEDDING_COUNTER_INVALID": (
        "The embedding token counter is invalid or does not match the profile."
    ),
    "EMBEDDING_PLAN_INVALID": "The embedding batch plan is invalid or does not match the profile.",
    "EMBEDDING_RESULT_INVALID": "The embedding result is invalid.",
    "EMBEDDING_RESULT_COUNT_MISMATCH": (
        "The embedding result count does not match the request."
    ),
    "EMBEDDING_RESULT_ORDINAL_INVALID": (
        "Embedding result ordinals are missing, duplicated, or out of range."
    ),
    "EMBEDDING_RESULT_VALUE_INVALID": (
        "An embedding result value is not a finite number."
    ),
    "EMBEDDING_RESULT_DIMENSION_MISMATCH": (
        "An embedding result dimension does not match the profile."
    ),
    "EMBEDDING_RESULT_ZERO_VECTOR": "An embedding result is a zero vector.",
    "EMBEDDING_PROVIDER_INVALID": (
        "The embedding provider is invalid or does not match the batch plan."
    ),
}


class EmbeddingError(ValueError):
    """Finite domain failure; messages never contain input, endpoints, or secrets."""

    def __init__(self, code: str) -> None:
        if code not in MESSAGES:
            code = "EMBEDDING_INPUT_INVALID"
        self.code = code
        super().__init__(f"{code}: {MESSAGES[code]}")


def _valid_identifier(value: object, max_chars: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) <= max_chars
        and _IDENTIFIER_RE.fullmatch(value) is not None
    )


def _valid_prefix(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return len(value.encode("utf-8")) <= MAX_PREFIX_BYTES
    except Exception:
        return False


def _valid_evidence_ref(value: object) -> bool:
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_EVIDENCE_CHARS:
        return False
    return all(
        ord(character) >= 0x20 and ord(character) != 0x7F for character in value
    )


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None


def _fingerprint(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, kw_only=True)
class EmbeddingLimits:
    """Explicit finite limits; there is no default or inferred upper bound.

    Per-batch limits must be at least their per-item counterparts.  Otherwise
    no non-empty item could ever fit, and the profile would be unusable.
    A missing field stays ``None`` so profile construction fails with a finite
    domain error instead of inventing a limit.
    """

    max_tokens_per_item: int | None = None
    max_tokens_per_batch: int | None = None
    max_utf8_bytes_per_item: int | None = None
    max_utf8_bytes_per_batch: int | None = None
    max_items_per_batch: int | None = None

    def __post_init__(self) -> None:
        values = (
            self.max_tokens_per_item,
            self.max_tokens_per_batch,
            self.max_utf8_bytes_per_item,
            self.max_utf8_bytes_per_batch,
            self.max_items_per_batch,
        )
        if any(
            type(value) is not int or not 1 <= value <= MAX_LIMIT
            for value in values
        ):
            raise EmbeddingError("EMBEDDING_PROFILE_INVALID")
        if self.max_tokens_per_batch < self.max_tokens_per_item:
            raise EmbeddingError("EMBEDDING_PROFILE_INVALID")
        if self.max_utf8_bytes_per_batch < self.max_utf8_bytes_per_item:
            raise EmbeddingError("EMBEDDING_PROFILE_INVALID")


@dataclass(frozen=True, kw_only=True)
class EmbeddingProfile:
    """Immutable, explicitly verified embedding configuration.

    ``space_fingerprint`` is the cross-purpose vector-space key.  Query and
    document profiles may use different purposes and input prefixes while
    sharing it.  ``compatibility_fingerprint`` adds the purpose and exact
    input prefix, which is the key for "same embedding configuration".
    ``fingerprint`` adds the profile id, limits, and verification binding, so a
    plan can never be replayed against a different immutable profile.

    ``input_prefix`` is the only purpose-specific text transform applied by
    this module.  ``preprocessing`` is an opaque version identifier for any
    caller-side preprocessing that must happen before planning; this module
    never silently trims, normalizes, truncates, or otherwise changes text.
    """

    profile_id: str
    provider: str
    model: str
    # A deployment id or an immutable model revision/version string.  It must
    # change whenever the served model behind the same name can change.
    deployment: str
    dimension: int
    tokenizer: str
    preprocessing: str
    normalization: EmbeddingNormalization
    purpose: EmbeddingPurpose
    input_prefix: str
    limits: EmbeddingLimits
    verified: bool
    evidence_ref: str | None

    def __post_init__(self) -> None:
        if not _valid_identifier(self.profile_id, MAX_IDENTIFIER_CHARS):
            raise EmbeddingError("EMBEDDING_PROFILE_INVALID")
        for identifier in (
            self.provider,
            self.model,
            self.deployment,
            self.tokenizer,
            self.preprocessing,
        ):
            if not _valid_identifier(identifier, MAX_IDENTIFIER_CHARS):
                raise EmbeddingError("EMBEDDING_PROFILE_INVALID")
        if (
            type(self.dimension) is not int
            or not 1 <= self.dimension <= MAX_DIMENSION
        ):
            raise EmbeddingError("EMBEDDING_PROFILE_INVALID")
        if (
            not isinstance(self.normalization, str)
            or self.normalization not in _NORMALIZATIONS
        ):
            raise EmbeddingError("EMBEDDING_PROFILE_INVALID")
        if not isinstance(self.purpose, str) or self.purpose not in _PURPOSES:
            raise EmbeddingError("EMBEDDING_PROFILE_INVALID")
        if not _valid_prefix(self.input_prefix):
            raise EmbeddingError("EMBEDDING_PROFILE_INVALID")
        if not isinstance(self.limits, EmbeddingLimits):
            raise EmbeddingError("EMBEDDING_PROFILE_INVALID")
        if type(self.verified) is not bool:
            raise EmbeddingError("EMBEDDING_PROFILE_INVALID")
        if self.evidence_ref is not None and not _valid_evidence_ref(self.evidence_ref):
            raise EmbeddingError("EMBEDDING_PROFILE_INVALID")
        if self.verified and self.evidence_ref is None:
            raise EmbeddingError("EMBEDDING_PROFILE_INVALID")

    @property
    def space_fingerprint(self) -> str:
        """Vector-space identity shared by compatible query/document profiles."""

        return _fingerprint(
            {
                "schema": "rag-embedding-space.v1",
                "provider": self.provider,
                "model": self.model,
                "deployment": self.deployment,
                "dimension": self.dimension,
                "tokenizer_fingerprint": self.tokenizer_fingerprint,
                "preprocessing_fingerprint": self.preprocessing_fingerprint,
                "normalization_fingerprint": self.normalization_fingerprint,
                "count_basis": {"tokens": "tokenizer", "bytes": "utf8"},
            }
        )

    @property
    def tokenizer_fingerprint(self) -> str:
        """Exact tokenizer/count-basis identity, independent of the model name."""

        return _fingerprint(
            {"schema": "rag-embedding-tokenizer.v1", "tokenizer": self.tokenizer}
        )

    @property
    def preprocessing_fingerprint(self) -> str:
        """Exact preprocessing version identity; never inferred from the model."""

        return _fingerprint(
            {
                "schema": "rag-embedding-preprocessing.v1",
                "preprocessing": self.preprocessing,
            }
        )

    @property
    def normalization_fingerprint(self) -> str:
        """Exact output normalization identity."""

        return _fingerprint(
            {
                "schema": "rag-embedding-normalization.v1",
                "normalization": self.normalization,
            }
        )

    @property
    def compatibility_fingerprint(self) -> str:
        """Purpose-bound configuration identity, including the exact prefix."""

        return _fingerprint(
            {
                "schema": "rag-embedding-compatibility.v1",
                "space_fingerprint": self.space_fingerprint,
                "purpose": self.purpose,
                "input_prefix": self.input_prefix,
            }
        )

    @property
    def fingerprint(self) -> str:
        """Full immutable profile identity used to bind a batch plan."""

        return _fingerprint(
            {
                "schema": "rag-embedding-profile.v1",
                "compatibility_fingerprint": self.compatibility_fingerprint,
                "profile_id": self.profile_id,
                "limits": {
                    "max_tokens_per_item": self.limits.max_tokens_per_item,
                    "max_tokens_per_batch": self.limits.max_tokens_per_batch,
                    "max_utf8_bytes_per_item": self.limits.max_utf8_bytes_per_item,
                    "max_utf8_bytes_per_batch": self.limits.max_utf8_bytes_per_batch,
                    "max_items_per_batch": self.limits.max_items_per_batch,
                },
                "verified": self.verified,
                "evidence_ref": self.evidence_ref,
            }
        )


@dataclass(frozen=True)
class EmbeddingPlanItem:
    """One exact input and its stable global ordinal in the plan."""

    ordinal: int
    text: str
    provider_text: str
    token_count: int
    utf8_bytes: int

    def __post_init__(self) -> None:
        if type(self.ordinal) is not int or self.ordinal < 0:
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        if not isinstance(self.text, str) or not self.text:
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        if not isinstance(self.provider_text, str) or not self.provider_text:
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        if not self.provider_text.endswith(self.text):
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        try:
            encoded = self.provider_text.encode("utf-8")
        except Exception:
            encoded = None
        if encoded is None:
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        if (
            type(self.utf8_bytes) is not int
            or not 0 <= self.utf8_bytes <= MAX_LIMIT
            or self.utf8_bytes != len(encoded)
        ):
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        if type(self.token_count) is not int or self.token_count < 0:
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")


@dataclass(frozen=True)
class EmbeddingPlanBatch:
    """One non-empty, ordered partition of plan items."""

    index: int
    items: tuple[EmbeddingPlanItem, ...]
    token_count: int
    utf8_bytes: int

    def __post_init__(self) -> None:
        if type(self.index) is not int or self.index < 0:
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        if not isinstance(self.items, tuple) or not self.items:
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        previous = -1
        token_sum = 0
        byte_sum = 0
        for item in self.items:
            if not isinstance(item, EmbeddingPlanItem):
                raise EmbeddingError("EMBEDDING_PLAN_INVALID")
            if item.ordinal <= previous:
                raise EmbeddingError("EMBEDDING_PLAN_INVALID")
            previous = item.ordinal
            token_sum += item.token_count
            byte_sum += item.utf8_bytes
        if type(self.token_count) is not int or self.token_count != token_sum:
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        if type(self.utf8_bytes) is not int or self.utf8_bytes != byte_sum:
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")

    @property
    def ordinals(self) -> tuple[int, ...]:
        return tuple(item.ordinal for item in self.items)


@dataclass(frozen=True)
class EmbeddingBatchPlan:
    """A lossless, deterministic packing of exact inputs.

    ``items`` is the authoritative ordered input; ``batches`` is a view that
    partitions it in order.  A batch item's ordinal is global to the plan, not
    local to the batch.  Provider adapters must echo that ordinal in each
    result.  This plan performs no network I/O and has no retry behavior.
    """

    profile_id: str
    profile_fingerprint: str
    compatibility_fingerprint: str
    space_fingerprint: str
    purpose: EmbeddingPurpose
    dimension: int
    normalization: EmbeddingNormalization
    input_prefix: str
    limits: EmbeddingLimits
    items: tuple[EmbeddingPlanItem, ...]
    batches: tuple[EmbeddingPlanBatch, ...]

    def __post_init__(self) -> None:
        if not _valid_identifier(self.profile_id, MAX_IDENTIFIER_CHARS):
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        if not (
            _is_sha256(self.profile_fingerprint)
            and _is_sha256(self.compatibility_fingerprint)
            and _is_sha256(self.space_fingerprint)
        ):
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        if not isinstance(self.purpose, str) or self.purpose not in _PURPOSES:
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        if (
            type(self.dimension) is not int
            or not 1 <= self.dimension <= MAX_DIMENSION
        ):
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        if (
            not isinstance(self.normalization, str)
            or self.normalization not in _NORMALIZATIONS
        ):
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        if not _valid_prefix(self.input_prefix):
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        if not isinstance(self.limits, EmbeddingLimits):
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        if not isinstance(self.items, tuple) or not isinstance(self.batches, tuple):
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        for index, item in enumerate(self.items):
            if not isinstance(item, EmbeddingPlanItem) or item.ordinal != index:
                raise EmbeddingError("EMBEDDING_PLAN_INVALID")
            if item.provider_text != self.input_prefix + item.text:
                raise EmbeddingError("EMBEDDING_PLAN_INVALID")
            if item.token_count > self.limits.max_tokens_per_item:
                raise EmbeddingError("EMBEDDING_PLAN_INVALID")
            if item.utf8_bytes > self.limits.max_utf8_bytes_per_item:
                raise EmbeddingError("EMBEDDING_PLAN_INVALID")
        flattened: list[EmbeddingPlanItem] = []
        for index, batch in enumerate(self.batches):
            if not isinstance(batch, EmbeddingPlanBatch) or batch.index != index:
                raise EmbeddingError("EMBEDDING_PLAN_INVALID")
            if len(batch.items) > self.limits.max_items_per_batch:
                raise EmbeddingError("EMBEDDING_PLAN_INVALID")
            if batch.token_count > self.limits.max_tokens_per_batch:
                raise EmbeddingError("EMBEDDING_PLAN_INVALID")
            if batch.utf8_bytes > self.limits.max_utf8_bytes_per_batch:
                raise EmbeddingError("EMBEDDING_PLAN_INVALID")
            flattened.extend(batch.items)
        if tuple(flattened) != self.items:
            raise EmbeddingError("EMBEDDING_PLAN_INVALID")

    @property
    def item_count(self) -> int:
        return len(self.items)

    @property
    def ordinals(self) -> tuple[int, ...]:
        return tuple(item.ordinal for item in self.items)


class TokenCounter(Protocol):
    """Deterministic local token-count port bound to one tokenizer identity.

    Implementations must count with the exact provider tokenizer named by the
    profile.  Character counts or approximate tokenizers must not be presented
    as provider tokens.  The port must be local and deterministic: it performs
    no network I/O, no retry, and no hidden input mutation.
    """

    @property
    def tokenizer(self) -> str:
        ...

    def count_tokens(self, text: str) -> int:
        ...


@dataclass(frozen=True)
class EmbeddingResult:
    """Provider-supplied result record; the domain core validates every field."""

    ordinal: int
    vector: tuple[float, ...] | list[float]


class EmbeddingProvider(Protocol):
    """Supervised embedding adapter seam.

    Implementations are adapters behind the existing call/egress supervision
    and the shared execution gate.  This module never calls the network and
    provides no free-form HTTP client.  ``embed_batch`` must use the exact
    immutable profile exposed by ``profile`` and must echo each plan item's
    global ordinal in the returned records.
    """

    @property
    def profile(self) -> EmbeddingProfile:
        ...

    def embed_batch(
        self, batch: EmbeddingPlanBatch
    ) -> Sequence[EmbeddingResult]:
        ...


def plan_embedding_batches(
    *,
    profile: EmbeddingProfile,
    purpose: EmbeddingPurpose,
    texts: Sequence[str],
    counter: TokenCounter,
) -> EmbeddingBatchPlan:
    """Packs exact inputs into deterministic batches.

    The caller must state the purpose explicitly; it must equal the profile's
    purpose.  Every input is retained verbatim in ``EmbeddingPlanItem.text``;
    ``provider_text`` is exactly ``profile.input_prefix + text``.  Token and
    UTF-8 byte limits are checked per item and per batch, and ``MAX_PLAN_ITEMS``
    bounds the total count.  No input is trimmed, truncated, or silently
    discarded.  An unverified profile cannot produce a plan.
    """

    if not isinstance(profile, EmbeddingProfile):
        raise EmbeddingError("EMBEDDING_PROFILE_INVALID")
    if not profile.verified:
        raise EmbeddingError("EMBEDDING_PROFILE_UNVERIFIED")
    if (
        not isinstance(purpose, str)
        or purpose not in _PURPOSES
        or purpose != profile.purpose
    ):
        raise EmbeddingError("EMBEDDING_PURPOSE_MISMATCH")
    if not isinstance(texts, Sequence) or isinstance(
        texts, (str, bytes, bytearray)
    ):
        raise EmbeddingError("EMBEDDING_INPUT_INVALID")

    try:
        counter_tokenizer = counter.tokenizer
        count_tokens = counter.count_tokens
    except Exception:
        counter_tokenizer = None
        count_tokens = None
    if counter_tokenizer != profile.tokenizer or not callable(count_tokens):
        raise EmbeddingError("EMBEDDING_COUNTER_INVALID")

    try:
        raw_texts = tuple(texts)
    except Exception:
        raw_texts = None
    if not isinstance(raw_texts, tuple):
        raise EmbeddingError("EMBEDDING_INPUT_INVALID")
    if not raw_texts:
        raise EmbeddingError("EMBEDDING_INPUT_INVALID")
    if len(raw_texts) > MAX_PLAN_ITEMS:
        raise EmbeddingError("EMBEDDING_INPUT_INVALID")

    limits = profile.limits
    prepared: list[tuple[str, str, int]] = []
    for text in raw_texts:
        if not isinstance(text, str) or not text:
            raise EmbeddingError("EMBEDDING_INPUT_INVALID")
        try:
            provider_text = profile.input_prefix + text
            byte_count = len(provider_text.encode("utf-8"))
        except Exception:
            provider_text = ""
            byte_count = None
        if byte_count is None:
            raise EmbeddingError("EMBEDDING_INPUT_INVALID")
        # Per-item byte rejection happens before any token counting, so an
        # oversized input cannot drive work on the tokenizer port.
        if byte_count > limits.max_utf8_bytes_per_item:
            raise EmbeddingError("EMBEDDING_ITEM_LIMIT_EXCEEDED")
        prepared.append((text, provider_text, byte_count))

    items: list[EmbeddingPlanItem] = []
    for ordinal, (text, provider_text, utf8_bytes) in enumerate(prepared):
        try:
            token_count = count_tokens(provider_text)
        except Exception:
            token_count = None
        if type(token_count) is not int or token_count < 0:
            raise EmbeddingError("EMBEDDING_COUNTER_INVALID")
        if (
            token_count > limits.max_tokens_per_item
            or utf8_bytes > limits.max_utf8_bytes_per_item
        ):
            raise EmbeddingError("EMBEDDING_ITEM_LIMIT_EXCEEDED")
        items.append(
            EmbeddingPlanItem(
                ordinal=ordinal,
                text=text,
                provider_text=provider_text,
                token_count=token_count,
                utf8_bytes=utf8_bytes,
            )
        )

    batches: list[EmbeddingPlanBatch] = []
    current: list[EmbeddingPlanItem] = []
    current_tokens = 0
    current_bytes = 0

    def flush() -> None:
        nonlocal current, current_tokens, current_bytes
        if not current:
            return
        batches.append(
            EmbeddingPlanBatch(
                index=len(batches),
                items=tuple(current),
                token_count=current_tokens,
                utf8_bytes=current_bytes,
            )
        )
        current = []
        current_tokens = 0
        current_bytes = 0

    for item in items:
        if current and (
            len(current) + 1 > limits.max_items_per_batch
            or current_tokens + item.token_count > limits.max_tokens_per_batch
            or current_bytes + item.utf8_bytes > limits.max_utf8_bytes_per_batch
        ):
            flush()
        # A valid profile makes this unreachable; retain it so a forged or
        # mutated profile cannot dispatch an oversized single item.
        if (
            item.token_count > limits.max_tokens_per_batch
            or item.utf8_bytes > limits.max_utf8_bytes_per_batch
        ):
            raise EmbeddingError("EMBEDDING_ITEM_LIMIT_EXCEEDED")
        current.append(item)
        current_tokens += item.token_count
        current_bytes += item.utf8_bytes
    flush()

    return EmbeddingBatchPlan(
        profile_id=profile.profile_id,
        profile_fingerprint=profile.fingerprint,
        compatibility_fingerprint=profile.compatibility_fingerprint,
        space_fingerprint=profile.space_fingerprint,
        purpose=profile.purpose,
        dimension=profile.dimension,
        normalization=profile.normalization,
        input_prefix=profile.input_prefix,
        limits=profile.limits,
        items=tuple(items),
        batches=tuple(batches),
    )


def validate_shared_vector_space(
    *,
    query_profile: EmbeddingProfile,
    document_profile: EmbeddingProfile,
) -> str:
    """Returns the shared vector-space fingerprint or a finite rejection.

    This checks the cross-purpose space key only.  Planning and result
    validation separately require each profile to be verified.
    """

    if not isinstance(query_profile, EmbeddingProfile) or not isinstance(
        document_profile, EmbeddingProfile
    ):
        raise EmbeddingError("EMBEDDING_PROFILE_INVALID")
    if (
        query_profile.purpose != "query"
        or document_profile.purpose != "document"
    ):
        raise EmbeddingError("EMBEDDING_PURPOSE_MISMATCH")
    if query_profile.space_fingerprint != document_profile.space_fingerprint:
        raise EmbeddingError("EMBEDDING_SPACE_MISMATCH")
    return query_profile.space_fingerprint


def validate_provider_binding(
    *,
    provider: EmbeddingProvider,
    plan: EmbeddingBatchPlan,
) -> None:
    """Checks that an adapter identifies the exact immutable profile of a plan.

    The adapter's ``embed_batch`` method is checked for callability but is not
    invoked.  This function therefore performs no external dispatch.
    """

    if not isinstance(plan, EmbeddingBatchPlan):
        raise EmbeddingError("EMBEDDING_PLAN_INVALID")
    try:
        provider_profile = provider.profile
        embed_batch = provider.embed_batch
    except Exception:
        provider_profile = None
        embed_batch = None
    if not isinstance(provider_profile, EmbeddingProfile) or not provider_profile.verified:
        raise EmbeddingError("EMBEDDING_PROVIDER_INVALID")
    if not callable(embed_batch):
        raise EmbeddingError("EMBEDDING_PROVIDER_INVALID")
    if (
        provider_profile.fingerprint != plan.profile_fingerprint
        or provider_profile.compatibility_fingerprint
        != plan.compatibility_fingerprint
        or provider_profile.space_fingerprint != plan.space_fingerprint
        or provider_profile.purpose != plan.purpose
        or provider_profile.dimension != plan.dimension
        or provider_profile.normalization != plan.normalization
    ):
        raise EmbeddingError("EMBEDDING_PROVIDER_INVALID")


def validate_embedding_results(
    *,
    profile: EmbeddingProfile,
    plan: EmbeddingBatchPlan,
    results: Sequence[EmbeddingResult],
) -> tuple[tuple[float, ...], ...]:
    """Validates one complete provider response and returns plan-ordered vectors.

    ``results`` may be in any order but must contain exactly one record for
    every global plan ordinal.  Every invalid response is rejected as a whole;
    no vector is repaired, truncated, or zero-filled.  When the profile says
    ``l2``, each accepted vector is normalized with a scale-safe algorithm that
    remains finite for the largest and smallest finite input magnitudes.
    """

    if not isinstance(profile, EmbeddingProfile):
        raise EmbeddingError("EMBEDDING_PROFILE_INVALID")
    if not isinstance(plan, EmbeddingBatchPlan):
        raise EmbeddingError("EMBEDDING_PLAN_INVALID")
    if not profile.verified:
        raise EmbeddingError("EMBEDDING_PROFILE_UNVERIFIED")
    if (
        plan.profile_fingerprint != profile.fingerprint
        or plan.compatibility_fingerprint != profile.compatibility_fingerprint
        or plan.space_fingerprint != profile.space_fingerprint
        or plan.purpose != profile.purpose
        or plan.dimension != profile.dimension
        or plan.normalization != profile.normalization
    ):
        raise EmbeddingError("EMBEDDING_PLAN_INVALID")
    if not isinstance(results, Sequence) or isinstance(
        results, (str, bytes, bytearray)
    ):
        raise EmbeddingError("EMBEDDING_RESULT_INVALID")

    expected = len(plan.items)
    if len(results) != expected:
        raise EmbeddingError("EMBEDDING_RESULT_COUNT_MISMATCH")

    ordered: list[tuple[float, ...] | None] = [None] * expected
    for candidate in results:
        if not isinstance(candidate, EmbeddingResult):
            raise EmbeddingError("EMBEDDING_RESULT_INVALID")
        ordinal = candidate.ordinal
        if type(ordinal) is not int or ordinal < 0 or ordinal >= expected:
            raise EmbeddingError("EMBEDDING_RESULT_ORDINAL_INVALID")
        if ordered[ordinal] is not None:
            raise EmbeddingError("EMBEDDING_RESULT_ORDINAL_INVALID")
        vector = candidate.vector
        if not isinstance(vector, (tuple, list)):
            raise EmbeddingError("EMBEDDING_RESULT_VALUE_INVALID")
        if len(vector) != profile.dimension:
            raise EmbeddingError("EMBEDDING_RESULT_DIMENSION_MISMATCH")
        converted: list[float] = []
        all_zero = True
        for value in vector:
            if type(value) is bool or not isinstance(value, (int, float)):
                raise EmbeddingError("EMBEDDING_RESULT_VALUE_INVALID")
            try:
                number = float(value)
            except Exception:
                number = None
            if number is None or not math.isfinite(number):
                raise EmbeddingError("EMBEDDING_RESULT_VALUE_INVALID")
            if number != 0.0:
                all_zero = False
            converted.append(0.0 if number == 0.0 else number)
        if all_zero:
            raise EmbeddingError("EMBEDDING_RESULT_ZERO_VECTOR")
        if profile.normalization == "l2":
            ordered[ordinal] = _l2_normalize(converted)
        else:
            ordered[ordinal] = tuple(converted)

    final: list[tuple[float, ...]] = []
    for vector in ordered:
        if vector is None:
            raise EmbeddingError("EMBEDDING_RESULT_ORDINAL_INVALID")
        final.append(vector)
    return tuple(final)


def _l2_normalize(values: Sequence[float]) -> tuple[float, ...]:
    """Scale by the largest magnitude before squaring to avoid overflow."""

    scale = max(abs(value) for value in values)
    if scale == 0.0 or not math.isfinite(scale):
        raise EmbeddingError("EMBEDDING_RESULT_VALUE_INVALID")
    scaled = [value / scale for value in values]
    squares = math.fsum(value * value for value in scaled)
    if not math.isfinite(squares) or squares <= 0.0:
        raise EmbeddingError("EMBEDDING_RESULT_VALUE_INVALID")
    norm = math.sqrt(squares)
    if not math.isfinite(norm) or norm <= 0.0:
        raise EmbeddingError("EMBEDDING_RESULT_VALUE_INVALID")
    normalized: list[float] = []
    for value in scaled:
        component = value / norm
        if not math.isfinite(component):
            raise EmbeddingError("EMBEDDING_RESULT_VALUE_INVALID")
        normalized.append(0.0 if component == 0.0 else component)
    return tuple(normalized)

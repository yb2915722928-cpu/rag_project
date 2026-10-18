from __future__ import annotations

import dataclasses
import math

import pytest

from rag_app.modules.indexing.embedding import (
    EmbeddingBatchPlan,
    EmbeddingError,
    EmbeddingLimits,
    EmbeddingProfile,
    EmbeddingResult,
    plan_embedding_batches,
    validate_embedding_results,
    validate_provider_binding,
    validate_shared_vector_space,
)


class CountingCounter:
    """Deterministic stand-in for a verified provider tokenizer."""

    def __init__(self, tokenizer="tok.v1", *, per_char=False, failure=None):
        self.tokenizer = tokenizer
        self.per_char = per_char
        self.failure = failure
        self.calls = []

    def count_tokens(self, text: str) -> int:
        self.calls.append(text)
        if self.failure is not None:
            raise self.failure
        return len(text) if self.per_char else 1


def limits(**overrides):
    values = dict(
        max_tokens_per_item=10,
        max_tokens_per_batch=20,
        max_utf8_bytes_per_item=100,
        max_utf8_bytes_per_batch=200,
        max_items_per_batch=2,
    )
    values.update(overrides)
    return EmbeddingLimits(**values)


def profile(**overrides):
    values = dict(
        profile_id="doc-profile.v1",
        provider="provider-a",
        model="embed-model-a",
        deployment="deployment-a/2026-10-01",
        dimension=4,
        tokenizer="tok.v1",
        preprocessing="preprocess.v1",
        normalization="l2",
        purpose="document",
        input_prefix="",
        limits=limits(),
        verified=True,
        evidence_ref="/fileOfRag/testOfRAG/metadata/u2b/profile-evidence.json",
    )
    values.update(overrides)
    return EmbeddingProfile(**values)


def query_profile(**overrides):
    values = dict(
        profile_id="query-profile.v1",
        purpose="query",
        input_prefix="query: ",
    )
    values.update(overrides)
    return profile(**values)


def document_profile(**overrides):
    values = dict(
        profile_id="document-profile.v1",
        purpose="document",
        input_prefix="document: ",
    )
    values.update(overrides)
    return profile(**values)


def plan(texts, *, prof=None, purpose="document", counter=None):
    return plan_embedding_batches(
        profile=prof or profile(),
        purpose=purpose,
        texts=texts,
        counter=counter or CountingCounter(),
    )


def reject(call, code):
    with pytest.raises(EmbeddingError) as caught:
        call()
    assert caught.value.code == code
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None
    return caught.value


def vector(*values):
    return tuple(float(value) for value in values)


def test_limits_require_every_explicit_value():
    reject(lambda: EmbeddingLimits(), "EMBEDDING_PROFILE_INVALID")
    for field in (
        "max_tokens_per_item",
        "max_tokens_per_batch",
        "max_utf8_bytes_per_item",
        "max_utf8_bytes_per_batch",
        "max_items_per_batch",
    ):
        values = dict(
            max_tokens_per_item=10,
            max_tokens_per_batch=20,
            max_utf8_bytes_per_item=100,
            max_utf8_bytes_per_batch=200,
            max_items_per_batch=2,
        )
        values[field] = None
        reject(
            lambda values=values: EmbeddingLimits(**values),
            "EMBEDDING_PROFILE_INVALID",
        )


@pytest.mark.parametrize(
    "overrides",
    [
        {"max_tokens_per_item": 0},
        {"max_tokens_per_item": -1},
        {"max_tokens_per_item": True},
        {"max_tokens_per_item": 1.0},
        {"max_tokens_per_batch": 9},
        {"max_utf8_bytes_per_batch": 99},
        {"max_items_per_batch": 0},
        {"max_items_per_batch": 2_147_483_648},
    ],
)
def test_limits_reject_non_finite_or_contradictory_values(overrides):
    reject(lambda: limits(**overrides), "EMBEDDING_PROFILE_INVALID")


def test_profile_is_immutable():
    frozen = profile()
    with pytest.raises(dataclasses.FrozenInstanceError):
        frozen.dimension = 8
    with pytest.raises(dataclasses.FrozenInstanceError):
        frozen.limits.max_tokens_per_batch = 1


def test_verified_profile_requires_evidence_reference():
    reject(
        lambda: profile(evidence_ref=None),
        "EMBEDDING_PROFILE_INVALID",
    )
    reject(
        lambda: profile(evidence_ref="   "),
        "EMBEDDING_PROFILE_INVALID",
    )
    assert profile(verified=False, evidence_ref=None).verified is False


@pytest.mark.parametrize(
    "overrides",
    [
        {"profile_id": ""},
        {"profile_id": "bad profile"},
        {"provider": ""},
        {"model": "m" * 129},
        {"deployment": "dep\nvalue"},
        {"dimension": 0},
        {"dimension": True},
        {"dimension": 65_537},
        {"tokenizer": ""},
        {"preprocessing": "-starts-with-punctuation"},
        {"normalization": "l1"},
        {"purpose": "both"},
        {"input_prefix": "x" * 257},
        {"limits": {"max_tokens_per_item": 1}},
        {"verified": "yes"},
    ],
)
def test_profile_rejects_invalid_or_ambiguous_fields(overrides):
    reject(lambda: profile(**overrides), "EMBEDDING_PROFILE_INVALID")


def test_profile_fingerprints_change_for_every_compatibility_input():
    base = profile()
    assert base.space_fingerprint == base.space_fingerprint
    assert base.compatibility_fingerprint == base.compatibility_fingerprint
    assert base.fingerprint == base.fingerprint
    assert base.fingerprint != base.compatibility_fingerprint
    assert base.compatibility_fingerprint != base.space_fingerprint

    variants = [
        profile(provider="provider-b"),
        profile(model="embed-model-b"),
        profile(deployment="deployment-b/2026-10-01"),
        profile(dimension=8),
        profile(tokenizer="tok.v2"),
        profile(preprocessing="preprocess.v2"),
        profile(normalization="none"),
        profile(purpose="query"),
        profile(input_prefix="document: "),
        profile(limits=limits(max_tokens_per_batch=21)),
        profile(profile_id="doc-profile.v2"),
        profile(evidence_ref="/other/evidence.json"),
        profile(verified=False, evidence_ref=None),
    ]
    for variant in variants:
        assert variant.fingerprint != base.fingerprint
        assert variant.compatibility_fingerprint != base.compatibility_fingerprint
        assert variant.space_fingerprint != base.space_fingerprint


def test_query_and_document_profiles_can_share_one_vector_space():
    query = query_profile()
    document = document_profile()
    assert query.space_fingerprint == document.space_fingerprint
    assert query.compatibility_fingerprint != document.compatibility_fingerprint
    assert query.profile_id != document.profile_id
    assert validate_shared_vector_space(
        query_profile=query, document_profile=document
    ) == query.space_fingerprint


def test_shared_space_rejects_different_model_or_normalization():
    query = query_profile()
    reject(
        lambda: validate_shared_vector_space(
            query_profile=query,
            document_profile=document_profile(model="embed-model-b"),
        ),
        "EMBEDDING_SPACE_MISMATCH",
    )
    reject(
        lambda: validate_shared_vector_space(
            query_profile=query,
            document_profile=document_profile(normalization="none"),
        ),
        "EMBEDDING_SPACE_MISMATCH",
    )
    reject(
        lambda: validate_shared_vector_space(
            query_profile=document_profile(),
            document_profile=query_profile(),
        ),
        "EMBEDDING_PURPOSE_MISMATCH",
    )


def test_plan_is_deterministic_and_lossless():
    texts = ["alpha", " beta ", "gamma\nline", "δ"]
    first = plan(texts)
    second = plan(list(texts))
    assert first == second
    assert first.item_count == len(texts)
    assert first.ordinals == (0, 1, 2, 3)
    assert tuple(item.text for item in first.items) == tuple(texts)
    assert tuple(item.provider_text for item in first.items) == tuple(texts)
    assert first.profile_fingerprint == profile().fingerprint
    assert first.compatibility_fingerprint == profile().compatibility_fingerprint
    assert first.space_fingerprint == profile().space_fingerprint
    assert first.dimension == 4
    assert first.purpose == "document"
    assert [batch.ordinals for batch in first.batches] == [(0, 1), (2, 3)]


def test_plan_applies_the_exact_profile_prefix_without_mutating_text():
    prof = document_profile()
    result = plan(["text"], prof=prof)
    item = result.items[0]
    assert item.text == "text"
    assert item.provider_text == "document: text"
    assert item.utf8_bytes == len("document: text".encode("utf-8"))
    assert result.input_prefix == "document: "


def test_plan_respects_item_and_batch_token_byte_and_count_boundaries():
    counter = CountingCounter(per_char=True)
    prof = profile(
        limits=limits(
            max_tokens_per_item=5,
            max_tokens_per_batch=10,
            max_utf8_bytes_per_item=5,
            max_utf8_bytes_per_batch=10,
            max_items_per_batch=2,
        )
    )
    result = plan(
        ["a", "bb", "ccc", "dddd", "eeeee"],
        prof=prof,
        counter=counter,
    )
    assert [batch.ordinals for batch in result.batches] == [(0, 1, 2), (3, 4)]
    assert [batch.token_count for batch in result.batches] == [6, 9]
    assert [batch.utf8_bytes for batch in result.batches] == [6, 9]
    assert counter.calls == ["a", "bb", "ccc", "dddd", "eeeee"]


def test_plan_byte_limit_can_split_before_token_limit():
    counter = CountingCounter()
    prof = profile(
        limits=limits(
            max_tokens_per_item=100,
            max_tokens_per_batch=100,
            max_utf8_bytes_per_item=4,
            max_utf8_bytes_per_batch=8,
            max_items_per_batch=10,
        )
    )
    result = plan(["aa", "bb", "cc", "dd", "ee"], prof=prof, counter=counter)
    assert [batch.ordinals for batch in result.batches] == [(0, 1), (2, 3), (4,)]
    assert [batch.utf8_bytes for batch in result.batches] == [4, 4, 2]


def test_plan_rejects_a_single_item_above_a_limit_without_echoing_it():
    secret = "sk-very-secret-value"
    error = reject(
        lambda: plan(
            [secret],
            prof=profile(limits=limits(max_utf8_bytes_per_item=4)),
        ),
        "EMBEDDING_ITEM_LIMIT_EXCEEDED",
    )
    assert secret not in str(error)
    assert "http" not in str(error).lower()


def test_plan_rejects_an_oversized_token_count():
    secret = "a" * 1000
    error = reject(
        lambda: plan(
            [secret],
            prof=profile(),
            counter=CountingCounter(per_char=True),
        ),
        "EMBEDDING_ITEM_LIMIT_EXCEEDED",
    )
    assert secret not in str(error)


def test_plan_requires_a_verified_profile():
    reject(
        lambda: plan(
            ["text"],
            prof=profile(verified=False, evidence_ref=None),
        ),
        "EMBEDDING_PROFILE_UNVERIFIED",
    )


def test_plan_requires_an_explicit_matching_purpose():
    reject(lambda: plan(["text"], purpose="query"), "EMBEDDING_PURPOSE_MISMATCH")
    reject(lambda: plan(["text"], purpose="both"), "EMBEDDING_PURPOSE_MISMATCH")


def test_plan_requires_the_exact_tokenizer_counter():
    reject(
        lambda: plan(["text"], counter=CountingCounter("tok.v2")),
        "EMBEDDING_COUNTER_INVALID",
    )
    reject(
        lambda: plan(["text"], counter=CountingCounter(failure=RuntimeError("boom"))),
        "EMBEDDING_COUNTER_INVALID",
    )
    for value in (True, -1, 1.5, "1", None):
        counter = CountingCounter()
        counter.count_tokens = lambda text, value=value: value
        reject(
            lambda counter=counter: plan(["text"], counter=counter),
            "EMBEDDING_COUNTER_INVALID",
        )


def test_plan_rejects_empty_and_non_text_inputs():
    for texts in ([], [""], [None], [b"bytes"], "text", b"text", None):
        reject(lambda texts=texts: plan(texts), "EMBEDDING_INPUT_INVALID")


def test_plan_never_calls_a_provider_or_retries_the_counter():
    counter = CountingCounter()
    prof = profile(limits=limits(max_items_per_batch=1))
    provider = FakeProvider(prof)
    result = plan(["a", "b", "c"], prof=prof, counter=counter)
    assert counter.calls == ["a", "b", "c"]
    assert provider.calls == []
    assert len(result.batches) == 3


class FakeProvider:
    def __init__(self, prof, results=None, failure=None):
        self._profile = prof
        self.results = results or []
        self.failure = failure
        self.calls = []

    @property
    def profile(self):
        return self._profile

    def embed_batch(self, batch):
        self.calls.append(batch)
        if self.failure is not None:
            raise self.failure
        return self.results


def test_results_are_reordered_by_global_request_ordinal():
    result = plan(["a", "b", "c"], prof=profile(dimension=2))
    shuffle = [
        EmbeddingResult(2, vector(3, 4)),
        EmbeddingResult(0, vector(1, 0)),
        EmbeddingResult(1, vector(0, 1)),
    ]
    vectors = validate_embedding_results(
        profile=profile(dimension=2), plan=result, results=shuffle
    )
    assert len(vectors) == 3
    assert vectors[0] == (1.0, 0.0)
    assert vectors[1] == (0.0, 1.0)
    assert math.isclose(vectors[2][0], 0.6, rel_tol=0, abs_tol=1e-15)
    assert math.isclose(vectors[2][1], 0.8, rel_tol=0, abs_tol=1e-15)


def test_results_accept_lists_and_reject_bool_or_non_numeric_values():
    result = plan(["a"], prof=profile(dimension=2))
    accepted = validate_embedding_results(
        profile=profile(dimension=2),
        plan=result,
        results=[EmbeddingResult(0, [1, 2])],
    )
    assert accepted[0] == (1 / math.sqrt(5), 2 / math.sqrt(5))
    for vector_value in (
        [True, 1.0],
        [1.0, "1"],
        [None, 1.0],
        [1.0, float("nan")],
        [1.0, float("inf")],
        [1.0, float("-inf")],
        "1,2",
    ):
        reject(
            lambda vector_value=vector_value: validate_embedding_results(
                profile=profile(dimension=2),
                plan=result,
                results=[EmbeddingResult(0, vector_value)],
            ),
            "EMBEDDING_RESULT_VALUE_INVALID",
        )


def test_results_reject_duplicate_missing_and_extra_ordinals():
    result = plan(["a", "b"], prof=profile(dimension=2))
    reject(
        lambda: validate_embedding_results(
            profile=profile(dimension=2),
            plan=result,
            results=[
                EmbeddingResult(0, vector(1, 0)),
                EmbeddingResult(0, vector(0, 1)),
            ],
        ),
        "EMBEDDING_RESULT_ORDINAL_INVALID",
    )
    reject(
        lambda: validate_embedding_results(
            profile=profile(dimension=2),
            plan=result,
            results=[EmbeddingResult(0, vector(1, 0))],
        ),
        "EMBEDDING_RESULT_COUNT_MISMATCH",
    )
    reject(
        lambda: validate_embedding_results(
            profile=profile(dimension=2),
            plan=result,
            results=[
                EmbeddingResult(0, vector(1, 0)),
                EmbeddingResult(2, vector(0, 1)),
            ],
        ),
        "EMBEDDING_RESULT_ORDINAL_INVALID",
    )
    reject(
        lambda: validate_embedding_results(
            profile=profile(dimension=2),
            plan=result,
            results=[
                EmbeddingResult(0, vector(1, 0)),
                EmbeddingResult(1, vector(0, 1)),
                EmbeddingResult(2, vector(1, 1)),
            ],
        ),
        "EMBEDDING_RESULT_COUNT_MISMATCH",
    )


def test_results_reject_wrong_dimension_and_zero_vectors():
    result = plan(["a"], prof=profile(dimension=3))
    reject(
        lambda: validate_embedding_results(
            profile=profile(dimension=3),
            plan=result,
            results=[EmbeddingResult(0, vector(1, 2))],
        ),
        "EMBEDDING_RESULT_DIMENSION_MISMATCH",
    )
    reject(
        lambda: validate_embedding_results(
            profile=profile(dimension=3),
            plan=result,
            results=[EmbeddingResult(0, vector(0, 0, 0))],
        ),
        "EMBEDDING_RESULT_ZERO_VECTOR",
    )
    reject(
        lambda: validate_embedding_results(
            profile=profile(dimension=3),
            plan=result,
            results=[EmbeddingResult(0, (-0.0, 0, 0))],
        ),
        "EMBEDDING_RESULT_ZERO_VECTOR",
    )


def test_results_must_match_the_exact_plan_profile():
    document = profile(dimension=2)
    query = query_profile(dimension=2)
    result = plan(["a"], prof=document)
    reject(
        lambda: validate_embedding_results(
            profile=query,
            plan=result,
            results=[EmbeddingResult(0, vector(1, 0))],
        ),
        "EMBEDDING_PLAN_INVALID",
    )
    other_limits = profile(
        dimension=2, limits=limits(max_tokens_per_batch=21)
    )
    reject(
        lambda: validate_embedding_results(
            profile=other_limits,
            plan=result,
            results=[EmbeddingResult(0, vector(1, 0))],
        ),
        "EMBEDDING_PLAN_INVALID",
    )


def test_l2_normalization_is_stable_for_extreme_finite_magnitudes():
    prof = profile(dimension=3)
    result = plan(["a"], prof=prof)
    for values in (
        (1.7976931348623157e308, -1.7976931348623157e308, 1.0),
        (5e-324, 1e-323, -5e-324),
        (1e-200, 2e-200, 3e-200),
    ):
        vectors = validate_embedding_results(
            profile=prof,
            plan=result,
            results=[EmbeddingResult(0, values)],
        )
        normalized = vectors[0]
        assert all(math.isfinite(value) for value in normalized)
        assert math.isclose(
            math.fsum(value * value for value in normalized),
            1.0,
            rel_tol=0,
            abs_tol=1e-12,
        )
    tiny = validate_embedding_results(
        profile=prof,
        plan=result,
        results=[EmbeddingResult(0, (5e-324, 1e-323, -5e-324))],
    )[0]
    assert tiny[0] < 0 < tiny[1]


def test_none_normalization_preserves_the_exact_finite_values():
    prof = profile(dimension=2, normalization="none")
    result = plan(["a"], prof=prof)
    vectors = validate_embedding_results(
        profile=prof,
        plan=result,
        results=[EmbeddingResult(0, (3, 4))],
    )
    assert vectors == ((3.0, 4.0),)


def test_provider_binding_accepts_only_the_exact_verified_profile():
    prof = profile(dimension=2)
    result = plan(["a"], prof=prof)
    validate_provider_binding(provider=FakeProvider(prof), plan=result)
    for other in (
        query_profile(dimension=2),
        profile(dimension=3),
        profile(normalization="none"),
        profile(verified=False, evidence_ref=None),
    ):
        reject(
            lambda other=other: validate_provider_binding(
                provider=FakeProvider(other), plan=result
            ),
            "EMBEDDING_PROVIDER_INVALID",
        )


def test_errors_are_finite_and_never_include_inputs_endpoints_or_secrets():
    secret = "https://provider.example.invalid/v1?key=secret"
    prof = profile(input_prefix=secret)
    result = plan([secret], prof=prof)
    error = reject(
        lambda: validate_embedding_results(
            profile=prof,
            plan=result,
            results=[EmbeddingResult(0, vector(0, 0, 0, 0))],
        ),
        "EMBEDDING_RESULT_ZERO_VECTOR",
    )
    message = str(error)
    assert secret not in message
    assert "provider.example" not in message
    assert "secret" not in message
    assert message.startswith("EMBEDDING_RESULT_ZERO_VECTOR: ")


def test_plan_type_cannot_be_forged_with_mismatched_items():
    prof = profile()
    result = plan(["a"], prof=prof)
    with pytest.raises(EmbeddingError):
        EmbeddingBatchPlan(
            profile_id=result.profile_id,
            profile_fingerprint=result.profile_fingerprint,
            compatibility_fingerprint=result.compatibility_fingerprint,
            space_fingerprint=result.space_fingerprint,
            purpose=result.purpose,
            dimension=result.dimension,
            normalization=result.normalization,
            input_prefix=result.input_prefix,
            limits=result.limits,
            items=(dataclasses.replace(result.items[0], text="b"),),
            batches=result.batches,
        )

from app.models import Source, Fact


def test_source_model_required_fields_and_defaults():
    s = Source(source_id="src_0", title="Example", url="https://example.com",
               domain="example.com", snippet="a snippet")
    assert s.source_id == "src_0"
    assert s.content is None
    assert s.authority_score == 0.0
    assert s.quality_score == 0.0


def test_fact_model_defaults_to_unverified():
    f = Fact(fact_id="fact_0", claim="The sky is blue.")
    assert f.status == "UNVERIFIED"
    assert f.date == "unknown"
    assert f.location == "unknown"
    assert f.source_ids == []

from rag.models import ComplianceResult, RegulationRef


def test_regulation_ref_with_alias():
    ref = RegulationRef(
        regulation="GDPR",
        article="5",
        sourceUrl="https://example.com/gdpr",
        excerpt="Lawful processing requirement.",
    )
    assert ref.regulation == "GDPR"
    assert ref.article == "5"
    assert ref.source_url == "https://example.com/gdpr"
    assert ref.excerpt == "Lawful processing requirement."


def test_regulation_ref_serializes_with_alias():
    ref = RegulationRef(
        regulation="EU AI Act",
        article="52",
        sourceUrl="https://example.com/ai-act",
        excerpt="Transparency obligations.",
    )
    data = ref.model_dump(by_alias=True)
    assert data["sourceUrl"] == "https://example.com/ai-act"
    assert "source_url" not in data


def test_compliance_result_with_alias():
    ref = RegulationRef(
        regulation="GDPR",
        article="5",
        sourceUrl="https://example.com/gdpr",
        excerpt="Lawful processing.",
    )
    result = ComplianceResult(
        summary="GDPR Article 5 applies.",
        regulationRefs=[ref],
    )
    assert result.summary == "GDPR Article 5 applies."
    assert len(result.regulation_refs) == 1
    assert result.regulation_refs[0].regulation == "GDPR"


def test_compliance_result_serializes_with_alias():
    ref = RegulationRef(
        regulation="GDPR",
        article="5",
        sourceUrl="https://example.com/gdpr",
        excerpt="Lawful processing.",
    )
    result = ComplianceResult(
        summary="Summary text.",
        regulationRefs=[ref],
    )
    data = result.model_dump(by_alias=True)
    assert "regulationRefs" in data
    assert data["regulationRefs"][0]["sourceUrl"] == "https://example.com/gdpr"

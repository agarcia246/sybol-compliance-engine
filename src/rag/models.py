from pydantic import BaseModel, ConfigDict, Field


class RegulationRef(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    regulation: str
    article: str
    source_url: str = Field(alias="sourceUrl")
    excerpt: str


class ComplianceResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    summary: str
    regulation_refs: list[RegulationRef] = Field(alias="regulationRefs")

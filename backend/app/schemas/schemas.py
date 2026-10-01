from pydantic import BaseModel, Field, field_validator

class LeadCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    location: str = Field(min_length=1, max_length=120)
    property_requirement: str = Field(min_length=1)
    budget: float = Field(gt=0)
    timeline: str = Field(min_length=1, max_length=80)
    customer_message: str = Field(min_length=1)
    bhk: list[int] = [3]
    parking_required: bool = False

    @field_validator("bhk")
    @classmethod
    def validate_bhk(cls, value):
        if not value or any(v <= 0 or v > 10 for v in value):
            raise ValueError("BHK must contain valid positive values")
        return sorted(set(value))

class LeadPatch(BaseModel):
    name: str | None = None
    location: str | None = None
    property_requirement: str | None = None
    budget: float | None = Field(default=None, gt=0)
    timeline: str | None = None
    bhk: list[int] | None = None
    parking_required: bool | None = None

class InteractionCreate(BaseModel):
    type: str = Field(min_length=1, max_length=30)
    note: str = Field(min_length=1)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

class ChatResponse(BaseModel):
    answer: str = Field(min_length=1)

class Change(BaseModel):
    field: str
    old_value: object
    new_value: object
    reason: str = Field(min_length=1)

class ChangeResponse(BaseModel):
    changes: list[Change]

class AIAnalysis(BaseModel):
    summary: str
    intent: str
    key_requirements: list[str]
    objections: list[str]
    recommended_next_action: str
    suggested_response: str

from pydantic import BaseModel, Field, model_validator


class ZohoExpenseInput(BaseModel):
    action: str = Field(..., pattern="^(get|create|update)$")
    expense_id: str | None = None
    data: dict | None = None

    @model_validator(mode="after")
    def validate_required_fields(self):
        if self.action in ("get", "update") and self.expense_id is None:
            raise ValueError("expense_id is required for get and update actions")
        if self.action in ("create", "update") and self.data is None:
            raise ValueError("data is required for create and update actions")
        return self


class ZohoPoliciesInput(BaseModel):
    action: str = Field(..., pattern="^(list|evaluate)$")
    policy_id: str | None = None
    data: dict | None = None

    @model_validator(mode="after")
    def validate_required_fields(self):
        if self.action == "evaluate" and self.policy_id is None:
            raise ValueError("policy_id is required for evaluate action")
        return self

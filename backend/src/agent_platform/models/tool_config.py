from pydantic import BaseModel, Field


class ZohoExpenseConfig(BaseModel):
    organization_id: str = Field(..., min_length=1)
    api_endpoint: str = Field(default="https://expense.zoho.com/api/v1")

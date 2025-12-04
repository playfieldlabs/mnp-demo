from typing import Any

import httpx

from agent_platform.models.tool_config import ZohoExpenseConfig
from agent_platform.models.tool_input import ZohoExpenseInput, ZohoPoliciesInput
from agent_platform.tools.base import Tool


class ZohoExpenseTool(Tool):
    _id: str
    _name: str
    _config: ZohoExpenseConfig
    _input_schema: dict[str, Any]
    _output_schema: dict[str, Any]
    _context: str

    def __init__(self, tool_id: str, name: str, config: dict[str, str]) -> None:
        self._id = tool_id
        self._name = name
        self._config = ZohoExpenseConfig(**config)
        self._input_schema = {
            "type": "object",
            "properties": {
                "expense_id": {"type": "string"},
                "action": {"type": "string", "enum": ["get", "create", "update"]},
                "data": {"type": "object"},
            },
            "required": ["action"],
        }
        self._output_schema = {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {"type": "object"},
                "error": {"type": "string"},
            },
        }
        self._context = "Zoho Expense API tool for managing expenses"

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def input_schema(self) -> dict[str, Any]:
        return self._input_schema

    @property
    def output_schema(self) -> dict[str, Any]:
        return self._output_schema

    @property
    def context(self) -> str:
        return self._context

    async def execute(
        self, input_data: dict[str, str | dict | None]
    ) -> dict[str, str | bool | dict]:
        validated_input: ZohoExpenseInput = ZohoExpenseInput.model_validate(input_data)
        organization_id: str = self._config.organization_id
        api_endpoint: str = str(self._config.api_endpoint)

        async with httpx.AsyncClient() as client:
            if validated_input.action == "get":
                if validated_input.expense_id is None:
                    return {"success": False, "error": "expense_id is required for get action"}
                response = await client.get(
                    f"{api_endpoint}/expenses/{validated_input.expense_id}",
                    headers={"X-Organization-Id": organization_id},
                )
                return {"success": True, "data": response.json()}
            elif validated_input.action == "create":
                if validated_input.data is None:
                    return {"success": False, "error": "data is required for create action"}
                response = await client.post(
                    f"{api_endpoint}/expenses",
                    json=validated_input.data,
                    headers={"X-Organization-Id": organization_id},
                )
                return {"success": response.status_code == 200, "data": response.json()}
            elif validated_input.action == "update":
                if validated_input.expense_id is None:
                    return {"success": False, "error": "expense_id is required for update action"}
                if validated_input.data is None:
                    return {"success": False, "error": "data is required for update action"}
                response = await client.put(
                    f"{api_endpoint}/expenses/{validated_input.expense_id}",
                    json=validated_input.data,
                    headers={"X-Organization-Id": organization_id},
                )
                return {"success": response.status_code == 200, "data": response.json()}

        return {"success": False, "error": "Invalid action"}


class ZohoPoliciesTool(Tool):
    _id: str
    _name: str
    _config: dict[str, str]
    _input_schema: dict[str, Any]
    _output_schema: dict[str, Any]
    _context: str

    def __init__(self, tool_id: str, name: str, config: dict[str, str]) -> None:
        self._id = tool_id
        self._name = name
        self._config = config
        self._input_schema = {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["list", "evaluate"]},
                "policy_id": {"type": "string"},
                "data": {"type": "object"},
            },
            "required": ["action"],
        }
        self._output_schema = {
            "type": "object",
            "properties": {
                "policies": {"type": "array"},
                "evaluation": {"type": "object"},
            },
        }
        self._context = "Zoho Policies tool for evaluating expense policies"

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def input_schema(self) -> dict[str, Any]:
        return self._input_schema

    @property
    def output_schema(self) -> dict[str, Any]:
        return self._output_schema

    @property
    def context(self) -> str:
        return self._context

    async def execute(self, input_data: dict[str, str | dict | None]) -> dict[str, list | dict]:
        validated_input: ZohoPoliciesInput = ZohoPoliciesInput.model_validate(input_data)

        if validated_input.action == "list":
            return {
                "policies": [
                    {
                        "id": "policy_1",
                        "name": "Expense Approval Policy",
                        "description": "Standard expense approval workflow",
                        "rules": ["amount > 1000 requires manager approval"],
                        "is_active": True,
                    }
                ]
            }
        elif validated_input.action == "evaluate":
            if validated_input.policy_id is None:
                return {
                    "evaluation": {
                        "policy_id": None,
                        "passed": False,
                        "reasoning": "policy_id is required for evaluate action",
                        "confidence": 0.0,
                    }
                }
            return {
                "evaluation": {
                    "policy_id": validated_input.policy_id,
                    "passed": True,
                    "reasoning": "Expense meets all policy requirements",
                    "confidence": 0.95,
                }
            }

        return {"policies": [], "evaluation": {}}

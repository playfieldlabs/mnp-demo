from agent_platform.models.agent_config import AgentConfig


class AgentModel:
    id: str
    name: str
    task: str
    tool_ids: list[str]
    system_prompt: str
    policy_agent_ids: list[str]
    config: AgentConfig

    def __init__(
        self,
        id: str,
        name: str,
        task: str,
        tool_ids: list[str],
        system_prompt: str,
        policy_agent_ids: list[str],
        config: AgentConfig,
    ):
        self.id = id
        self.name = name
        self.task = task
        self.tool_ids = tool_ids
        self.system_prompt = system_prompt
        self.policy_agent_ids = policy_agent_ids
        self.config: AgentConfig = config

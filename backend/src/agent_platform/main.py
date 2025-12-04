from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount

from agent_platform.config import settings
from agent_platform.llm.client import AnthropicClient
from agent_platform.llm.executor import AgentExecutor
from agent_platform.services.agent import AgentServiceImpl
from agent_platform.services.tool import ToolServiceImpl
from agent_platform.tools.registry import ToolRegistry


def create_app() -> Starlette:
    llm_client: AnthropicClient = AnthropicClient()
    tool_registry: ToolRegistry = ToolRegistry()
    executor: AgentExecutor = AgentExecutor(llm_client, tool_registry)

    agent_service: AgentServiceImpl = AgentServiceImpl(executor)
    tool_service: ToolServiceImpl = ToolServiceImpl()

    routes: list[Mount] = []

    try:
        from agent_platform.service.v1.agent_service_connect import (
            AgentServiceASGIApplication,
        )
        from agent_platform.service.v1.benchmark_service_connect import (
            BenchmarkServiceASGIApplication,
        )
        from agent_platform.service.v1.dataset_service_connect import (
            DatasetServiceASGIApplication,
        )
        from agent_platform.service.v1.policy_service_connect import (
            PolicyServiceASGIApplication,
        )
        from agent_platform.service.v1.tool_service_connect import (
            ToolServiceASGIApplication,
        )
        from agent_platform.service.v1.trajectory_service_connect import (
            TrajectoryServiceASGIApplication,
        )
        from agent_platform.services.benchmark import BenchmarkServiceImpl
        from agent_platform.services.dataset import DatasetServiceImpl
        from agent_platform.services.policy import PolicyServiceImpl
        from agent_platform.services.trajectory import TrajectoryServiceImpl

        policy_service = PolicyServiceImpl()
        dataset_service = DatasetServiceImpl()
        benchmark_service = BenchmarkServiceImpl()
        trajectory_service = TrajectoryServiceImpl()

        agent_app = AgentServiceASGIApplication(agent_service)
        tool_app = ToolServiceASGIApplication(tool_service)
        policy_app = PolicyServiceASGIApplication(policy_service)
        dataset_app = DatasetServiceASGIApplication(dataset_service)
        benchmark_app = BenchmarkServiceASGIApplication(benchmark_service)
        trajectory_app = TrajectoryServiceASGIApplication(trajectory_service)

        routes.extend(
            [
                Mount("/agent_platform.service.v1.AgentService", agent_app),
                Mount("/agent_platform.service.v1.ToolService", tool_app),
                Mount("/agent_platform.service.v1.PolicyService", policy_app),
                Mount("/agent_platform.service.v1.DatasetService", dataset_app),
                Mount("/agent_platform.service.v1.BenchmarkService", benchmark_app),
                Mount("/agent_platform.service.v1.TrajectoryService", trajectory_app),
            ]
        )
    except ImportError as e:
        import logging

        logging.warning(
            f"Could not import generated connect code: {e}. Make sure to run 'pixi run proto' first."
        )

    app = Starlette(routes=routes)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.server_host,
        port=5005,
        reload=True,
    )

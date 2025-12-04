import { create } from '@bufbuild/protobuf';
import { agentClient } from './clients/agent';
import type { Agent } from '$gen/agent_platform/agent/v1/agent_pb.js';
import type { CreateAgentRequest, CreateAgentResponse, GetAgentRequest, GetAgentResponse, ListAgentsRequest, ListAgentsResponse, UpdateAgentRequest, UpdateAgentResponse, RunAgentRequest, RunAgentResponse, GetAgentRunRequest, GetAgentRunResponse, ListAgentRunsRequest, ListAgentRunsResponse, StreamAgentRunRequest } from '$gen/agent_platform/service/v1/agent_service_pb.js';
import { CreateAgentRequestSchema, GetAgentRequestSchema, ListAgentsRequestSchema, UpdateAgentRequestSchema, DeleteAgentRequestSchema, RunAgentRequestSchema, GetAgentRunRequestSchema, ListAgentRunsRequestSchema, StreamAgentRunRequestSchema } from '$gen/agent_platform/service/v1/agent_service_pb.js';
import type { Pagination } from '$gen/agent_platform/common/v1/types_pb.js';

export async function listAgents(pagination?: Pagination): Promise<ListAgentsResponse> {
	const request = create(ListAgentsRequestSchema, { pagination });
	return await agentClient.listAgents(request);
}

export async function getAgent(agentId: string): Promise<GetAgentResponse> {
	const request = create(GetAgentRequestSchema, { agentId });
	return await agentClient.getAgent(request);
}

export async function createAgent(agent: Agent): Promise<CreateAgentResponse> {
	const request = create(CreateAgentRequestSchema, { agent });
	return await agentClient.createAgent(request);
}

export async function updateAgent(agent: Agent): Promise<UpdateAgentResponse> {
	const request = create(UpdateAgentRequestSchema, { agent });
	return await agentClient.updateAgent(request);
}

export async function deleteAgent(agentId: string): Promise<void> {
	const request = create(DeleteAgentRequestSchema, { agentId });
	await agentClient.deleteAgent(request);
}

export async function runAgent(agentId: string, input: string, datasetIds: string[] = []): Promise<RunAgentResponse> {
	const request = create(RunAgentRequestSchema, { agentId, input, datasetIds });
	return await agentClient.runAgent(request);
}

export async function getAgentRun(runId: string): Promise<GetAgentRunResponse> {
	const request = create(GetAgentRunRequestSchema, { runId });
	return await agentClient.getAgentRun(request);
}

export async function listAgentRuns(agentId: string, pagination?: Pagination): Promise<ListAgentRunsResponse> {
	const request = create(ListAgentRunsRequestSchema, { agentId, pagination });
	return await agentClient.listAgentRuns(request);
}

export async function* streamAgentRun(agentId: string, input: string, datasetIds: string[] = []): AsyncGenerator<import('$gen/agent_platform/service/v1/agent_service_pb.js').StreamAgentRunResponse> {
	const request = create(StreamAgentRunRequestSchema, { agentId, input, datasetIds });
	for await (const response of agentClient.streamAgentRun(request)) {
		yield response;
	}
}

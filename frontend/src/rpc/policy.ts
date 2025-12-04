import { create } from '@bufbuild/protobuf';
import { policyClient } from './clients/policy';
import type { PolicyAgent } from '$gen/agent_platform/policy/v1/policy_pb.js';
import type { CreatePolicyAgentRequest, CreatePolicyAgentResponse, GetPolicyAgentRequest, GetPolicyAgentResponse, ListPolicyAgentsRequest, ListPolicyAgentsResponse, UpdatePolicyAgentRequest, UpdatePolicyAgentResponse, DeletePolicyAgentRequest, RunPolicyAgentRequest, RunPolicyAgentResponse, GetPolicyRunRequest, GetPolicyRunResponse, ListPolicyRunsRequest, ListPolicyRunsResponse } from '$gen/agent_platform/service/v1/policy_service_pb.js';
import { CreatePolicyAgentRequestSchema, GetPolicyAgentRequestSchema, ListPolicyAgentsRequestSchema, UpdatePolicyAgentRequestSchema, DeletePolicyAgentRequestSchema, RunPolicyAgentRequestSchema, GetPolicyRunRequestSchema, ListPolicyRunsRequestSchema } from '$gen/agent_platform/service/v1/policy_service_pb.js';
import type { Pagination } from '$gen/agent_platform/common/v1/types_pb.js';

export async function listPolicyAgents(pagination?: Pagination): Promise<ListPolicyAgentsResponse> {
	const request = create(ListPolicyAgentsRequestSchema, { pagination });
	return await policyClient.listPolicyAgents(request);
}

export async function getPolicyAgent(policyAgentId: string): Promise<GetPolicyAgentResponse> {
	const request = create(GetPolicyAgentRequestSchema, { policyAgentId });
	return await policyClient.getPolicyAgent(request);
}

export async function createPolicyAgent(policyAgent: PolicyAgent): Promise<CreatePolicyAgentResponse> {
	const request = create(CreatePolicyAgentRequestSchema, { policyAgent });
	return await policyClient.createPolicyAgent(request);
}

export async function updatePolicyAgent(policyAgent: PolicyAgent): Promise<UpdatePolicyAgentResponse> {
	const request = create(UpdatePolicyAgentRequestSchema, { policyAgent });
	return await policyClient.updatePolicyAgent(request);
}

export async function deletePolicyAgent(policyAgentId: string): Promise<void> {
	const request = create(DeletePolicyAgentRequestSchema, { policyAgentId });
	await policyClient.deletePolicyAgent(request);
}

export async function runPolicyAgent(policyAgentId: string): Promise<RunPolicyAgentResponse> {
	const request = create(RunPolicyAgentRequestSchema, { policyAgentId });
	return await policyClient.runPolicyAgent(request);
}

export async function getPolicyRun(policyRunId: string): Promise<GetPolicyRunResponse> {
	const request = create(GetPolicyRunRequestSchema, { policyRunId });
	return await policyClient.getPolicyRun(request);
}

export async function listPolicyRuns(policyAgentId: string, pagination?: Pagination): Promise<ListPolicyRunsResponse> {
	const request = create(ListPolicyRunsRequestSchema, { policyAgentId, pagination });
	return await policyClient.listPolicyRuns(request);
}

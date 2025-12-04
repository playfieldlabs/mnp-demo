import { create } from '@bufbuild/protobuf';
import { benchmarkClient } from './clients/benchmark';
import type { BenchmarkConfig } from '$gen/agent_platform/benchmark/v1/benchmark_pb.js';
import type { CreateBenchmarkRunRequest, CreateBenchmarkRunResponse, GetBenchmarkRunRequest, GetBenchmarkRunResponse, ListBenchmarkRunsRequest, ListBenchmarkRunsResponse, CompareBenchmarksRequest, CompareBenchmarksResponse, AddBenchmarkCommentRequest, AddBenchmarkCommentResponse, CreateRewardAgentRequest, CreateRewardAgentResponse, GetRewardAgentRequest, GetRewardAgentResponse, ListRewardAgentsRequest, ListRewardAgentsResponse, UpdateRewardAgentRequest, UpdateRewardAgentResponse, StreamBenchmarkRunRequest } from '$gen/agent_platform/service/v1/benchmark_service_pb.js';
import { CreateBenchmarkRunRequestSchema, GetBenchmarkRunRequestSchema, ListBenchmarkRunsRequestSchema, CompareBenchmarksRequestSchema, AddBenchmarkCommentRequestSchema, CreateRewardAgentRequestSchema, GetRewardAgentRequestSchema, ListRewardAgentsRequestSchema, UpdateRewardAgentRequestSchema, StreamBenchmarkRunRequestSchema } from '$gen/agent_platform/service/v1/benchmark_service_pb.js';
import type { Pagination } from '$gen/agent_platform/common/v1/types_pb.js';
import type { RewardAgent, RewardAgentUpdate } from '$gen/agent_platform/reward/v1/reward_pb.js';

export async function createBenchmarkRun(agentId: string, promptDatasetId: string, config?: BenchmarkConfig): Promise<CreateBenchmarkRunResponse> {
	const request = create(CreateBenchmarkRunRequestSchema, { agentId, promptDatasetId, config });
	return await benchmarkClient.createBenchmarkRun(request);
}

export async function getBenchmarkRun(benchmarkRunId: string): Promise<GetBenchmarkRunResponse> {
	const request = create(GetBenchmarkRunRequestSchema, { benchmarkRunId });
	return await benchmarkClient.getBenchmarkRun(request);
}

export async function listBenchmarkRuns(agentId: string, pagination?: Pagination): Promise<ListBenchmarkRunsResponse> {
	const request = create(ListBenchmarkRunsRequestSchema, { agentId, pagination });
	return await benchmarkClient.listBenchmarkRuns(request);
}

export async function* streamBenchmarkRun(benchmarkRunId: string): AsyncGenerator<import('$gen/agent_platform/service/v1/benchmark_service_pb.js').StreamBenchmarkRunResponse> {
	const request = create(StreamBenchmarkRunRequestSchema, { benchmarkRunId });
	for await (const response of benchmarkClient.streamBenchmarkRun(request)) {
		yield response;
	}
}

export async function compareBenchmarks(benchmarkRunIds: string[]): Promise<CompareBenchmarksResponse> {
	const request = create(CompareBenchmarksRequestSchema, { benchmarkRunIds });
	return await benchmarkClient.compareBenchmarks(request);
}

export async function addBenchmarkComment(benchmarkRunId: string, rowId: string, content: string): Promise<AddBenchmarkCommentResponse> {
	const request = create(AddBenchmarkCommentRequestSchema, { benchmarkRunId, rowId, content });
	return await benchmarkClient.addBenchmarkComment(request);
}

export async function createRewardAgent(rewardAgent: RewardAgent): Promise<CreateRewardAgentResponse> {
	const request = create(CreateRewardAgentRequestSchema, { rewardAgent });
	return await benchmarkClient.createRewardAgent(request);
}

export async function getRewardAgent(rewardAgentId: string): Promise<GetRewardAgentResponse> {
	const request = create(GetRewardAgentRequestSchema, { rewardAgentId });
	return await benchmarkClient.getRewardAgent(request);
}

export async function listRewardAgents(pagination?: Pagination): Promise<ListRewardAgentsResponse> {
	const request = create(ListRewardAgentsRequestSchema, { pagination });
	return await benchmarkClient.listRewardAgents(request);
}

export async function updateRewardAgent(update: RewardAgentUpdate): Promise<UpdateRewardAgentResponse> {
	const request = create(UpdateRewardAgentRequestSchema, { update });
	return await benchmarkClient.updateRewardAgent(request);
}

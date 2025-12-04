import { create } from '@bufbuild/protobuf';
import { toolClient } from './clients/tool';
import type { Tool } from '$gen/agent_platform/tool/v1/tool_pb.js';
import type { CreateToolRequest, CreateToolResponse, GetToolRequest, GetToolResponse, ListToolsRequest, ListToolsResponse, UpdateToolRequest, UpdateToolResponse, DeleteToolRequest } from '$gen/agent_platform/service/v1/tool_service_pb.js';
import { CreateToolRequestSchema, GetToolRequestSchema, ListToolsRequestSchema, UpdateToolRequestSchema, DeleteToolRequestSchema } from '$gen/agent_platform/service/v1/tool_service_pb.js';
import type { Pagination } from '$gen/agent_platform/common/v1/types_pb.js';

export async function createTool(tool: Tool): Promise<CreateToolResponse> {
	const request = create(CreateToolRequestSchema, { tool });
	return await toolClient.createTool(request);
}

export async function getTool(toolId: string): Promise<GetToolResponse> {
	const request = create(GetToolRequestSchema, { toolId });
	return await toolClient.getTool(request);
}

export async function listTools(pagination?: Pagination): Promise<ListToolsResponse> {
	const request = create(ListToolsRequestSchema, { pagination });
	return await toolClient.listTools(request);
}

export async function updateTool(tool: Tool): Promise<UpdateToolResponse> {
	const request = create(UpdateToolRequestSchema, { tool });
	return await toolClient.updateTool(request);
}

export async function deleteTool(toolId: string): Promise<void> {
	const request = create(DeleteToolRequestSchema, { toolId });
	await toolClient.deleteTool(request);
}

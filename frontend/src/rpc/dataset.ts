import { create } from '@bufbuild/protobuf';
import { datasetClient } from './clients/dataset';
import type { PromptDatasetRow } from '$gen/agent_platform/dataset/v1/prompt_dataset_pb.js';
import type { CreateDatasetRequest, CreateDatasetResponse, GetDatasetRequest, GetDatasetResponse, ListDatasetsRequest, ListDatasetsResponse, DeleteDatasetRequest, CreatePromptDatasetRequest, CreatePromptDatasetResponse, GetPromptDatasetRequest, GetPromptDatasetResponse, ListPromptDatasetsRequest, ListPromptDatasetsResponse, UpdatePromptDatasetRowRequest, UpdatePromptDatasetRowResponse, AddSMECommentRequest, AddSMECommentResponse } from '$gen/agent_platform/service/v1/dataset_service_pb.js';
import { CreateDatasetRequestSchema, GetDatasetRequestSchema, ListDatasetsRequestSchema, DeleteDatasetRequestSchema, CreatePromptDatasetRequestSchema, GetPromptDatasetRequestSchema, ListPromptDatasetsRequestSchema, UpdatePromptDatasetRowRequestSchema, AddSMECommentRequestSchema } from '$gen/agent_platform/service/v1/dataset_service_pb.js';
import type { Pagination } from '$gen/agent_platform/common/v1/types_pb.js';

export async function createDataset(name: string): Promise<CreateDatasetResponse> {
	const request = create(CreateDatasetRequestSchema, { name });
	return await datasetClient.createDataset(request);
}

export async function getDataset(datasetId: string): Promise<GetDatasetResponse> {
	const request = create(GetDatasetRequestSchema, { datasetId });
	return await datasetClient.getDataset(request);
}

export async function listDatasets(pagination?: Pagination): Promise<ListDatasetsResponse> {
	const request = create(ListDatasetsRequestSchema, { pagination });
	return await datasetClient.listDatasets(request);
}

export async function deleteDataset(datasetId: string): Promise<void> {
	const request = create(DeleteDatasetRequestSchema, { datasetId });
	await datasetClient.deleteDataset(request);
}

export async function createPromptDataset(name: string, rows: PromptDatasetRow[]): Promise<CreatePromptDatasetResponse> {
	const request = create(CreatePromptDatasetRequestSchema, { name, rows });
	return await datasetClient.createPromptDataset(request);
}

export async function getPromptDataset(promptDatasetId: string): Promise<GetPromptDatasetResponse> {
	const request = create(GetPromptDatasetRequestSchema, { promptDatasetId });
	return await datasetClient.getPromptDataset(request);
}

export async function listPromptDatasets(pagination?: Pagination): Promise<ListPromptDatasetsResponse> {
	const request = create(ListPromptDatasetsRequestSchema, { pagination });
	return await datasetClient.listPromptDatasets(request);
}

export async function updatePromptDatasetRow(promptDatasetId: string, row: PromptDatasetRow): Promise<UpdatePromptDatasetRowResponse> {
	const request = create(UpdatePromptDatasetRowRequestSchema, { promptDatasetId, row });
	return await datasetClient.updatePromptDatasetRow(request);
}

export async function addSMEComment(promptDatasetId: string, rowId: string, content: string): Promise<AddSMECommentResponse> {
	const request = create(AddSMECommentRequestSchema, { promptDatasetId, rowId, content });
	return await datasetClient.addSMEComment(request);
}

import { create } from '@bufbuild/protobuf';
import { trajectoryClient } from './clients/trajectory';
import type { TrajectoryFilter, TrajectoryLabel, StepLabel } from '$gen/agent_platform/trajectory/v1/trajectory_pb.js';
import type { GetTrajectoryRequest, GetTrajectoryResponse, ListTrajectoriesRequest, ListTrajectoriesResponse, AnnotateTrajectoryRequest, AnnotateTrajectoryResponse, AnnotateStepRequest, AnnotateStepResponse, ExportTrajectoriesRequest } from '$gen/agent_platform/service/v1/trajectory_service_pb.js';
import { GetTrajectoryRequestSchema, ListTrajectoriesRequestSchema, AnnotateTrajectoryRequestSchema, AnnotateStepRequestSchema, ExportTrajectoriesRequestSchema } from '$gen/agent_platform/service/v1/trajectory_service_pb.js';
import type { Pagination } from '$gen/agent_platform/common/v1/types_pb.js';

export async function getTrajectory(trajectoryId: string): Promise<GetTrajectoryResponse> {
	const request = create(GetTrajectoryRequestSchema, { trajectoryId });
	return await trajectoryClient.getTrajectory(request);
}

export async function listTrajectories(filter?: TrajectoryFilter, pagination?: Pagination): Promise<ListTrajectoriesResponse> {
	const request = create(ListTrajectoriesRequestSchema, { filter, pagination });
	return await trajectoryClient.listTrajectories(request);
}

export async function annotateTrajectory(trajectoryId: string, label: TrajectoryLabel, notes: string): Promise<AnnotateTrajectoryResponse> {
	const request = create(AnnotateTrajectoryRequestSchema, { trajectoryId, label, notes });
	return await trajectoryClient.annotateTrajectory(request);
}

export async function annotateStep(trajectoryId: string, blockId: string, label: StepLabel, feedback: string): Promise<AnnotateStepResponse> {
	const request = create(AnnotateStepRequestSchema, { trajectoryId, blockId, label, feedback });
	return await trajectoryClient.annotateStep(request);
}

export async function* exportTrajectories(filter?: TrajectoryFilter, format?: number): AsyncGenerator<Uint8Array> {
	const request = create(ExportTrajectoriesRequestSchema, { filter, format });
	for await (const response of trajectoryClient.exportTrajectories(request)) {
		yield response.data;
	}
}

import { createClient } from '@connectrpc/connect';
import { TrajectoryService } from '$gen/agent_platform/service/v1/trajectory_service_pb.js';
import { transport } from '../transport';

export const trajectoryClient = createClient(TrajectoryService, transport);


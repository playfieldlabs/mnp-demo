import { createClient } from '@connectrpc/connect';
import { DatasetService } from '$gen/agent_platform/service/v1/dataset_service_pb.js';
import { transport } from '../transport';

export const datasetClient = createClient(DatasetService, transport);


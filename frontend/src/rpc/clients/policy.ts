import { createClient } from '@connectrpc/connect';
import { PolicyService } from '$gen/agent_platform/service/v1/policy_service_pb.js';
import { transport } from '../transport';

export const policyClient = createClient(PolicyService, transport);


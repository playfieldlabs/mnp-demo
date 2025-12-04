import { createClient } from '@connectrpc/connect';
import { AgentService } from '$gen/agent_platform/service/v1/agent_service_pb.js';
import { transport } from '../transport';

export const agentClient = createClient(AgentService, transport);


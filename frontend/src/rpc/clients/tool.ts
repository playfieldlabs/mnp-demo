import { createClient } from '@connectrpc/connect';
import { ToolService } from '$gen/agent_platform/service/v1/tool_service_pb.js';
import { transport } from '../transport';

export const toolClient = createClient(ToolService, transport);


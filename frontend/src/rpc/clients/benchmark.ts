import { createClient } from '@connectrpc/connect';
import { BenchmarkService } from '$gen/agent_platform/service/v1/benchmark_service_pb.js';
import { transport } from '../transport';

export const benchmarkClient = createClient(BenchmarkService, transport);


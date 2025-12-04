import { createConnectTransport } from '@connectrpc/connect-web';
import { getRpcBaseUrl } from '$config/rpc';

export const transport = createConnectTransport({
	baseUrl: getRpcBaseUrl(),
	useBinaryFormat: false
});


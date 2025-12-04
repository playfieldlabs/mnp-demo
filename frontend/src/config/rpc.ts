export function getRpcBaseUrl(): string {
	const envUrl = import.meta.env?.VITE_API_BASE_URL;
	if (typeof envUrl !== 'string' || envUrl.length === 0) {
		throw new Error('VITE_API_BASE_URL environment variable is required');
	}
	return envUrl.replace(/\/$/, '');
}

export const RPC_TIMEOUT_MS = 30_000;


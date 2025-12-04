import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => ({
	agentId: params.agentId
});


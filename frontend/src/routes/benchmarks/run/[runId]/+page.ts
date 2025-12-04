import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => ({
	runId: params.runId
});


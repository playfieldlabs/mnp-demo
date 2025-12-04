import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url }) => {
	return {
		agentId: url.searchParams.get('agentId')
	};
};


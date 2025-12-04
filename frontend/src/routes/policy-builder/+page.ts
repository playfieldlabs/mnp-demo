import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url }) => {
	const policyId = url.searchParams.get('policyId');
	return {
		policyId: policyId || null
	};
};


import { derived, get, writable } from 'svelte/store';
import type { RewardAgent } from '$gen/agent_platform/reward/v1/reward_pb.js';
import * as rewardRpc from '$rpc/reward';

type LoadStatus = 'idle' | 'loading' | 'success' | 'error';

interface RewardStoreState {
	rewardAgents: RewardAgent[];
	status: LoadStatus;
	error?: string;
}

const initialState: RewardStoreState = {
	rewardAgents: [],
	status: 'idle'
};

function createRewardStore() {
	const store = writable<RewardStoreState>(initialState);

	const agentsById = derived(store, ($state) => {
		const map = new Map<string, RewardAgent>();
		$state.rewardAgents.forEach((agent) => {
			const id = agent.agent?.id || '';
			if (id) map.set(id, agent);
		});
		return map;
	});

	async function loadRewardAgents(force = false) {
		const value = get(store);
		if (!force && value.status === 'success' && value.rewardAgents.length > 0) return;

		store.update((prev) => ({ ...prev, status: 'loading', error: undefined }));
		try {
			const response = await rewardRpc.listRewardAgents();
			store.update((prev) => ({ ...prev, rewardAgents: response.rewardAgents || [], status: 'success' }));
		} catch (error) {
			console.error(error);
			store.update((prev) => ({
				...prev,
				status: 'error',
				error: error instanceof Error ? error.message : 'Failed to load reward agents'
			}));
		}
	}

	return {
		subscribe: store.subscribe,
		agentsById,
		loadRewardAgents
	};
}

export const rewardStore = createRewardStore();

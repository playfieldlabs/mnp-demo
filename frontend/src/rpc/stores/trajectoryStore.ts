import { create } from '@bufbuild/protobuf';
import { derived, get, writable } from 'svelte/store';
import type { Trajectory, TrajectoryFilter } from '$gen/agent_platform/trajectory/v1/trajectory_pb.js';
import { TrajectoryFilterSchema } from '$gen/agent_platform/trajectory/v1/trajectory_pb.js';
import * as trajectoryRpc from '$rpc/trajectory';

type LoadStatus = 'idle' | 'loading' | 'success' | 'error';

interface TrajectoryStoreState {
	trajectories: Map<string, Trajectory>;
	status: LoadStatus;
	error?: string;
	lastRunId?: string;
}

const initialState: TrajectoryStoreState = {
	trajectories: new Map(),
	status: 'idle'
};

function createTrajectoryStore() {
	const store = writable<TrajectoryStoreState>(initialState);

	const trajectoriesList = derived(store, ($state) => Array.from($state.trajectories.values()));

	async function loadForRun(runId: string, agentId?: string) {
		store.update((prev) => ({ ...prev, status: 'loading', error: undefined, lastRunId: runId }));
		try {
			const filter = create(TrajectoryFilterSchema, agentId ? { agentIds: [agentId] } : {});
			const response = await trajectoryRpc.listTrajectories(filter);
			store.update((prev) => ({
				...prev,
				status: 'success',
				trajectories: new Map((response.trajectories || []).map((t) => [t.id, t]))
			}));
		} catch (error) {
			console.error(error);
			store.update((prev) => ({
				...prev,
				status: 'error',
				error: error instanceof Error ? error.message : 'Failed to load trajectories'
			}));
		}
	}

	function getByAgentRun(agentRunId: string) {
		const state = get(store);
		for (const trajectory of state.trajectories.values()) {
			if (trajectory.agentRun?.id === agentRunId) {
				return trajectory;
			}
		}
		return null;
	}

	return {
		subscribe: store.subscribe,
		trajectoriesList,
		loadForRun,
		getByAgentRun
	};
}

export const trajectoryStore = createTrajectoryStore();

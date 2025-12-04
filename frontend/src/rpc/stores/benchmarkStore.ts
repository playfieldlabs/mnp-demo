import { derived, get, writable } from 'svelte/store';
import type { BenchmarkRun, BenchmarkConfig } from '$gen/agent_platform/benchmark/v1/benchmark_pb.js';
import * as benchmarkRpc from '$rpc/benchmark';

type LoadStatus = 'idle' | 'loading' | 'success' | 'error';

interface BenchmarkStoreState {
	runs: Map<string, BenchmarkRun>;
	listStatus: LoadStatus;
	error?: string;
	selectedRunId?: string;
}

const initialState: BenchmarkStoreState = {
	runs: new Map(),
	listStatus: 'idle'
};

function createBenchmarkStore() {
	const store = writable<BenchmarkStoreState>(initialState);

	const runsList = derived(store, ($state) =>
		Array.from($state.runs.values()).sort((a, b) => {
			const aTime = a.startedAt ? (typeof a.startedAt === 'string' ? new Date(a.startedAt).getTime() : Number(a.startedAt.seconds) * 1000) : 0;
			const bTime = b.startedAt ? (typeof b.startedAt === 'string' ? new Date(b.startedAt).getTime() : Number(b.startedAt.seconds) * 1000) : 0;
			return bTime - aTime;
		})
	);

	const selectedRun = derived(store, ($state) => {
		if (!$state.selectedRunId) return null;
		return $state.runs.get($state.selectedRunId) ?? null;
	});

	async function loadRuns(agentId: string) {
		store.update((prev) => ({ ...prev, listStatus: 'loading', error: undefined }));
		try {
			const response = await benchmarkRpc.listBenchmarkRuns(agentId);
			store.update((prev) => {
				const runs = new Map(prev.runs);
				(response.benchmarkRuns || []).forEach((run) => runs.set(run.id, run));
				return {
					...prev,
					listStatus: 'success',
					runs
				};
			});
		} catch (error) {
			console.error(error);
			store.update((prev) => ({
				...prev,
				listStatus: 'error',
				error: error instanceof Error ? error.message : 'Failed to load benchmark runs'
			}));
		}
	}

	async function loadRun(benchmarkRunId: string) {
		const state = get(store);
		if (state.runs.has(benchmarkRunId)) {
			store.update((prev) => ({ ...prev, selectedRunId: benchmarkRunId }));
			return;
		}

		try {
			const response = await benchmarkRpc.getBenchmarkRun(benchmarkRunId);
			if (response.benchmarkRun) {
				store.update((prev) => {
					const runs = new Map(prev.runs);
					runs.set(response.benchmarkRun!.id, response.benchmarkRun!);
					return { ...prev, runs, selectedRunId: response.benchmarkRun!.id };
				});
			}
		} catch (error) {
			console.error(error);
			store.update((prev) => ({
				...prev,
				error: error instanceof Error ? error.message : 'Failed to load benchmark run'
			}));
		}
	}

	function selectRun(runId?: string) {
		store.update((prev) => ({ ...prev, selectedRunId: runId }));
	}

	async function createRun(params: {
		agentId: string;
		promptDatasetId: string;
		config?: BenchmarkConfig;
	}) {
		const response = await benchmarkRpc.createBenchmarkRun(
			params.agentId,
			params.promptDatasetId,
			params.config
		);

		if (response.benchmarkRun) {
			store.update((prev) => {
				const runs = new Map(prev.runs);
				runs.set(response.benchmarkRun!.id, response.benchmarkRun!);
				return { ...prev, runs, selectedRunId: response.benchmarkRun!.id };
			});

			return response.benchmarkRun;
		}
	}

	return {
		subscribe: store.subscribe,
		runsList,
		selectedRun,
		loadRuns,
		loadRun,
		selectRun,
		createRun
	};
}

export const benchmarkStore = createBenchmarkStore();

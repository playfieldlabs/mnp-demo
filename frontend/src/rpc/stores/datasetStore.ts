import { derived, get, writable } from 'svelte/store';
import type { PromptDataset } from '$gen/agent_platform/dataset/v1/prompt_dataset_pb.js';
import * as datasetRpc from '$rpc/dataset';

type LoadStatus = 'idle' | 'loading' | 'success' | 'error';

interface DatasetStoreState {
	promptDatasets: Map<string, PromptDataset>;
	status: LoadStatus;
	error?: string;
}

const initialState: DatasetStoreState = {
	promptDatasets: new Map(),
	status: 'idle'
};

function createDatasetStore() {
	const store = writable<DatasetStoreState>(initialState);

	const promptDatasets = derived(store, ($state) =>
		Array.from($state.promptDatasets.values()).sort((a, b) => a.name.localeCompare(b.name))
	);

	async function loadPromptDatasets(force = false) {
		const state = get(store);
		if (!force && state.status === 'success' && state.promptDatasets.size > 0) return;

		store.update((prev) => ({ ...prev, status: 'loading', error: undefined }));
		try {
			const response = await datasetRpc.listPromptDatasets();
			store.update((prev) => ({
				...prev,
				status: 'success',
				promptDatasets: new Map((response.promptDatasets || []).map((dataset) => [dataset.id, dataset]))
			}));
		} catch (error) {
			console.error(error);
			store.update((prev) => ({
				...prev,
				status: 'error',
				error: error instanceof Error ? error.message : 'Failed to load prompt datasets'
			}));
		}
	}

	async function loadPromptDataset(promptDatasetId: string, options: { force?: boolean } = {}) {
		const { force = false } = options;
		const state = get(store);
		if (!force && state.promptDatasets.has(promptDatasetId)) return;

		try {
			const response = await datasetRpc.getPromptDataset(promptDatasetId);
			if (response.promptDataset) {
				store.update((prev) => {
					const promptDatasets = new Map(prev.promptDatasets);
					promptDatasets.set(response.promptDataset!.id, response.promptDataset!);
					return { ...prev, promptDatasets };
				});
			}
		} catch (error) {
			console.error(error);
			store.update((prev) => ({
				...prev,
				error: error instanceof Error ? error.message : 'Failed to load prompt dataset'
			}));
		}
	}

	return {
		subscribe: store.subscribe,
		promptDatasets,
		loadPromptDatasets,
		loadPromptDataset
	};
}

export const datasetStore = createDatasetStore();

import { derived, get, writable } from 'svelte/store';
import type { Tool } from '$gen/agent_platform/tool/v1/tool_pb.js';
import * as toolRpc from '$rpc/tool';

type LoadStatus = 'idle' | 'loading' | 'success' | 'error';

interface ToolStoreState {
	tools: Tool[];
	toolsStatus: LoadStatus;
	toolError?: string;
}

const initialState: ToolStoreState = {
	tools: [],
	toolsStatus: 'idle'
};

function createToolStore() {
	const store = writable<ToolStoreState>(initialState);

	const sortedTools = derived(store, ($state) =>
		[...$state.tools].sort((a, b) => a.name.localeCompare(b.name))
	);

	async function loadTools(force = false) {
		const value = get(store);
		if (!force && value.toolsStatus === 'success' && value.tools.length > 0) return;

		store.update((prev) => ({ ...prev, toolsStatus: 'loading', toolError: undefined }));
		try {
			const response = await toolRpc.listTools();
			store.update((prev) => ({ ...prev, tools: response.tools || [], toolsStatus: 'success' }));
		} catch (error) {
			console.error(error);
			store.update((prev) => ({
				...prev,
				toolsStatus: 'error',
				toolError: error instanceof Error ? error.message : 'Failed to load tools'
			}));
		}
	}

	return {
		subscribe: store.subscribe,
		tools: sortedTools,
		loadTools
	};
}

export const toolStore = createToolStore();

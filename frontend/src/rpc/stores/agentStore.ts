import { create } from '@bufbuild/protobuf';
import { derived, get, writable } from 'svelte/store';
import type { Agent, AgentConfig } from '$gen/agent_platform/agent/v1/agent_pb.js';
import { AgentSchema, AgentConfigSchema } from '$gen/agent_platform/agent/v1/agent_pb.js';
import * as agentRpc from '$rpc/agent';

type LoadStatus = 'idle' | 'loading' | 'success' | 'error';

interface AgentStoreState {
	agents: Map<string, Agent>;
	listStatus: LoadStatus;
	error?: string;
	activeAgentId?: string;
	saveStatus: LoadStatus;
}

const initialState: AgentStoreState = {
	agents: new Map(),
	listStatus: 'idle',
	saveStatus: 'idle'
};

function createAgentStore() {
	const store = writable<AgentStoreState>(initialState);

	const agentsList = derived(store, ($state) =>
		Array.from($state.agents.values()).sort((a, b) => a.name.localeCompare(b.name))
	);

	const activeAgent = derived(store, ($state) => {
		if (!$state.activeAgentId) return null;
		return $state.agents.get($state.activeAgentId) ?? null;
	});

	async function loadAgents(force = false) {
		const value = get(store);
		if (!force && value.listStatus === 'success' && value.agents.size > 0) {
			return;
		}

		store.update((prev) => ({ ...prev, listStatus: 'loading', error: undefined }));
		try {
			const response = await agentRpc.listAgents();
			store.update((prev) => ({
				...prev,
				listStatus: 'success',
				agents: new Map((response.agents || []).map((agent) => [agent.id, agent]))
			}));
		} catch (error) {
			console.error(error);
			store.update((prev) => ({
				...prev,
				listStatus: 'error',
				error: error instanceof Error ? error.message : 'Failed to load agents'
			}));
		}
	}

	async function loadAgent(agentId: string, options: { force?: boolean } = {}) {
		const { force = false } = options;
		const value = get(store);
		if (!force && value.agents.has(agentId)) {
			store.update((prev) => ({ ...prev, activeAgentId: agentId }));
			return;
		}

		try {
			const response = await agentRpc.getAgent(agentId);
			if (response.agent) {
				store.update((prev) => {
					const agents = new Map(prev.agents);
					agents.set(response.agent!.id, response.agent!);
					return { ...prev, agents, activeAgentId: response.agent!.id };
				});
			}
		} catch (error) {
			console.error(error);
			store.update((prev) => ({
				...prev,
				error: error instanceof Error ? error.message : 'Failed to load agent'
			}));
		}
	}

	function setActiveAgent(agentId?: string) {
		store.update((prev) => ({ ...prev, activeAgentId: agentId }));
	}

	async function saveAgent(agent: { id?: string; name: string; task: string; systemPrompt: string; toolIds?: string[]; policyAgentIds?: string[]; config?: { model: string; temperature: number; maxTokens: number; maxToolCalls: number } }) {
		store.update((prev) => ({ ...prev, saveStatus: 'loading', error: undefined }));

		try {
			const agentMessage = create(AgentSchema, {
				...agent,
				id: agent.id || '',
				toolIds: agent.toolIds || [],
				policyAgentIds: agent.policyAgentIds || [],
				config: agent.config ? create(AgentConfigSchema, agent.config) : undefined
			});
			const response = agent.id && agent.id.length > 0
				? await agentRpc.updateAgent(agentMessage)
				: await agentRpc.createAgent(agentMessage);

			if (response.agent) {
				store.update((prev) => {
					const agents = new Map(prev.agents);
					agents.set(response.agent!.id, response.agent!);
					return {
						...prev,
						saveStatus: 'success',
						activeAgentId: response.agent!.id,
						agents
					};
				});

				return response.agent;
			}
		} catch (error) {
			console.error(error);
			store.update((prev) => ({
				...prev,
				saveStatus: 'error',
				error: error instanceof Error ? error.message : 'Unable to save agent'
			}));
			throw error;
		}
	}

	return {
		subscribe: store.subscribe,
		agentsList,
		activeAgent,
		loadAgents,
		loadAgent,
		setActiveAgent,
		saveAgent
	};
}

export const agentStore = createAgentStore();

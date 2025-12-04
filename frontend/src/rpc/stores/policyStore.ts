import { derived, get, writable } from 'svelte/store';
import * as policyRpc from '../policy';
import type { PolicyAgent, PolicyTool } from '$gen/agent_platform/policy/v1/policy_pb.js';
import { create } from '@bufbuild/protobuf';
import { PolicyAgentSchema, PolicyToolSchema } from '$gen/agent_platform/policy/v1/policy_pb.js';

type LoadStatus = 'idle' | 'loading' | 'success' | 'error';

interface PolicyStoreState {
	policies: Map<string, PolicyAgent>;
	listStatus: LoadStatus;
	error?: string;
	activePolicyId?: string;
	saveStatus: LoadStatus;
}

const initialState: PolicyStoreState = {
	policies: new Map(),
	listStatus: 'idle',
	saveStatus: 'idle'
};

function createPolicyStore() {
	const store = writable<PolicyStoreState>(initialState);

	const policiesList = derived(store, ($state) =>
		Array.from($state.policies.values()).sort((a, b) => a.name.localeCompare(b.name))
	);

	const activePolicy = derived(store, ($state) => {
		if (!$state.activePolicyId) return null;
		return $state.policies.get($state.activePolicyId) ?? null;
	});

	async function loadPolicies(force = false) {
		const value = get(store);
		if (!force && value.listStatus === 'success' && value.policies.size > 0) {
			return;
		}

		store.update((prev) => ({ ...prev, listStatus: 'loading', error: undefined }));
		try {
			const response = await policyRpc.listPolicyAgents();
			store.update((prev) => ({
				...prev,
				listStatus: 'success',
				policies: new Map((response.policyAgents || []).map((policy) => [policy.id, policy]))
			}));
		} catch (error) {
			console.error(error);
			store.update((prev) => ({
				...prev,
				listStatus: 'error',
				error: error instanceof Error ? error.message : 'Failed to load policies'
			}));
		}
	}

	async function loadPolicy(policyId: string, options: { force?: boolean } = {}) {
		const { force = false } = options;
		const value = get(store);
		if (!force && value.policies.has(policyId)) {
			store.update((prev) => ({ ...prev, activePolicyId: policyId }));
			return;
		}

		try {
			const response = await policyRpc.getPolicyAgent(policyId);
			if (response.policyAgent) {
				store.update((prev) => {
					const policies = new Map(prev.policies);
					policies.set(response.policyAgent!.id, response.policyAgent!);
					return { ...prev, policies, activePolicyId: response.policyAgent!.id };
				});
			}
		} catch (error) {
			console.error(error);
			store.update((prev) => ({
				...prev,
				error: error instanceof Error ? error.message : 'Failed to load policy'
			}));
		}
	}

	function setActivePolicy(policyId?: string) {
		store.update((prev) => ({ ...prev, activePolicyId: policyId }));
	}

	async function savePolicy(policy: {
		id?: string;
		name: string;
		systemPrompt: string;
		dataSourceIds?: string[];
		externalSourceConfig?: Record<string, any>;
		outputSchema?: Record<string, any>;
		updateSchedule?: string;
		policyTool?: { tool?: any; policyContent?: string };
	}) {
		store.update((prev) => ({ ...prev, saveStatus: 'loading', error: undefined }));

		try {
			const policyAgent = create(PolicyAgentSchema, {
				id: policy.id || '',
				name: policy.name,
				systemPrompt: policy.systemPrompt,
				dataSourceIds: policy.dataSourceIds || [],
				externalSourceConfig: policy.externalSourceConfig,
				outputSchema: policy.outputSchema,
				updateSchedule: policy.updateSchedule || '',
				policyTool: policy.policyTool ? create(PolicyToolSchema, policy.policyTool) : undefined
			});

			const response = policy.id && policy.id.length > 0
				? await policyRpc.updatePolicyAgent(policyAgent)
				: await policyRpc.createPolicyAgent(policyAgent);

			if (response.policyAgent) {
				store.update((prev) => {
					const policies = new Map(prev.policies);
					policies.set(response.policyAgent!.id, response.policyAgent!);
					return {
						...prev,
						saveStatus: 'success',
						activePolicyId: response.policyAgent!.id,
						policies
					};
				});
			}

			return response.policyAgent;
		} catch (error) {
			console.error(error);
			store.update((prev) => ({
				...prev,
				saveStatus: 'error',
				error: error instanceof Error ? error.message : 'Unable to save policy'
			}));
			throw error;
		}
	}

	async function runPolicy(policyId: string) {
		try {
			const response = await policyRpc.runPolicyAgent(policyId);
			if (response.policyRun) {
				await loadPolicy(policyId, { force: true });
			}
			return response.policyRun;
		} catch (error) {
			console.error(error);
			store.update((prev) => ({
				...prev,
				error: error instanceof Error ? error.message : 'Failed to run policy'
			}));
			throw error;
		}
	}

	async function deletePolicy(policyId: string) {
		try {
			await policyRpc.deletePolicyAgent(policyId);
			store.update((prev) => {
				const policies = new Map(prev.policies);
				policies.delete(policyId);
				if (prev.activePolicyId === policyId) {
					return { ...prev, policies, activePolicyId: undefined };
				}
				return { ...prev, policies };
			});
		} catch (error) {
			console.error(error);
			store.update((prev) => ({
				...prev,
				error: error instanceof Error ? error.message : 'Failed to delete policy'
			}));
			throw error;
		}
	}

	return {
		subscribe: store.subscribe,
		policiesList,
		activePolicy,
		loadPolicies,
		loadPolicy,
		setActivePolicy,
		savePolicy,
		deletePolicy,
		runPolicy
	};
}

export const policyStore = createPolicyStore();


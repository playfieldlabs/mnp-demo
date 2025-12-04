<script lang="ts">
	import type { PolicyAgent } from '$gen/agent_platform/policy/v1/policy_pb.js';
	import { createEventDispatcher } from 'svelte';

	export let policies: PolicyAgent[] = [];
	export let selectedId = '';
	export let disabled = false;

	const dispatch = createEventDispatcher<{ change: string }>();

let currentPolicy: PolicyAgent | null = null;

$: currentPolicy = policies.find((policy) => policy.id === selectedId) ?? null;

	function handleChange(event: Event) {
		selectedId = (event.target as HTMLSelectElement).value;
		dispatch('change', selectedId);
	}
</script>

<div class="policy-selector">
	<div class="policy-selector__header">
		<div>
			<h3>Policy</h3>
			<p>Choose the guardrail agent that evaluates this builder.</p>
		</div>
		<select bind:value={selectedId} on:change={handleChange} disabled={disabled}>
			<option value="">No policy</option>
			{#each policies as policy}
				<option value={policy.id}>{policy.name}</option>
			{/each}
		</select>
	</div>
	{#if currentPolicy}
		<div class="policy-card">
			<h4>{currentPolicy.name}</h4>
			<p>{currentPolicy.systemPrompt}</p>
			{#if currentPolicy.policyTool?.tool}
				<small>
					Evaluated via {currentPolicy.policyTool.tool.name} ·
					{currentPolicy.policyTool.policyContent}
				</small>
			{/if}
		</div>
	{:else}
		<p class="empty">Agent output will not go through policy QA.</p>
	{/if}
</div>

<style>
	.policy-selector {
		display: flex;
		flex-direction: column;
		gap: 0.8rem;
	}

	.policy-selector__header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
	}

	select {
		border: 1px solid var(--border-strong);
		border-radius: 2px;
		padding: 0.4rem 0.6rem;
		background: var(--surface-1);
		color: var(--text-primary);
		font-size: 0.95rem;
	}

	.policy-card {
		border: 1px solid var(--border-strong);
		background: var(--surface-1);
		border-radius: 2px;
		padding: 0.9rem;
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}

	.policy-card h4 {
		margin: 0;
	}

	.policy-card p {
		margin: 0;
		color: var(--text-muted);
	}

	.policy-card small {
		color: var(--text-secondary);
	}

	.empty {
		color: var(--text-muted);
		font-style: italic;
	}
</style>


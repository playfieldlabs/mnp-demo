<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Tool } from '$gen/agent_platform/tool/v1/tool_pb.js';

	export let tools: Tool[] = [];
	export let selectedIds: string[] = [];
	export let disabled = false;
	let search = '';

	const dispatch = createEventDispatcher<{ change: string[] }>();

	$: filteredTools =
		search.length === 0
			? tools
			: tools.filter(
					(tool) =>
						tool.name.toLowerCase().includes(search.toLowerCase()) ||
						(tool.context ?? '').toLowerCase().includes(search.toLowerCase())
				);

	function toggle(toolId: string) {
		if (disabled) return;
		if (selectedIds.includes(toolId)) {
			selectedIds = selectedIds.filter((id: string) => id !== toolId);
		} else {
			selectedIds = [...selectedIds, toolId];
		}
		dispatch('change', selectedIds);
	}
</script>

<div class="tool-selector">
	<div class="tool-selector__header">
		<div>
			<h3>Tools</h3>
			<p>Select which capabilities the agent can call.</p>
		</div>
		<input
			type="search"
			placeholder="Search tools"
			bind:value={search}
			disabled={disabled}
		/>
	</div>
	<div class="tool-list">
		{#if filteredTools.length === 0}
			<p class="empty-state">No tools match your search.</p>
		{:else}
			{#each filteredTools as tool}
				<button
					type="button"
					class:selected={selectedIds.includes(tool.id)}
					class="tool-pill"
					on:click={() => toggle(tool.id)}
					disabled={disabled}
				>
					<strong>{tool.name}</strong>
					<span>{tool.context ?? 'No description yet.'}</span>
				</button>
			{/each}
		{/if}
	</div>
</div>

<style>
	.tool-selector {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.tool-selector__header {
		display: flex;
		gap: 1rem;
		align-items: center;
		justify-content: space-between;
	}

	.tool-selector__header h3 {
		margin: 0;
		font-size: 1rem;
	}

	.tool-selector__header p {
		margin: 0.1rem 0 0;
		color: var(--text-muted);
		font-size: 0.85rem;
	}

	input[type='search'] {
		border: 1px solid var(--border-strong);
		border-radius: 999px;
		padding: 0.4rem 0.9rem;
		font-size: 0.9rem;
		background: var(--surface-1);
		color: var(--text-primary);
		width: 50%;
	}

	.tool-list {
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
		max-height: 320px;
		overflow: auto;
		padding-right: 0.2rem;
	}

	.tool-pill {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		gap: 0.25rem;
		padding: 0.75rem 1rem;
		border-radius: 2px;
		border: 1px solid var(--border-strong);
		background: var(--surface-1);
		text-align: left;
		transition: border-color 0.2s ease, background 0.2s ease;
	}

	.tool-pill.selected {
		border-color: var(--blue-5);
		background: color-mix(in srgb, var(--blue-5) 10%, var(--surface-1));
	}

	.tool-pill strong {
		font-size: 0.95rem;
	}

	.tool-pill span {
		color: var(--text-muted);
		font-size: 0.85rem;
	}

	.empty-state {
		color: var(--text-muted);
		font-style: italic;
	}

	@media (max-width: 900px) {
		.tool-selector__header {
			flex-direction: column;
			align-items: flex-start;
		}

		input[type='search'] {
			width: 100%;
		}
	}
</style>


<script lang="ts">
	import type { Trajectory } from '$gen/agent_platform/trajectory/v1/trajectory_pb.js';
	import { formatRelative, formatScore } from '$utils/format';
	import BlockRenderer from './BlockRenderer.svelte';

	export let trajectory: Trajectory | null;
</script>

{#if trajectory}
	<section class="trajectory-panel">
		<header>
			<div>
				<h3>Trajectory {trajectory.id}</h3>
				<p>
					Agent run {trajectory.agentRun?.id ?? '—'} · {formatRelative(trajectory.createdAt ? (typeof trajectory.createdAt === 'object' ? new Date(Number(trajectory.createdAt.seconds) * 1000) : trajectory.createdAt) : undefined)}
				</p>
			</div>
			{#if trajectory.reward}
				<span class="score">Score {formatScore(trajectory.reward.score)}</span>
			{/if}
		</header>
		<ul>
			<li>
				<strong>Label</strong>
				<span>{trajectory.annotation?.label ?? '—'}</span>
			</li>
			<li>
				<strong>Blocks</strong>
				<span>{trajectory.agentRun?.blocks?.length ?? '—'}</span>
			</li>
			<li>
				<strong>Notes</strong>
				<span>{trajectory.annotation?.notes ?? 'No reviewer notes yet.'}</span>
			</li>
		</ul>
		{#if trajectory.agentRun?.blocks && trajectory.agentRun.blocks.length > 0}
			<div class="blocks">
				{#each trajectory.agentRun.blocks as block}
					<BlockRenderer block={block} />
				{/each}
			</div>
		{/if}
	</section>
{:else}
	<p class="empty">Select a benchmark row to inspect its trajectory.</p>
{/if}

<style>
	.trajectory-panel {
		border: 1px solid var(--border-strong);
		border-radius: 2px;
		padding: 1rem;
		background: var(--surface-1);
	}

	header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 0.8rem;
	}

	header h3 {
		margin: 0;
	}

	header p {
		margin: 0.2rem 0 0;
		color: var(--text-muted);
	}

	.score {
		font-weight: 600;
		color: var(--blue-6);
	}

	ul {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 0.6rem;
	}

	li {
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
	}

	li strong {
		font-size: 0.85rem;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}

	.empty {
		color: var(--text-muted);
		font-style: italic;
	}

	.blocks {
		margin-top: 1.2rem;
		padding-top: 1.2rem;
		border-top: 1px solid var(--border-weak);
	}
</style>


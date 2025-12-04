<script lang="ts">
	import { onMount } from 'svelte';
	import type { PageData } from './$types';
	import { benchmarkStore } from '$stores/benchmarkStore';
	import { datasetStore } from '$stores/datasetStore';
	import { trajectoryStore } from '$stores/trajectoryStore';
	import { agentStore } from '$stores/agentStore';
	import { StatusBadge, MetricCard, TrajectoryPanel } from '$lib';
	import { formatDateTime, formatScore } from '$utils/format';

	export let data: PageData;

	const runStore = benchmarkStore.selectedRun;
	const datasets = datasetStore.promptDatasets;
	const trajectories = trajectoryStore.trajectoriesList;

	let selectedRowId: string | null = null;
	let loadedRunId: string | null = null;

	onMount(() => {
		benchmarkStore.loadRun(data.runId);
		datasetStore.loadPromptDatasets();
		agentStore.loadAgents();
	});

	$: run = $runStore;
	$: if (run && run.id !== loadedRunId) {
		loadedRunId = run.id;
		datasetStore.loadPromptDataset(run.promptDatasetId);
		trajectoryStore.loadForRun(run.id, run.agentId);
		selectedRowId = run.rows[0]?.id ?? null;
	}

	$: selectedRow = run?.rows.find((row) => row.id === selectedRowId) ?? null;
	$: promptDataset = $datasets.find((dataset) => dataset.id === run?.promptDatasetId);
	$: promptRow = promptDataset?.rows.find((row) => row.id === selectedRow?.promptDatasetRowId);

	$: currentTrajectory =
		selectedRow && selectedRow.agentRunIds.length
			? trajectoryStore.getByAgentRun(selectedRow.agentRunIds[0])
			: null;
</script>

{#if !run}
	<p>Loading benchmark run…</p>
{:else}
	<section class="run-detail">
		<header>
			<div>
				<a href="/benchmarks" class="link-back">← Benchmarks</a>
				<h1>Run {run.id}</h1>
				<p>
					Agent {run.agentId} · Dataset {promptDataset?.name ?? run.promptDatasetId}
				</p>
			</div>
			<StatusBadge status={run.status} />
		</header>

		<section class="metrics">
			<MetricCard label="Mean score" value={formatScore(run.finalReward?.meanScore)} caption="Across all rows" />
			<MetricCard label="Std Dev" value={formatScore(run.finalReward?.stdDev)} caption="Score variability" />
			<MetricCard label="Success rate" value={`${run.finalReward?.successfulRuns ?? 0}/${run.finalReward?.totalRuns ?? 0}`} caption="Successful vs total runs" />
			<div class="meta">
				<strong>Timing</strong>
				<span>Started {formatDateTime(run.startedAt)}</span>
				<span>Finished {formatDateTime(run.finishedAt)}</span>
			</div>
		</section>

		<div class="detail-grid">
			<section class="rows card">
				<h2>Rows</h2>
				<table>
					<thead>
						<tr>
							<th>Prompt</th>
							<th>Score</th>
							<th>Status</th>
						</tr>
					</thead>
					<tbody>
						{#each run.rows as row}
							<tr
								class:selected={row.id === selectedRowId}
								on:click={() => (selectedRowId = row.id)}
							>
								<td>{promptDataset?.rows.find((r) => r.id === row.promptDatasetRowId)?.prompt ?? 'Prompt unavailable'}</td>
								<td>{formatScore(row.reward?.score)}</td>
								<td><StatusBadge status={row.status} compact /></td>
							</tr>
						{/each}
					</tbody>
				</table>
			</section>

			<section class="trajectory card">
				<h2>Trajectory</h2>
				<TrajectoryPanel trajectory={currentTrajectory} />
			</section>
		</div>
	</section>
{/if}

<style>
	.run-detail {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
	}

	.link-back {
		color: var(--text-muted);
		font-size: 0.9rem;
	}

	.metrics {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
		gap: 1rem;
	}

	.meta {
		border: 1px solid var(--border-strong);
		border-radius: 2px;
		padding: 0.8rem;
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
		background: var(--surface-1);
	}

	.detail-grid {
		display: grid;
		grid-template-columns: 1.2fr 0.8fr;
		gap: 1.2rem;
	}

	.card {
		border: 1px solid var(--border-strong);
		border-radius: 2px;
		padding: 1rem;
		background: var(--surface-1);
	}

	table {
		width: 100%;
		border-collapse: collapse;
	}

	th,
	td {
		padding: 0.55rem;
		border-bottom: 1px solid var(--border-subtle);
		text-align: left;
	}

	tr.selected {
		background: color-mix(in srgb, var(--blue-5) 12%, transparent);
	}

	@media (max-width: 1000px) {
		.detail-grid {
			grid-template-columns: 1fr;
		}
	}
</style>


<script lang="ts">
	import { onMount } from 'svelte';
	import { agentStore } from '$stores/agentStore';
	import { benchmarkStore } from '$stores/benchmarkStore';
	import { datasetStore } from '$stores/datasetStore';
	import { rewardStore } from '$stores/rewardStore';
	import { MetricCard, StatusBadge, Sparkline } from '$lib';
	import { formatDateTime, formatScore } from '$utils/format';
	import type { BenchmarkRun } from '$gen/agent_platform/benchmark/v1/benchmark_pb.js';
	import { Status } from '$gen/agent_platform/common/v1/types_pb.js';

	const agents = agentStore.agentsList;
	const runsList = benchmarkStore.runsList;
	const datasets = datasetStore.promptDatasets;

	let agentFilter = '';
	let datasetFilter = '';
	let statusFilterStr = '';

	onMount(() => {
		agentStore.loadAgents();
		if (agentFilter) {
			benchmarkStore.loadRuns(agentFilter);
		}
		datasetStore.loadPromptDatasets();
		rewardStore.loadRewardAgents();
	});

	const statusOptions: { label: string; value: Status }[] = [
		{ label: 'Queued', value: Status.AWAITING_START },
		{ label: 'Running', value: Status.RUNNING },
		{ label: 'Done', value: Status.DONE },
		{ label: 'Error', value: Status.ERROR }
	];

	$: datasetMap = new Map($datasets.map((dataset) => [dataset.id, dataset.name]));
	$: agentMap = new Map($agents.map((agent) => [agent.id, agent.name]));

	$: statusFilter = statusFilterStr ? (Status[statusFilterStr as keyof typeof Status] as Status) : null;
	$: filteredRuns = $runsList.filter((run) => {
		if (agentFilter && run.agentId !== agentFilter) return false;
		if (datasetFilter && run.promptDatasetId !== datasetFilter) return false;
		if (statusFilter !== null && run.status !== statusFilter) return false;
		return true;
	});

	$: if (agentFilter) {
		benchmarkStore.loadRuns(agentFilter);
	}

	$: scoreSeries = filteredRuns
		.slice()
		.reverse()
		.slice(0, 10)
		.map((run) => run.finalReward?.meanScore)
		.filter((score): score is number => score !== undefined && score !== null);

	$: completionRate =
		filteredRuns.length === 0
		? 0
		: filteredRuns.filter((run) => run.status === Status.DONE).length / filteredRuns.length;

	$: completedRuns = filteredRuns.filter((run) => run.status === Status.DONE && run.finalReward?.meanScore !== undefined);
	$: avgScore =
		completedRuns.length === 0
			? null
			: completedRuns.reduce(
					(acc, run) => acc + (run.finalReward!.meanScore!),
					0
				) / completedRuns.length;

	$: previousPeriodRuns = filteredRuns.slice(Math.floor(filteredRuns.length / 2));
	$: previousPeriodCompletionRate =
		previousPeriodRuns.length === 0
			? 0
			: previousPeriodRuns.filter((run) => run.status === Status.DONE).length / previousPeriodRuns.length;
	$: completionTrend = completionRate - previousPeriodCompletionRate;

	$: leaderboard = filteredRuns.reduce<Record<string, { count: number; total: number }>>(
		(acc, run) => {
			const score = run.finalReward?.meanScore;
			if (score === undefined) return acc;
			if (!acc[run.agentId]) acc[run.agentId] = { count: 0, total: 0 };
			acc[run.agentId].count += 1;
			acc[run.agentId].total += score;
			return acc;
		},
		{}
	);

	$: leaderEntries = Object.entries(leaderboard)
		.map(([agentId, stats]) => ({
			agentId,
			average: stats.total / stats.count,
			count: stats.count
		}))
		.sort((a, b) => b.average - a.average)
		.slice(0, 3);

	function datasetLabel(run: BenchmarkRun) {
		return datasetMap.get(run.promptDatasetId) ?? run.promptDatasetId;
	}
</script>

<section class="benchmarks">
	<header class="benchmarks__header">
		<div>
			<p class="eyebrow">Benchmarks overview</p>
			<h1>Observe how each agent performs across datasets.</h1>
		</div>
		<div class="filters">
			<label>
				<span>Agent</span>
				<select bind:value={agentFilter}>
					<option value="">All</option>
					{#each $agents as agent}
						<option value={agent.id}>{agent.name}</option>
					{/each}
				</select>
			</label>
			<label>
				<span>Dataset</span>
				<select bind:value={datasetFilter}>
					<option value="">All</option>
					{#each $datasets as dataset}
						<option value={dataset.id}>{dataset.name}</option>
					{/each}
				</select>
			</label>
			<label>
				<span>Status</span>
				<select bind:value={statusFilterStr}>
					<option value="">Any</option>
					<option value="AWAITING_START">Queued</option>
					<option value="RUNNING">Running</option>
					<option value="DONE">Done</option>
					<option value="ERROR">Error</option>
				</select>
			</label>
		</div>
	</header>

	<section class="metrics">
		<MetricCard label="Avg reward" value={avgScore ? formatScore(avgScore) : '—'} caption="Mean score across filtered runs" />
		<MetricCard label="Completion rate" value={`${(completionRate * 100).toFixed(0)}%`} caption="Runs finished vs total" trend={previousPeriodRuns.length > 0 ? completionTrend : undefined} />
		<MetricCard label="Total runs" value={filteredRuns.length} caption="Matching the current filters" />
		<div class="sparkline-card">
			<div>
				<span>Trend</span>
				<strong>Last 10 scores</strong>
			</div>
			<Sparkline values={scoreSeries} />
		</div>
	</section>

	<section class="leaderboard card">
		<h2>Top agents</h2>
		{#if leaderEntries.length === 0}
			<p class="empty">Run a benchmark to populate the leaderboard.</p>
		{:else}
			<ul>
				{#each leaderEntries as entry}
					<li>
						<div>
							<strong>{agentMap.get(entry.agentId) ?? entry.agentId}</strong>
							<span>{entry.count} runs</span>
						</div>
						<span>{formatScore(entry.average)}</span>
					</li>
				{/each}
			</ul>
		{/if}
	</section>

	<section class="runs-table card">
		<div class="table-header">
			<h2>Benchmark runs</h2>
			<small>{filteredRuns.length} results</small>
		</div>
		<table>
			<thead>
				<tr>
					<th>Agent</th>
					<th>Dataset</th>
					<th>Status</th>
					<th>Mean score</th>
					<th>Started</th>
					<th></th>
				</tr>
			</thead>
			<tbody>
				{#if filteredRuns.length === 0}
					<tr>
						<td colspan="6">No runs yet.</td>
					</tr>
				{:else}
					{#each filteredRuns as run}
						<tr>
							<td>{agentMap.get(run.agentId) ?? run.agentId}</td>
							<td>{datasetLabel(run)}</td>
							<td><StatusBadge status={run.status} compact /></td>
							<td>{formatScore(run.finalReward?.meanScore)}</td>
							<td>{formatDateTime(run.startedAt)}</td>
							<td>
								<a href={`/benchmarks/run/${run.id}`} class="ghost-button small">Details</a>
							</td>
						</tr>
					{/each}
				{/if}
			</tbody>
		</table>
	</section>
</section>

<style>
	.benchmarks {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.benchmarks__header {
		display: flex;
		flex-direction: column;
		gap: 1.2rem;
	}

	.filters {
		display: flex;
		gap: 1rem;
		flex-wrap: wrap;
	}

	.filters label {
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
	}

	select {
		border: 1px solid var(--border-strong);
		border-radius: 2px;
		padding: 0.45rem 0.8rem;
		background: var(--surface-1);
		color: var(--text-primary);
	}

	.metrics {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
		gap: 1rem;
	}

	.sparkline-card {
		border: 1px solid var(--border-strong);
		border-radius: 2px;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.8rem;
		background: var(--surface-1);
	}

	.leaderboard,
	.runs-table {
		border: 1px solid var(--border-strong);
		border-radius: 2px;
		background: var(--surface-1);
		padding: 1.2rem;
	}

	.leaderboard ul {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 0.7rem;
	}

	.leaderboard li {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	table {
		width: 100%;
		border-collapse: collapse;
	}

	th,
	td {
		text-align: left;
		padding: 0.6rem;
		border-bottom: 1px solid var(--border-subtle);
	}

	.table-header {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		margin-bottom: 1rem;
	}

	.ghost-button {
		border: 1px solid var(--border-strong);
		border-radius: 2px;
		padding: 0.35rem 0.8rem;
		color: var(--text-primary);
		font-size: 0.85rem;
	}

	.ghost-button.small {
		font-size: 0.8rem;
		padding: 0.3rem 0.7rem;
	}

	.empty {
		color: var(--text-muted);
	}
</style>


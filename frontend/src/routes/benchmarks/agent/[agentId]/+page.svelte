<script lang="ts">
	import { onMount } from 'svelte';
	import type { PageData } from './$types';
	import { agentStore } from '$stores/agentStore';
	import { benchmarkStore } from '$stores/benchmarkStore';
	import { datasetStore } from '$stores/datasetStore';
	import { MetricCard, StatusBadge, Sparkline } from '$lib';
	import { formatDateTime, formatScore } from '$utils/format';
	import { Status } from '$gen/agent_platform/common/v1/types_pb.js';

	export let data: PageData;

	const agentId = data.agentId;
	const runsList = benchmarkStore.runsList;
	const datasets = datasetStore.promptDatasets;
	const activeAgentStore = agentStore.activeAgent;

	onMount(() => {
		agentStore.loadAgents().then(() => agentStore.setActiveAgent(agentId));
		agentStore.loadAgent(agentId, { force: true });
		benchmarkStore.loadRuns(agentId);
		datasetStore.loadPromptDatasets();
	});

	$: agent = $activeAgentStore;
	$: runsForAgent = $runsList.filter((run) => run.agentId === agentId);
	$: latestRun = runsForAgent.length > 0 ? runsForAgent[0] : null;
	$: scoreTrend = runsForAgent
		.slice()
		.reverse()
		.map((run) => run.finalReward?.meanScore)
		.filter((score): score is number => score !== undefined && score !== null);
	$: scoresWithValues = runsForAgent
		.map((run) => run.finalReward?.meanScore)
		.filter((score): score is number => score !== undefined && score !== null);
	$: bestScore = scoresWithValues.length > 0 ? Math.max(...scoresWithValues) : null;

	$: datasetBreakdown = runsForAgent.reduce<Record<
		string,
		{ count: number; avg: number; total: number; scores: number[] }
	>>((acc, run) => {
		const score = run.finalReward?.meanScore;
		if (score === undefined || score === null) return acc;
		if (!acc[run.promptDatasetId]) {
			acc[run.promptDatasetId] = { count: 0, avg: 0, total: 0, scores: [] };
		}
		const bucket = acc[run.promptDatasetId];
		bucket.count += 1;
		bucket.scores.push(score);
		bucket.total = bucket.scores.reduce((sum, s) => sum + s, 0);
		bucket.avg = bucket.total / bucket.count;
		return acc;
	}, {});

	function datasetName(datasetId: string) {
		const dataset = $datasets.find((d) => d.id === datasetId);
		return dataset ? dataset.name : datasetId;
	}
</script>

<section class="agent-benchmarks">
	<header>
		<div>
			<a href="/benchmarks" class="link-back">← Benchmarks</a>
			<h1>{agent?.name ?? 'Loading agent...'}</h1>
			<p>{agent?.task ?? 'Gathering agent details…'}</p>
		</div>
		<div class="header-actions">
			{#if agent}
				{#if latestRun}
					<StatusBadge status={latestRun.status} />
				{/if}
				<a class="ghost-button" href={`/agent-builder?agentId=${agent.id}`}>Edit agent</a>
			{/if}
		</div>
	</header>

	<section class="metrics">
		<MetricCard
			label="Runs"
			value={runsForAgent.length}
			caption="Total benchmark runs for this agent"
		/>
		<MetricCard label="Best score" value={formatScore(bestScore ?? undefined)} caption="Highest mean reward to date" />
		<MetricCard
			label="Latest score"
			value={formatScore(runsForAgent[0]?.finalReward?.meanScore)}
			caption={runsForAgent[0]?.startedAt ? `from ${formatDateTime(runsForAgent[0].startedAt)}` : ''}
		/>
		<div class="sparkline-card">
			<div>
				<span>Trend</span>
				<strong>Performance over time</strong>
			</div>
			<Sparkline values={scoreTrend} />
		</div>
	</section>

	<section class="dataset-breakdown card">
		<h2>Datasets</h2>
		{#if Object.keys(datasetBreakdown).length === 0}
			<p class="empty">No dataset benchmarks yet.</p>
		{:else}
			<div class="dataset-grid">
				{#each Object.entries(datasetBreakdown) as [datasetId, stats]}
					<div class="dataset-card">
						<h3>{datasetName(datasetId)}</h3>
						<p>{stats.count} run{stats.count === 1 ? '' : 's'}</p>
						<strong>{formatScore(stats.avg)}</strong>
					</div>
				{/each}
			</div>
		{/if}
	</section>

	<section class="runs-table card">
		<h2>Runs</h2>
		<table>
			<thead>
				<tr>
					<th>Dataset</th>
					<th>Status</th>
					<th>Mean score</th>
					<th>Started</th>
					<th></th>
				</tr>
			</thead>
			<tbody>
				{#if runsForAgent.length === 0}
					<tr>
						<td colspan="5">No runs yet.</td>
					</tr>
				{:else}
					{#each runsForAgent as run}
						<tr>
							<td>{datasetName(run.promptDatasetId)}</td>
							<td><StatusBadge status={run.status} compact /></td>
							<td>{formatScore(run.finalReward?.meanScore)}</td>
							<td>{formatDateTime(run.startedAt)}</td>
							<td>
								<a class="ghost-button small" href={`/benchmarks/run/${run.id}`}>Inspect</a>
							</td>
						</tr>
					{/each}
				{/if}
			</tbody>
		</table>
	</section>
</section>

<style>
	.agent-benchmarks {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 1rem;
	}

	.link-back {
		color: var(--text-muted);
		font-size: 0.9rem;
	}

	.metrics {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
	}

	.sparkline-card {
		border: 1px solid var(--border-strong);
		border-radius: 2px;
		padding: 1rem;
		background: var(--surface-1);
	}

	.card {
		border: 1px solid var(--border-strong);
		border-radius: 2px;
		background: var(--surface-1);
		padding: 1.1rem;
	}

	.dataset-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
		gap: 1rem;
	}

	.dataset-card {
		border: 1px solid var(--border-strong);
		border-radius: 2px;
		padding: 0.9rem;
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
	}

	table {
		width: 100%;
		border-collapse: collapse;
	}

	th,
	td {
		padding: 0.6rem;
		text-align: left;
		border-bottom: 1px solid var(--border-subtle);
	}

	.ghost-button {
		border: 1px solid var(--border-strong);
		border-radius: 2px;
		padding: 0.35rem 0.8rem;
		color: var(--text-primary);
	}

	.ghost-button.small {
		font-size: 0.8rem;
	}
</style>


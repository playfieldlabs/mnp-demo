<script lang="ts">
	import { onMount } from 'svelte';
	import type { PageData } from './$types';
	import { policyStore } from '$stores/policyStore';
	import { datasetStore } from '$stores/datasetStore';
	import * as datasetRpc from '$rpc/dataset';
	import { formatDateTime } from '$utils/format';

	type PolicyDraft = {
		id?: string;
		name: string;
		systemPrompt: string;
		dataSourceIds: string[];
		externalSourceConfig: string;
		outputSchema: string;
		updateSchedule: string;
	};

	export let data: PageData;

	const policiesList = policyStore.policiesList;
	const activePolicyStore = policyStore.activePolicy;
	const datasetsList = datasetStore.promptDatasets;

	let draft: PolicyDraft = {
		name: '',
		systemPrompt: '',
		dataSourceIds: [],
		externalSourceConfig: '',
		outputSchema: '',
		updateSchedule: ''
	};
	let selectedPolicyId = data.policyId ?? '';
	let toast: { message: string; kind: 'success' | 'error' } | null = null;
	let showDataSourcePicker = false;
	let isRunning = false;
	let externalConfigError: string | null = null;
	let outputSchemaError: string | null = null;

	onMount(() => {
		policyStore.loadPolicies();
		datasetStore.loadPromptDatasets();
		datasetRpc.listDatasets();
		if (data.policyId) {
			policyStore.loadPolicy(data.policyId).then(() => {
				policyStore.setActivePolicy(data.policyId ?? undefined);
			});
		}
	});

	$: activePolicy = $activePolicyStore;
	$: if (activePolicy && activePolicy.id !== draft.id) {
		draft = {
			id: activePolicy.id,
			name: activePolicy.name,
			systemPrompt: activePolicy.systemPrompt,
			dataSourceIds: activePolicy.dataSourceIds || [],
			externalSourceConfig: activePolicy.externalSourceConfig ? JSON.stringify(activePolicy.externalSourceConfig, null, 2) : '',
			outputSchema: activePolicy.outputSchema ? JSON.stringify(activePolicy.outputSchema, null, 2) : '',
			updateSchedule: activePolicy.updateSchedule || ''
		};
		selectedPolicyId = activePolicy.id;
	} else if (!activePolicy && draft.id) {
		draft = {
			id: '',
			name: '',
			systemPrompt: '',
			dataSourceIds: [],
			externalSourceConfig: '',
			outputSchema: '',
			updateSchedule: ''
		};
		selectedPolicyId = '';
	}

	function toggleDataSource(datasetId: string) {
		if (draft.dataSourceIds.includes(datasetId)) {
			draft = { ...draft, dataSourceIds: draft.dataSourceIds.filter((id) => id !== datasetId) };
		} else {
			draft = { ...draft, dataSourceIds: [...draft.dataSourceIds, datasetId] };
		}
	}

	function validateJSON(value: string): boolean {
		if (!value.trim()) return true;
		try {
			JSON.parse(value);
			return true;
		} catch {
			return false;
		}
	}

	$: externalConfigError = draft.externalSourceConfig && !validateJSON(draft.externalSourceConfig) ? 'Invalid JSON format' : null;
	$: outputSchemaError = draft.outputSchema && !validateJSON(draft.outputSchema) ? 'Invalid JSON format' : null;

	async function handleSave() {
		try {
			let externalConfig: Record<string, any> | undefined;
			let outputSchemaObj: Record<string, any> | undefined;

			if (draft.externalSourceConfig.trim()) {
				try {
					externalConfig = JSON.parse(draft.externalSourceConfig);
				} catch (e) {
					toast = { message: 'Invalid JSON in external source config', kind: 'error' };
					setTimeout(() => (toast = null), 3200);
					return;
				}
			}

			if (draft.outputSchema.trim()) {
				try {
					outputSchemaObj = JSON.parse(draft.outputSchema);
				} catch (e) {
					toast = { message: 'Invalid JSON in output schema', kind: 'error' };
					setTimeout(() => (toast = null), 3200);
					return;
				}
			}

			await policyStore.savePolicy({
				id: draft.id,
				name: draft.name,
				systemPrompt: draft.systemPrompt,
				dataSourceIds: draft.dataSourceIds,
				externalSourceConfig: externalConfig,
				outputSchema: outputSchemaObj,
				updateSchedule: draft.updateSchedule
			});
			toast = { message: 'Policy saved', kind: 'success' };
		} catch (error) {
			toast = {
				message: error instanceof Error ? error.message : 'Unable to save policy',
				kind: 'error'
			};
		}
		setTimeout(() => (toast = null), 3200);
	}

	async function handleRunNow() {
		if (!draft.id) {
			toast = { message: 'Please save the policy first', kind: 'error' };
			setTimeout(() => (toast = null), 3200);
			return;
		}

		isRunning = true;
		try {
			await policyStore.runPolicy(draft.id);
			toast = { message: 'Policy generation started', kind: 'success' };
		} catch (error) {
			toast = {
				message: error instanceof Error ? error.message : 'Failed to run policy',
				kind: 'error'
			};
		} finally {
			isRunning = false;
		}
		setTimeout(() => (toast = null), 3200);
	}

	function resetDraft() {
		draft = {
			id: '',
			name: '',
			systemPrompt: '',
			dataSourceIds: [],
			externalSourceConfig: '',
			outputSchema: '',
			updateSchedule: ''
		};
		policyStore.setActivePolicy(undefined);
		selectedPolicyId = '';
	}

	$: lastUpdated = activePolicy?.lastUpdated ? formatDateTime(activePolicy.lastUpdated) : null;
</script>

<div class="flex flex-col h-[calc(100vh-4rem)] max-w-[900px] mx-auto p-8">
	<header class="flex items-center gap-3 mb-6">
		<select
			class="bg-transparent border border-border-strong rounded-sm px-4 py-2 text-text-secondary text-sm cursor-pointer focus:outline-none focus:border-text-muted"
			bind:value={selectedPolicyId}
			on:change={() => policyStore.setActivePolicy(selectedPolicyId || undefined)}
		>
			<option value="">New policy</option>
			{#each $policiesList as policy}
				<option value={policy.id}>{policy.name}</option>
			{/each}
		</select>
		{#if draft.id}
			<button class="bg-transparent border border-border-strong rounded-sm px-4 py-2 text-text-secondary text-sm cursor-pointer transition-all duration-150 hover:bg-surface-2 hover:text-text-primary" type="button" on:click={resetDraft}>New</button>
		{/if}
	</header>

	<div class="flex-1 flex flex-col gap-6 overflow-y-auto">
		<div class="flex flex-col bg-surface-1 border border-border-strong rounded-sm overflow-hidden">
			<div class="px-5 py-3 border-b border-border-subtle">
				<label for="policy-name" class="block text-text-primary text-sm font-medium mb-1">Policy Name</label>
				<input
					id="policy-name"
					class="bg-transparent border-none w-full text-left text-text-primary text-lg placeholder:text-text-muted focus:outline-none"
					type="text"
					placeholder="Enter policy name"
					bind:value={draft.name}
				/>
			</div>
			<div class="px-5 py-3 border-b border-border-subtle">
				<label for="system-prompt" class="block text-text-primary text-sm font-medium mb-2">System Prompt</label>
				<textarea
					id="system-prompt"
					class="bg-transparent border-none w-full p-0 text-left text-text-primary text-sm leading-relaxed resize-none h-32 placeholder:text-text-muted focus:outline-none"
					placeholder="Describe the policy this agent should detect and enforce..."
					bind:value={draft.systemPrompt}
				></textarea>
			</div>
			<div class="px-5 py-3 border-b border-border-subtle">
				<div class="block text-text-primary text-sm font-medium mb-2">Data Sources</div>
				<div class="relative">
					<button
						class="flex items-center gap-2 bg-transparent border border-border-strong rounded-sm px-3 py-2 text-left text-text-secondary text-sm cursor-pointer transition-all duration-150 hover:bg-surface-2 hover:text-text-primary w-full {showDataSourcePicker ? 'bg-surface-2 text-text-primary' : ''}"
						type="button"
						on:click={() => { showDataSourcePicker = !showDataSourcePicker; }}
					>
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
							<polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
							<line x1="12" y1="22.08" x2="12" y2="12"/>
						</svg>
						<span>Select datasets</span>
						{#if draft.dataSourceIds.length > 0}
							<span class="ml-auto bg-[#0066CC] text-white text-xs px-1.5 py-0.5 rounded-sm">{draft.dataSourceIds.length}</span>
						{/if}
					</button>
					{#if showDataSourcePicker}
						<div class="absolute top-full left-0 right-0 mt-1 bg-surface-1 border border-border-strong rounded-sm max-h-60 overflow-y-auto z-[100]">
							{#each $datasetsList as dataset}
								<button
									class="flex items-center gap-2 w-full bg-transparent border-none px-3 py-2 text-left text-text-secondary text-sm cursor-pointer transition-all duration-100 hover:bg-surface-2 hover:text-text-primary {draft.dataSourceIds.includes(dataset.id) ? 'text-text-primary' : ''}"
									type="button"
									on:click={() => toggleDataSource(dataset.id)}
								>
									<span class="w-4 text-[#0066CC]">{draft.dataSourceIds.includes(dataset.id) ? '✓' : ''}</span>
									<span>{dataset.name}</span>
								</button>
							{/each}
							{#if $datasetsList.length === 0}
								<div class="px-3 py-3 text-left text-text-muted text-sm">No datasets available</div>
							{/if}
						</div>
					{/if}
				</div>
				{#if draft.dataSourceIds.length > 0}
					<div class="flex flex-wrap gap-2 mt-2">
						{#each $datasetsList.filter((d) => draft.dataSourceIds.includes(d.id)) as dataset}
							<span class="flex items-center gap-1.5 bg-surface-2 border border-border-strong rounded-sm px-2 py-1 text-left text-xs text-text-secondary">
								{dataset.name}
								<button class="bg-transparent border-none text-text-muted text-base cursor-pointer p-0 leading-none hover:text-text-primary" type="button" on:click={() => toggleDataSource(dataset.id)}>×</button>
							</span>
						{/each}
					</div>
				{/if}
			</div>
			<div class="px-5 py-3 border-b border-border-subtle">
				<label for="external-config" class="block text-text-primary text-sm font-medium mb-2">External Source Configuration</label>
				<p class="text-text-muted text-xs mb-2">Optional: JSON configuration for external APIs or databases</p>
				<textarea
					id="external-config"
					class="bg-transparent border border-border-subtle rounded-sm p-3 w-full text-left text-text-primary text-xs font-mono leading-relaxed resize-none h-32 placeholder:text-text-muted focus:outline-none focus:border-border-strong {externalConfigError ? 'border-[#C62828]' : ''}"
					placeholder="Enter JSON configuration (e.g., api_url, auth)"
					bind:value={draft.externalSourceConfig}
				></textarea>
				{#if externalConfigError}
					<p class="text-[#C62828] text-xs mt-1">{externalConfigError}</p>
				{/if}
			</div>
			<div class="px-5 py-3 border-b border-border-subtle">
				<label for="output-schema" class="block text-text-primary text-sm font-medium mb-2">Output Schema</label>
				<p class="text-text-muted text-xs mb-2">JSON schema defining the structure of the policy output</p>
				<textarea
					id="output-schema"
					class="bg-transparent border border-border-subtle rounded-sm p-3 w-full text-left text-text-primary text-xs font-mono leading-relaxed resize-none h-32 placeholder:text-text-muted focus:outline-none focus:border-border-strong {outputSchemaError ? 'border-[#C62828]' : ''}"
					placeholder="Enter JSON schema (e.g., type, properties)"
					bind:value={draft.outputSchema}
				></textarea>
				{#if outputSchemaError}
					<p class="text-[#C62828] text-xs mt-1">{outputSchemaError}</p>
				{/if}
			</div>
			<div class="px-5 py-3">
				<label for="update-schedule" class="block text-text-primary text-sm font-medium mb-2">Update Schedule</label>
				<p class="text-text-muted text-xs mb-2">Optional: Cron expression for scheduled policy updates</p>
				<div class="flex items-center gap-2">
					<input
						id="update-schedule"
						class="bg-transparent border border-border-subtle rounded-sm px-3 py-2 flex-1 text-left text-text-primary text-sm placeholder:text-text-muted focus:outline-none focus:border-border-strong"
						type="text"
						placeholder="0 0 * * *"
						bind:value={draft.updateSchedule}
					/>
					<div class="flex gap-1">
						<button
							class="bg-transparent border border-border-subtle rounded-sm px-2 py-1 text-text-secondary text-xs cursor-pointer hover:bg-surface-2 hover:text-text-primary"
							type="button"
							on:click={() => draft.updateSchedule = '0 0 * * *'}
							title="Daily at midnight"
						>Daily</button>
						<button
							class="bg-transparent border border-border-subtle rounded-sm px-2 py-1 text-text-secondary text-xs cursor-pointer hover:bg-surface-2 hover:text-text-primary"
							type="button"
							on:click={() => draft.updateSchedule = '0 0 * * 0'}
							title="Weekly on Sunday"
						>Weekly</button>
						<button
							class="bg-transparent border border-border-subtle rounded-sm px-2 py-1 text-text-secondary text-xs cursor-pointer hover:bg-surface-2 hover:text-text-primary"
							type="button"
							on:click={() => draft.updateSchedule = '0 0 1 * *'}
							title="Monthly on 1st"
						>Monthly</button>
					</div>
				</div>
			</div>
		</div>

		<div class="flex items-center justify-between">
			<div class="flex items-center gap-4">
				{#if lastUpdated}
					<span class="text-text-muted text-xs">Last updated: {lastUpdated}</span>
				{/if}
			</div>
			<div class="flex items-center gap-2">
				{#if draft.id}
					<button
						class="flex items-center gap-2 bg-transparent border border-border-strong rounded-sm px-4 py-2 text-left text-text-secondary text-sm cursor-pointer transition-all duration-150 hover:bg-surface-2 hover:text-text-primary disabled:opacity-50 disabled:cursor-not-allowed"
						type="button"
						on:click={handleRunNow}
						disabled={isRunning}
					>
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<polygon points="5 3 19 12 5 21 5 3"/>
						</svg>
						<span>{isRunning ? 'Running...' : 'Run Now'}</span>
					</button>
				{/if}
				<button class="flex items-center gap-2 bg-[#0066CC] border-none rounded-sm px-4 py-2 text-white text-sm font-medium cursor-pointer transition-opacity duration-150 hover:opacity-90" type="button" on:click={handleSave}>
					Save
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<line x1="22" y1="2" x2="11" y2="13"/>
						<polygon points="22 2 15 22 11 13 2 9 22 2"/>
					</svg>
				</button>
			</div>
		</div>
	</div>

	{#if toast}
		<div class="fixed bottom-8 left-1/2 -translate-x-1/2 px-5 py-3 rounded-sm text-sm z-[1000] {toast.kind === 'success' ? 'bg-[#2D7D32] text-white' : 'bg-[#C62828] text-white'}">{toast.message}</div>
	{/if}
</div>


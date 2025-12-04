<script lang="ts">
	import { onMount } from 'svelte';
	import type { PageData } from './$types';
	import { agentStore } from '$stores/agentStore';
	import { toolStore } from '$stores/toolStore';
	import { policyStore } from '$stores/policyStore';
	import { datasetStore } from '$stores/datasetStore';
	import { formatDateTime } from '$utils/format';
	type AgentDraft = {
		id?: string;
		name: string;
		task: string;
		systemPrompt: string;
		toolIds: string[];
		policyAgentIds: string[];
		config: {
			model: string;
			temperature: number;
			maxTokens: number;
			maxToolCalls: number;
		};
	};

	export let data: PageData;

	const agentsList = agentStore.agentsList;
	const activeAgentStore = agentStore.activeAgent;
	const toolsStore = toolStore.tools;
	const policiesStore = policyStore.policiesList;

	let draft: AgentDraft = {
		name: '',
		task: '',
		systemPrompt: '',
		toolIds: [],
		policyAgentIds: [],
		config: {
			model: 'gpt-4o-mini',
			temperature: 0.4,
			maxTokens: 1200,
			maxToolCalls: 4
		}
	};
	let selectedAgentId = data.agentId ?? '';
	let toast: { message: string; kind: 'success' | 'error' } | null = null;
	let showToolPicker = false;
	let showPolicyPicker = false;
	let showSettings = false;

	onMount(() => {
		agentStore.loadAgents();
		toolStore.loadTools();
		policyStore.loadPolicies();
		datasetStore.loadPromptDatasets();
		if (data.agentId) {
			agentStore.loadAgent(data.agentId).then(() => {
				agentStore.setActiveAgent(data.agentId ?? undefined);
			});
		}
	});

	$: activeAgent = $activeAgentStore;
	$: if (activeAgent && activeAgent.id !== draft.id) {
		draft = {
			id: activeAgent.id,
			name: activeAgent.name,
			task: activeAgent.task,
			systemPrompt: activeAgent.systemPrompt,
			toolIds: activeAgent.toolIds || [],
			policyAgentIds: activeAgent.policyAgentIds || [],
			config: activeAgent.config ? {
				model: activeAgent.config.model,
				temperature: activeAgent.config.temperature,
				maxTokens: activeAgent.config.maxTokens,
				maxToolCalls: activeAgent.config.maxToolCalls
			} : {
				model: 'gpt-4o-mini',
				temperature: 0.4,
				maxTokens: 1200,
				maxToolCalls: 4
			}
		};
		selectedAgentId = activeAgent.id;
	} else if (!activeAgent && draft.id) {
		draft = { ...draft, id: '' };
		selectedAgentId = '';
	}

	function toggleTool(toolId: string) {
		if (draft.toolIds.includes(toolId)) {
			draft = { ...draft, toolIds: draft.toolIds.filter((id) => id !== toolId) };
		} else {
			draft = { ...draft, toolIds: [...draft.toolIds, toolId] };
		}
	}

	function selectPolicy(policyId: string) {
		draft = { ...draft, policyAgentIds: policyId ? [policyId] : [] };
		showPolicyPicker = false;
	}

	async function handleSave() {
		try {
			await agentStore.saveAgent(draft);
			toast = { message: 'Agent saved', kind: 'success' };
		} catch (error) {
			toast = {
				message: error instanceof Error ? error.message : 'Unable to save agent',
				kind: 'error'
			};
		}
		setTimeout(() => (toast = null), 3200);
	}

	function resetDraft() {
		draft = {
			id: '',
			name: '',
			task: '',
			systemPrompt: '',
			toolIds: [],
			policyAgentIds: [],
			config: { model: 'gpt-4o-mini', temperature: 0.4, maxTokens: 1200, maxToolCalls: 4 }
		};
		agentStore.setActiveAgent(undefined);
		selectedAgentId = '';
	}

	$: selectedPolicy = $policiesStore.find((p) => p.id === draft.policyAgentIds[0]);
	$: selectedTools = $toolsStore.filter((t) => draft.toolIds.includes(t.id));
</script>

<div class="flex flex-col h-[calc(100vh-4rem)] max-w-[900px] mx-auto p-8">
	<header class="flex items-center gap-3 mb-6">
		<select
			class="bg-transparent border border-border-strong rounded-sm px-4 py-2 text-text-secondary text-sm cursor-pointer focus:outline-none focus:border-text-muted"
			bind:value={selectedAgentId}
			on:change={() => agentStore.setActiveAgent(selectedAgentId || undefined)}
		>
			<option value="">New agent</option>
			{#each $agentsList as agent}
				<option value={agent.id}>{agent.name}</option>
			{/each}
		</select>
		{#if draft.id}
			<button class="bg-transparent border border-border-strong rounded-sm px-4 py-2 text-text-secondary text-sm cursor-pointer transition-all duration-150 hover:bg-surface-2 hover:text-text-primary" type="button" on:click={resetDraft}>New</button>
		{/if}
	</header>

	<div class="flex-1 flex flex-col gap-4">
		<div class="flex flex-col bg-surface-1 border border-border-strong rounded-sm overflow-hidden">
			<input
				class="bg-transparent border-none border-b border-border-subtle px-5 py-2 text-left text-text-primary text-lg font-medium placeholder:text-text-muted focus:outline-none focus:bg-surface-2"
				type="text"
				placeholder="Agent name"
				bind:value={draft.name}
			/>
			<textarea
				class="bg-transparent border-none p-5 text-left text-text-primary text-sm leading-relaxed resize-none h-48 placeholder:text-text-muted focus:outline-none"
				placeholder="Describe your agent's instructions, persona, and behavior..."
				bind:value={draft.systemPrompt}
			></textarea>

			<div class="flex items-center justify-between px-4 py-3 border-t border-border-subtle bg-surface-2">
				<div class="flex items-center gap-2">
					<div class="relative">
						<button
							class="flex items-center gap-2 bg-transparent border border-transparent rounded-sm px-3 py-2 text-left text-text-secondary text-xs cursor-pointer transition-all duration-150 hover:bg-surface-1 hover:text-text-primary {showToolPicker ? 'bg-surface-1 border-border-strong text-text-primary' : ''}"
							type="button"
							on:click={() => { showToolPicker = !showToolPicker; showPolicyPicker = false; showSettings = false; }}
						>
							<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
							</svg>
							<span>Tools</span>
							{#if draft.toolIds.length > 0}
								<span class="bg-[#0066CC] text-white text-xs px-1.5 py-0.5 rounded-sm">{draft.toolIds.length}</span>
							{/if}
						</button>
						{#if showToolPicker}
							<div class="absolute bottom-full left-0 mb-2 bg-surface-1 border border-border-strong rounded-sm min-w-[200px] max-h-60 overflow-y-auto z-[100]">
								{#each $toolsStore as tool}
									<button
										class="flex items-center gap-2 w-full bg-transparent border-none px-3 py-2 text-left text-text-secondary text-sm cursor-pointer transition-all duration-100 hover:bg-surface-2 hover:text-text-primary {draft.toolIds.includes(tool.id) ? 'text-text-primary' : ''}"
										type="button"
										on:click={() => toggleTool(tool.id)}
									>
										<span class="w-4 text-[#0066CC]">{draft.toolIds.includes(tool.id) ? '✓' : ''}</span>
										<span>{tool.name}</span>
									</button>
								{/each}
								{#if $toolsStore.length === 0}
									<div class="px-3 py-3 text-left text-text-muted text-sm">No tools available</div>
								{/if}
							</div>
						{/if}
					</div>

					<div class="relative">
						<button
							class="flex items-center gap-2 bg-transparent border border-transparent rounded-sm px-3 py-2 text-left text-text-secondary text-xs cursor-pointer transition-all duration-150 hover:bg-surface-1 hover:text-text-primary {showPolicyPicker ? 'bg-surface-1 border-border-strong text-text-primary' : ''}"
							type="button"
							on:click={() => { showPolicyPicker = !showPolicyPicker; showToolPicker = false; showSettings = false; }}
						>
							<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
							</svg>
							<span>{selectedPolicy?.name || 'Policy'}</span>
							{#if selectedPolicy?.lastUpdated}
								<span class="text-text-muted text-[10px]">({formatDateTime(selectedPolicy.lastUpdated)})</span>
							{/if}
						</button>
						{#if showPolicyPicker}
							<div class="absolute bottom-full left-0 mb-2 bg-surface-1 border border-border-strong rounded-sm min-w-[280px] max-h-60 overflow-y-auto z-[100]">
								<button
									class="flex items-center gap-2 w-full bg-transparent border-none px-3 py-2 text-left text-text-secondary text-sm cursor-pointer transition-all duration-100 hover:bg-surface-2 hover:text-text-primary {!draft.policyAgentIds.length ? 'text-text-primary' : ''}"
									type="button"
									on:click={() => selectPolicy('')}
								>
									<span class="w-4 text-[#0066CC]">{!draft.policyAgentIds.length ? '✓' : ''}</span>
									<span>No policy</span>
								</button>
								{#each $policiesStore as policy}
									<button
										class="flex flex-col gap-0.5 w-full bg-transparent border-none px-3 py-2 text-left text-text-secondary text-sm cursor-pointer transition-all duration-100 hover:bg-surface-2 hover:text-text-primary {draft.policyAgentIds[0] === policy.id ? 'text-text-primary' : ''}"
										type="button"
										on:click={() => selectPolicy(policy.id)}
									>
										<div class="flex items-center gap-2">
											<span class="w-4 text-[#0066CC]">{draft.policyAgentIds[0] === policy.id ? '✓' : ''}</span>
										<span>{policy.name}</span>
										</div>
										{#if policy.lastUpdated}
											<span class="text-text-muted text-xs ml-6">Updated: {formatDateTime(policy.lastUpdated)}</span>
										{/if}
									</button>
								{/each}
							</div>
						{/if}
					</div>

					<div class="relative">
						<button
							class="flex items-center gap-2 bg-transparent border border-transparent rounded-sm px-3 py-2 text-left text-text-secondary text-xs cursor-pointer transition-all duration-150 hover:bg-surface-1 hover:text-text-primary {showSettings ? 'bg-surface-1 border-border-strong text-text-primary' : ''}"
							type="button"
							on:click={() => { showSettings = !showSettings; showToolPicker = false; showPolicyPicker = false; }}
						>
							<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<circle cx="12" cy="12" r="3"/>
								<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
							</svg>
							<span>Settings</span>
						</button>
						{#if showSettings}
							<div class="absolute bottom-full left-0 mb-2 bg-surface-1 border border-border-strong rounded-sm min-w-[240px] py-2 z-[100]">
								<label class="flex items-center justify-between px-3 py-2 text-left text-sm text-text-secondary">
									<span>Temperature</span>
									<select class="bg-surface-2 border border-border-strong rounded-sm px-2 py-1.5 text-left text-text-primary text-xs" bind:value={draft.config.temperature}>
										<option value={0}>0</option>
										<option value={0.1}>0.1</option>
										<option value={0.2}>0.2</option>
										<option value={0.3}>0.3</option>
										<option value={0.4}>0.4</option>
										<option value={0.5}>0.5</option>
										<option value={0.6}>0.6</option>
										<option value={0.7}>0.7</option>
										<option value={0.8}>0.8</option>
										<option value={0.9}>0.9</option>
										<option value={1}>1</option>
									</select>
								</label>
								<label class="flex items-center justify-between px-3 py-2 text-left text-sm text-text-secondary">
									<span>Max tokens</span>
									<select class="bg-surface-2 border border-border-strong rounded-sm px-2 py-1.5 text-left text-text-primary text-xs" bind:value={draft.config.maxTokens}>
										<option value={256}>256</option>
										<option value={512}>512</option>
										<option value={1024}>1024</option>
										<option value={1200}>1200</option>
										<option value={2048}>2048</option>
										<option value={4096}>4096</option>
										<option value={8192}>8192</option>
									</select>
								</label>
							</div>
						{/if}
					</div>
				</div>

				<div class="flex items-center">
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

		{#if selectedTools.length > 0}
			<div class="flex flex-wrap gap-2">
				{#each selectedTools as tool}
					<span class="flex items-center gap-2 bg-surface-2 border border-border-strong rounded-sm px-2 py-1.5 text-left text-xs text-text-secondary">
						{tool.name}
						<button class="bg-transparent border-none text-text-muted text-base cursor-pointer p-0 leading-none hover:text-text-primary" type="button" on:click={() => toggleTool(tool.id)}>×</button>
					</span>
				{/each}
			</div>
		{/if}
	</div>

	{#if toast}
		<div class="fixed bottom-8 left-1/2 -translate-x-1/2 px-5 py-3 rounded-sm text-sm z-[1000] {toast.kind === 'success' ? 'bg-[#2D7D32] text-white' : 'bg-[#C62828] text-white'}">{toast.message}</div>
	{/if}
</div>


<script lang="ts">
	import { create } from '@bufbuild/protobuf';
	import type { Block } from '$gen/agent_platform/agent/v1/block_pb.js';
	import { BlockSchema } from '$gen/agent_platform/agent/v1/block_pb.js';
	import type { StreamAgentRunResponse } from '$gen/agent_platform/service/v1/agent_service_pb.js';
	import { streamAgentRun } from '$rpc/agent';
	import BlockRenderer from './BlockRenderer.svelte';

	export let agentId: string;
	export let datasetIds: string[] = [];

	let inputValue = '';
	let blocks: Block[] = [];
	let isStreaming = false;
	let error: string | null = null;
	let messagesContainer: HTMLDivElement;

	async function handleSubmit() {
		if (!inputValue.trim() || !agentId || isStreaming) return;

		const userInput = inputValue.trim();
		inputValue = '';
		error = null;

		const userBlock = create(BlockSchema, {
			id: crypto.randomUUID(),
			sequence: blocks.length,
			content: {
				case: 'userInput',
				value: { text: userInput }
			}
		});

		blocks = [...blocks, userBlock];
		isStreaming = true;

		try {
			for await (const response of streamAgentRun(agentId, userInput, datasetIds)) {
				handleStreamResponse(response);
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to stream agent response';
		} finally {
			isStreaming = false;
		}
	}

	function handleStreamResponse(response: StreamAgentRunResponse) {
		if (response.event.case === 'block' && response.event.value) {
			blocks = [...blocks, response.event.value];
			scrollToBottom();
		} else if (response.event.case === 'completed' && response.event.value) {
			isStreaming = false;
		} else if (response.event.case === 'error' && response.event.value) {
			error = response.event.value.message || 'Agent run error';
			isStreaming = false;
		}
	}

	function scrollToBottom() {
		if (messagesContainer) {
			setTimeout(() => {
				messagesContainer.scrollTop = messagesContainer.scrollHeight;
			}, 0);
		}
	}

	function handleKeyDown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSubmit();
		}
	}

	function clearChat() {
		blocks = [];
		error = null;
	}
</script>

<div class="chat-panel">
	<div class="header">
		<h3>Test Agent</h3>
		{#if blocks.length > 0}
			<button class="clear-button" type="button" on:click={clearChat}>
				Clear
			</button>
		{/if}
	</div>

	<div class="messages" bind:this={messagesContainer}>
		{#if blocks.length === 0}
			<div class="empty-state">
				<p>Send a message to test your agent</p>
			</div>
		{:else}
			{#each blocks as block}
				<BlockRenderer block={block} />
			{/each}
			{#if isStreaming}
				<div class="streaming-indicator">
					<span class="dot"></span>
					<span class="dot"></span>
					<span class="dot"></span>
				</div>
			{/if}
		{/if}
		{#if error}
			<div class="error-message">
				<strong>Error</strong>
				<p>{error}</p>
			</div>
		{/if}
	</div>

	<div class="input-area">
		<textarea
			class="input"
			placeholder="Type your message..."
			bind:value={inputValue}
			on:keydown={handleKeyDown}
			disabled={!agentId || isStreaming}
			rows="3"
		></textarea>
		<button
			class="send-button"
			type="button"
			on:click={handleSubmit}
			disabled={!inputValue.trim() || !agentId || isStreaming}
		>
			<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<line x1="22" y1="2" x2="11" y2="13"/>
				<polygon points="22 2 15 22 11 13 2 9 22 2"/>
			</svg>
		</button>
	</div>
</div>

<style>
	.chat-panel {
		display: flex;
		flex-direction: column;
		height: 100%;
		background: var(--color-surface-1);
		border: 1px solid var(--color-border-strong);
		border-radius: 2px;
		overflow: hidden;
	}

	.header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem;
		border-bottom: 1px solid var(--color-border-subtle);
		background: var(--color-surface-2);
	}

	.header h3 {
		margin: 0;
		font-size: 0.875rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-primary);
	}

	.clear-button {
		background: transparent;
		border: 1px solid var(--color-border-strong);
		border-radius: 2px;
		padding: 0.375rem 0.75rem;
		font-size: 0.75rem;
		color: var(--color-text-secondary);
		cursor: pointer;
		transition: all 0.15s;
	}

	.clear-button:hover {
		background: var(--color-surface-1);
		color: var(--color-text-primary);
	}

	.messages {
		flex: 1;
		overflow-y: auto;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.empty-state {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		color: var(--color-text-muted);
	}

	.empty-state p {
		margin: 0;
		font-size: 0.875rem;
	}

	.streaming-indicator {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.8rem;
	}

	.dot {
		width: 0.5rem;
		height: 0.5rem;
		border-radius: 50%;
		background: var(--color-text-muted);
		animation: pulse 1.4s ease-in-out infinite;
	}

	.dot:nth-child(2) {
		animation-delay: 0.2s;
	}

	.dot:nth-child(3) {
		animation-delay: 0.4s;
	}

	@keyframes pulse {
		0%, 100% {
			opacity: 0.3;
		}
		50% {
			opacity: 1;
		}
	}

	.error-message {
		border: 1px solid #C62828;
		border-radius: 2px;
		padding: 0.8rem;
		background: rgba(198, 40, 40, 0.1);
		margin-top: 0.5rem;
	}

	.error-message strong {
		display: block;
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: #C62828;
		margin-bottom: 0.4rem;
		font-weight: 600;
	}

	.error-message p {
		margin: 0;
		color: #C62828;
		font-size: 0.875rem;
		line-height: 1.5;
	}

	.input-area {
		display: flex;
		gap: 0.5rem;
		padding: 1rem;
		border-top: 1px solid var(--color-border-subtle);
		background: var(--color-surface-2);
	}

	.input {
		flex: 1;
		background: var(--color-surface-1);
		border: 1px solid var(--color-border-strong);
		border-radius: 2px;
		padding: 0.75rem;
		font-family: inherit;
		font-size: 0.875rem;
		color: var(--color-text-primary);
		resize: none;
		line-height: 1.5;
	}

	.input:focus {
		outline: none;
		border-color: var(--color-text-muted);
	}

	.input:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.send-button {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 2.5rem;
		height: 2.5rem;
		background: #0066CC;
		border: none;
		border-radius: 2px;
		color: white;
		cursor: pointer;
		transition: opacity 0.15s;
		flex-shrink: 0;
	}

	.send-button:hover:not(:disabled) {
		opacity: 0.9;
	}

	.send-button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>


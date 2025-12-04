<script lang="ts">
	import type { Block } from '$gen/agent_platform/agent/v1/block_pb.js';
	import ThinkingBlockDisplay from './ThinkingBlockDisplay.svelte';

	export let block: Block;
</script>

{#if block.content.case === 'userInput'}
	<div class="block user-input">
		<strong>User</strong>
		<p>{block.content.value.text}</p>
	</div>
{:else if block.content.case === 'assistantMessage'}
	<div class="block assistant-message">
		<strong>Assistant</strong>
		<p>{block.content.value.text}</p>
	</div>
{:else if block.content.case === 'thinkingBlock'}
	<ThinkingBlockDisplay content={block.content.value} />
{:else if block.content.case === 'toolCall'}
	<div class="block tool-call">
		<strong>Tool: {block.content.value.toolId}</strong>
		<div class="tool-details">
			<div class="input">
				<em>Input:</em>
				<pre>{JSON.stringify(block.content.value.input, null, 2)}</pre>
			</div>
			<div class="output">
				<em>Output:</em>
				<pre>{JSON.stringify(block.content.value.output, null, 2)}</pre>
			</div>
		</div>
	</div>
{/if}

<style>
	.block {
		border: 1px solid var(--border-weak);
		border-radius: 2px;
		padding: 0.8rem;
		background: var(--surface-1);
		margin-bottom: 0.5rem;
	}

	.block strong {
		display: block;
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--text-muted);
		margin-bottom: 0.4rem;
		font-weight: 600;
	}

	.block p {
		margin: 0;
		color: var(--text);
		line-height: 1.5;
	}

	.tool-details {
		display: grid;
		gap: 0.8rem;
		margin-top: 0.6rem;
	}

	.tool-details > div {
		border: 1px solid var(--border-weak);
		border-radius: 2px;
		padding: 0.6rem;
		background: var(--surface-2);
	}

	.tool-details em {
		display: block;
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--text-muted);
		margin-bottom: 0.4rem;
		font-style: normal;
		font-weight: 600;
	}

	.tool-details pre {
		margin: 0;
		font-family: 'Azeret Mono', monospace;
		font-size: 0.75rem;
		color: var(--text);
		white-space: pre-wrap;
		word-wrap: break-word;
		overflow-x: auto;
	}
</style>



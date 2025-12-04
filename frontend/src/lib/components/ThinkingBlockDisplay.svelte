<script lang="ts">
	import type { ThinkingBlock } from '$gen/agent_platform/agent/v1/block_pb.js';

	export let content: ThinkingBlock;

	let expanded = false;

	function toggle() {
		expanded = !expanded;
	}
</script>

<div class="thinking-block">
	<button class="header" on:click={toggle} type="button">
		<span class="icon">{expanded ? '▼' : '▶'}</span>
		<strong>Thinking</strong>
		{#if content.signature}
			<span class="signature">{content.signature}</span>
		{/if}
	</button>
	{#if expanded}
		<pre class="content">{content.thinking}</pre>
	{/if}
</div>

<style>
	.thinking-block {
		border: 1px solid var(--border-weak);
		border-radius: 2px;
		background: var(--surface-2);
		overflow: hidden;
	}

	.header {
		width: 100%;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.6rem 0.8rem;
		background: transparent;
		border: none;
		cursor: pointer;
		text-align: left;
		font-family: inherit;
		font-size: 0.85rem;
		color: var(--text-muted);
		transition: background-color 0.15s;
	}

	.header:hover {
		background: var(--surface-3);
	}

	.icon {
		font-size: 0.7rem;
		color: var(--text-muted);
		width: 0.8rem;
		display: inline-block;
	}

	.header strong {
		font-weight: 600;
		color: var(--text);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		font-size: 0.75rem;
	}

	.signature {
		margin-left: auto;
		font-family: 'Azeret Mono', monospace;
		font-size: 0.7rem;
		color: var(--text-muted);
		opacity: 0.7;
	}

	.content {
		padding: 0.8rem;
		margin: 0;
		font-family: 'Azeret Mono', monospace;
		font-size: 0.8rem;
		line-height: 1.6;
		color: var(--text);
		background: var(--surface-1);
		border-top: 1px solid var(--border-weak);
		white-space: pre-wrap;
		word-wrap: break-word;
		overflow-x: auto;
	}
</style>



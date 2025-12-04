<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let label = 'System prompt';
	export let value = '';
	export let maxLength = 4000;
	export let placeholder =
		'Describe the agent tone, goals, constraints, and guardrails...';

	const dispatch = createEventDispatcher<{ change: string }>();

	function handleInput(event: Event) {
		value = (event.target as HTMLTextAreaElement).value;
		dispatch('change', value);
	}
</script>

<label class="prompt-editor">
	<div class="prompt-editor__header">
		<span>{label}</span>
		<span class={`count ${value.length > maxLength ? 'over-limit' : ''}`}>
			{value.length}/{maxLength}
		</span>
	</div>
	<textarea
		bind:value
		placeholder={placeholder}
		on:input={handleInput}
		maxlength={maxLength}
		rows={12}
	></textarea>
</label>

<style>
	.prompt-editor {
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
		width: 100%;
	}

	.prompt-editor__header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		font-size: 0.9rem;
		color: var(--text-muted);
	}

	textarea {
		width: 100%;
		border-radius: 2px;
		border: 1px solid var(--border-strong);
		padding: 1rem;
		font-size: 1rem;
		font-family: var(--font-mono, 'IBM Plex Mono', 'SFMono-Regular', monospace);
		background: var(--surface-1);
		color: var(--text-primary);
		resize: vertical;
		transition: border-color 0.2s ease;
	}

	textarea:focus {
		outline: none;
		border-color: var(--blue-5);
		box-shadow: 0 0 0 3px color-mix(in srgb, var(--blue-5) 20%, transparent);
	}

	.count {
		font-size: 0.8rem;
	}

	.over-limit {
		color: var(--red-6);
		font-weight: 600;
	}
</style>


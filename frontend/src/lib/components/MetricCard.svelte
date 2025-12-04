<script lang="ts">
	export let label = '';
	export let value: string | number = '—';
	export let caption = '';
	export let trend: number | undefined = undefined;

	$: formattedTrend =
		typeof trend === 'number'
			? `${trend > 0 ? '+' : ''}${(trend * 100).toFixed(1)}%`
			: undefined;
</script>

<div class="p-4 rounded-sm border border-border-strong bg-surface-1 flex flex-col gap-1.5">
	<span class="text-text-muted text-sm uppercase tracking-wider">{label}</span>
	<div class="flex items-baseline gap-1.5">
		<strong class="text-3xl">{value}</strong>
		{#if formattedTrend}
			<span class={trend && trend >= 0 ? 'text-[#1B5E20] font-semibold' : 'text-[#C62828] font-semibold'}>{formattedTrend}</span>
		{/if}
	</div>
	{#if caption}
		<span class="text-text-secondary text-sm">{caption}</span>
	{/if}
</div>


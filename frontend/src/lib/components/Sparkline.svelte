<script lang="ts">
	export let values: number[] = [];
	export let width = 220;
	export let height = 60;
	export let stroke = 'var(--blue-5)';

	$: normalized = (values.length ? values : [0]) as number[];
	$: min = Math.min(...normalized);
	$: max = Math.max(...normalized);
	$: range = max - min || 1;
	$: points = normalized
		.map((value, index) => {
			const x = (index / Math.max(normalized.length - 1, 1)) * width;
			const y = height - ((value - min) / range) * height;
			return `${x},${y}`;
		})
		.join(' ');
</script>

<svg {width} {height} viewBox={`0 0 ${width} ${height}`} class="sparkline" aria-hidden="true">
	{#if normalized.length > 1}
		<polyline points={points} stroke={stroke} fill="none" stroke-width="2" stroke-linecap="round" />
	{:else}
		<line x1="0" y1={height / 2} x2={width} y2={height / 2} stroke={stroke} stroke-width="2" />
	{/if}
</svg>

<style>
	.sparkline {
		width: 100%;
		height: auto;
	}
</style>


<script lang="ts">
	import type { Snippet } from 'svelte';
	import favicon from '$lib/assets/favicon.svg';
	import logo from '$lib/assets/logo.svg';
	import '../app.css';

	export let children: Snippet;

	const navLinks = [
		{ href: '/agent-builder', label: 'Agent Builder' },
		{ href: '/policy-builder', label: 'Policy Builder' },
		{ href: '/benchmarks', label: 'Benchmarks' }
	];
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link
		href="https://fonts.googleapis.com/css2?family=Azeret+Mono:wght@400;500;600&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<div class="min-h-screen grid grid-cols-[280px_1fr] max-md:grid-cols-1">
	<aside class="bg-surface-1 border-r border-border-subtle p-6 flex flex-col gap-8 max-md:flex-row max-md:items-center max-md:justify-between">
		<div class="flex items-center">
			<img src={logo} alt="Analytical Engine" class="w-full max-w-[180px] h-auto" />
		</div>
		<nav class="flex flex-col gap-2.5 max-md:flex-row max-md:gap-4">
			{#each navLinks as link}
				<a href={link.href} class="px-3 py-2.5 rounded-sm text-text-secondary font-medium transition-all duration-150 hover:bg-surface-2 hover:text-text-primary focus-visible:bg-surface-2 focus-visible:text-text-primary">{link.label}</a>
			{/each}
		</nav>
	</aside>
	<main class="min-h-screen bg-surface p-8">
		{@render children()}
	</main>
</div>

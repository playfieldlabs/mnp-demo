<section class="home">
	<header>
		<p class="eyebrow">Orchestrate · Evaluate · Ship</p>
		<h1>Build agents faster with a focused builder & benchmark hub.</h1>
		<p>
			Spin up prompts, attach tools, wire policies, and validate quality across datasets in a single
			workspace.
		</p>
		<div class="cta-row">
			<a class="cta" href="/agent-builder">Open Agent Builder</a>
			<a class="secondary" href="/benchmarks">View Benchmarks</a>
		</div>
	</header>
</section>

<style>
	.home {
		max-width: 820px;
		margin: 0 auto;
		padding: 3rem 0;
	}

	.eyebrow {
		text-transform: uppercase;
		letter-spacing: 0.3em;
		color: var(--text-muted);
		font-size: 0.8rem;
		margin-bottom: 1rem;
	}

	h1 {
		font-size: clamp(2.4rem, 4vw, 3.4rem);
		margin-bottom: 1rem;
	}

	p {
		color: var(--text-secondary);
		font-size: 1.1rem;
	}

	.cta-row {
		display: flex;
		gap: 1rem;
		margin-top: 2rem;
	}

	.cta,
	.secondary {
		padding: 0.9rem 1.4rem;
		border-radius: 2px;
		font-weight: 500;
		transition: opacity 0.15s ease;
	}

	.cta {
		background: var(--blue-5);
		color: #ffffff;
	}

	.cta:hover {
		opacity: 0.9;
	}

	.secondary {
		border: 1px solid var(--border-strong);
		color: var(--text-primary);
		background: transparent;
	}

	.secondary:hover {
		background: var(--surface-2);
	}
</style>

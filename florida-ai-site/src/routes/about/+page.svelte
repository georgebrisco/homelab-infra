<svelte:head>
	<title>About — Florida AI</title>
	<meta name="description" content="Meet the team behind Florida AI. Experienced technologists helping small businesses make the most of AI." />
</svelte:head>

<section class="page-hero">
	<div class="container">
		<h1>About Florida AI</h1>
		<p class="subtitle">Experienced technologists who speak plain English.</p>
	</div>
</section>

<section class="section">
	<div class="container">
		<div class="about-content">
			<div class="about-text">
				<h2>Why we started this</h2>
				<p>AI is the most significant shift in how businesses operate since the internet.
				   But for most small businesses, it feels inaccessible — drowned in hype, locked
				   behind technical jargon, and seemingly designed for big companies with big budgets.</p>
				<p>We started Florida AI because we believe every business deserves practical access
				   to these tools. Not a sales pitch about "digital transformation" or "synergistic
				   AI-driven paradigm shifts." Just honest, hands-on help from people who've spent
				   years working with this technology and understand that what matters is whether
				   it saves you time and money.</p>
				<p>We come from backgrounds in software engineering, infrastructure, and systems
				   design. We've built the kind of systems that power the tools businesses use
				   every day. Now we're bringing that expertise directly to the people who need
				   it most — small business owners who are too busy running their business to
				   become AI experts.</p>
			</div>
		</div>
	</div>
</section>

<section class="section section-alt">
	<div class="container">
		<h2 class="text-center">Our approach</h2>
		<p class="subtitle text-center">What makes us different from a YouTube tutorial.</p>
		<div class="approach-grid">
			<div class="approach-item">
				<h3>We come to you</h3>
				<p>No webinars, no online courses. We sit in your office, learn how your business
				   works, and build solutions around your actual workflow. Every business is different,
				   and cookie-cutter advice doesn't cut it.</p>
			</div>
			<div class="approach-item">
				<h3>We use your real work</h3>
				<p>During our audit and training sessions, we work with your actual emails, documents,
				   and tasks. You'll see exactly what AI can do with the work you're already doing,
				   not some hypothetical demo.</p>
			</div>
			<div class="approach-item">
				<h3>We stay with you</h3>
				<p>AI moves fast. What's possible today will be different in three months. Our
				   retainer model means you always have someone keeping an eye on what's new and
				   making sure your setup evolves with the technology.</p>
			</div>
			<div class="approach-item">
				<h3>We're honest about limits</h3>
				<p>AI isn't magic. It hallucinates, it makes mistakes, and it's not right for every
				   task. We'll always tell you what it can't do, set up guardrails to catch errors,
				   and make sure your team knows when to trust it and when to double-check.</p>
			</div>
		</div>
	</div>
</section>

<section class="section">
	<div class="container">
		<h2 class="text-center">What we help with</h2>
		<div class="help-grid">
			<div class="help-item">
				<div class="help-icon">&#9993;</div>
				<h3>Email &amp; messaging</h3>
				<p>Draft replies, summarise threads, handle routine enquiries. AI as your email co-pilot.</p>
			</div>
			<div class="help-item">
				<div class="help-icon">&#128196;</div>
				<h3>Document production</h3>
				<p>Reports, proposals, invoices, contracts. Templates that produce professional output in seconds.</p>
			</div>
			<div class="help-item">
				<div class="help-icon">&#128187;</div>
				<h3>General productivity</h3>
				<p>Meeting summaries, research, data analysis, scheduling. The tasks that eat your day.</p>
			</div>
			<div class="help-item">
				<div class="help-icon">&#128274;</div>
				<h3>Privacy &amp; security</h3>
				<p>Guidance on keeping your data safe, choosing the right tools, and understanding what AI does with your information.</p>
			</div>
		</div>
	</div>
</section>

<section class="cta-section">
	<div class="container text-center">
		<h2>Curious? Let's talk.</h2>
		<p class="cta-text">A free 45-minute chat costs you nothing but could change how you work.</p>
		<a href="/contact" class="btn btn-primary btn-lg">Book a Free AI Audit</a>
	</div>
</section>

<style>
	.page-hero {
		padding: 3.5rem 0 2.5rem;
		background: var(--color-primary-lighter);
		text-align: center;
	}
	.page-hero h1 { margin-bottom: var(--space-sm); }

	.about-text {
		max-width: 700px;
	}
	.about-text p {
		color: var(--color-text-light);
		margin-bottom: var(--space-lg);
		font-size: 1.05rem;
		line-height: 1.8;
	}

	.approach-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: var(--space-2xl);
		max-width: 850px;
		margin: 0 auto;
	}
	.approach-item h3 { color: var(--color-primary); }
	.approach-item p { color: var(--color-text-light); }

	.help-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: var(--space-xl);
		margin-top: var(--space-2xl);
		text-align: center;
	}
	.help-icon {
		font-size: 2.5rem;
		margin-bottom: var(--space-md);
	}
	.help-item h3 { font-size: 1.05rem; }
	.help-item p {
		color: var(--color-text-light);
		font-size: 0.95rem;
	}

	.cta-section {
		padding: var(--space-4xl) 0;
		background: var(--color-primary);
	}
	.cta-section h2 { color: var(--color-text-inverse); }
	.cta-text {
		color: #cbd5e0;
		max-width: 500px;
		margin: 0 auto var(--space-2xl);
	}

	@media (max-width: 768px) {
		.approach-grid,
		.help-grid {
			grid-template-columns: 1fr;
		}
	}
</style>

<svelte:head>
	<title>Florida AI — AI Consulting for Small Businesses</title>
	<meta name="description" content="Florida AI helps small businesses harness the power of AI. Free AI audits, hands-on setup, ongoing support." />
</svelte:head>

<!-- Hero -->
<section class="hero">
	<div class="container">
		<div class="hero-content">
			<p class="hero-eyebrow">AI consulting for small businesses</p>
			<h1>Stop worrying about AI.<br/>Start <span class="highlight">using</span> it.</h1>
			<p class="hero-text">
				You know AI is changing everything. But between the hype and the jargon,
				it's hard to know where to start. We cut through the noise, come to your
				office, and get AI working for your business — in language you understand.
			</p>
			<div class="hero-actions">
				<a href="/contact" class="btn btn-primary btn-lg">Book a Free AI Audit</a>
				<a href="/services" class="btn btn-outline btn-lg">See Our Services</a>
			</div>
		</div>
	</div>
</section>

<!-- Pain points -->
<section class="section section-alt">
	<div class="container text-center">
		<h2>Sound familiar?</h2>
		<p class="subtitle">These are the things we hear from business owners every day.</p>
		<div class="pain-grid">
			<div class="pain-card">
				<div class="pain-icon">&#128172;</div>
				<p>"I've tried ChatGPT but I don't know how to actually use it for my business."</p>
			</div>
			<div class="pain-card">
				<div class="pain-icon">&#128274;</div>
				<p>"I'm worried about sending confidential client data to AI tools."</p>
			</div>
			<div class="pain-card">
				<div class="pain-icon">&#9201;</div>
				<p>"My staff spend hours on emails and documents that AI could probably help with."</p>
			</div>
			<div class="pain-card">
				<div class="pain-icon">&#128176;</div>
				<p>"I can't afford to hire a tech team, but I know I'm falling behind."</p>
			</div>
		</div>
	</div>
</section>

<!-- How it works -->
<section class="section">
	<div class="container text-center">
		<h2>How it works</h2>
		<p class="subtitle">Three simple steps to get AI working in your business.</p>
		<div class="steps-grid">
			<div class="step">
				<div class="step-number">1</div>
				<h3>Free AI Audit</h3>
				<p>We visit your office, learn about your day-to-day work, and show you — live — how AI
				   can handle your real tasks. No slides, no jargon. Just a practical demo with your actual work.</p>
			</div>
			<div class="step">
				<div class="step-number">2</div>
				<h3>Setup &amp; Training</h3>
				<p>We configure AI tools tailored to your business, build custom templates for your
				   common tasks, and train your team in a hands-on half-day session. You'll be up and
				   running before we leave.</p>
			</div>
			<div class="step">
				<div class="step-number">3</div>
				<h3>Ongoing Support</h3>
				<p>AI moves fast. Our monthly retainer includes support hours, template updates,
				   and regular check-ins to make sure you're getting the most from your setup
				   as the technology evolves.</p>
			</div>
		</div>
	</div>
</section>

<!-- Service tiers preview -->
<section class="section section-alt">
	<div class="container text-center">
		<h2>Choose your starting point</h2>
		<p class="subtitle">Whether you want to dip a toe in or dive deep, we have you covered.</p>
		<div class="tiers-grid">
			<div class="card">
				<h3>AI Kickstart</h3>
				<p class="tier-price">Free</p>
				<p class="tier-desc">A 45-minute visit to your office. We look at how you work,
				   identify where AI can save you time, and give you a live demo using your own tasks.</p>
				<a href="/contact" class="btn btn-outline">Book Now</a>
			</div>
			<div class="card card-featured">
				<h3>AI Ready</h3>
				<p class="tier-price">$450</p>
				<p class="tier-desc">Half-day setup and training on your existing machines. We configure
				   AI tools, build templates for your workflows, and get your team comfortable using them.</p>
				<a href="/contact" class="btn btn-primary">Get Started</a>
			</div>
			<div class="card">
				<h3>AI Powerhouse</h3>
				<p class="tier-price">$1,200</p>
				<p class="tier-desc">We supply and install a dedicated, pre-configured AI workstation.
				   Clean, professional setup with everything ready to go, plus full training.</p>
				<a href="/contact" class="btn btn-outline">Learn More</a>
			</div>
		</div>
		<p class="tiers-retainer">
			All clients can add our <strong>monthly retainer ($500/mo)</strong> for ongoing support,
			template updates, and regular check-ins.
		</p>
	</div>
</section>

<!-- Trust / social proof placeholder -->
<section class="section">
	<div class="container text-center">
		<h2>AI that works for real businesses</h2>
		<div class="trust-grid">
			<div class="trust-item">
				<div class="trust-stat">2hrs</div>
				<p>Average time saved per employee, per day, on email and document tasks</p>
			</div>
			<div class="trust-item">
				<div class="trust-stat">45min</div>
				<p>That's all it takes for our free audit to show you what's possible</p>
			</div>
			<div class="trust-item">
				<div class="trust-stat">Plain English</div>
				<p>No jargon, no hype. Just practical help from people who understand small business</p>
			</div>
		</div>
	</div>
</section>

<!-- Final CTA -->
<section class="cta-section">
	<div class="container text-center">
		<h2>Ready to see what AI can do for you?</h2>
		<p class="cta-text">Book a free, no-obligation AI audit. We'll come to you, look at your
		   real work, and show you exactly how AI can help. No commitment, no hard sell.</p>
		<a href="/contact" class="btn btn-primary btn-lg">Book Your Free AI Audit</a>
	</div>
</section>

<style>
	/* Hero */
	.hero {
		padding: 5rem 0 4rem;
		background: linear-gradient(135deg, var(--color-primary-lighter) 0%, var(--color-bg) 70%);
	}
	.hero-content { max-width: 720px; }
	.hero-eyebrow {
		text-transform: uppercase;
		letter-spacing: 0.1em;
		font-size: 0.85rem;
		color: var(--color-accent);
		font-weight: 600;
		margin-bottom: var(--space-md);
	}
	.hero h1 { margin-bottom: var(--space-lg); }
	.highlight { color: var(--color-accent); }
	.hero-text {
		font-size: 1.15rem;
		color: var(--color-text-light);
		line-height: 1.75;
		margin-bottom: var(--space-2xl);
	}
	.hero-actions {
		display: flex;
		gap: var(--space-md);
		flex-wrap: wrap;
	}

	/* Pain points */
	.pain-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: var(--space-lg);
		max-width: 800px;
		margin: 0 auto;
	}
	.pain-card {
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: 10px;
		padding: var(--space-xl);
		text-align: left;
	}
	.pain-icon {
		font-size: 1.75rem;
		margin-bottom: var(--space-sm);
	}
	.pain-card p {
		font-style: italic;
		color: var(--color-text-light);
	}

	/* Steps */
	.steps-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--space-2xl);
		text-align: left;
	}
	.step-number {
		width: 44px;
		height: 44px;
		border-radius: 50%;
		background: var(--color-accent);
		color: white;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 700;
		font-size: 1.1rem;
		margin-bottom: var(--space-md);
	}
	.step p { color: var(--color-text-light); }

	/* Tiers */
	.tiers-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--space-lg);
		margin-bottom: var(--space-2xl);
	}
	.tier-price {
		font-size: 2rem;
		font-weight: 700;
		color: var(--color-primary);
		margin: var(--space-md) 0;
	}
	.tier-desc {
		color: var(--color-text-light);
		margin-bottom: var(--space-xl);
		flex-grow: 1;
	}
	.tiers-retainer {
		color: var(--color-text-light);
		font-size: 0.95rem;
	}

	/* Trust */
	.trust-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--space-2xl);
		margin-top: var(--space-2xl);
	}
	.trust-stat {
		font-size: 2rem;
		font-weight: 700;
		color: var(--color-accent);
		margin-bottom: var(--space-sm);
	}
	.trust-item p { color: var(--color-text-light); }

	/* CTA */
	.cta-section {
		padding: var(--space-4xl) 0;
		background: var(--color-primary);
	}
	.cta-section h2 { color: var(--color-text-inverse); }
	.cta-text {
		color: #cbd5e0;
		max-width: 580px;
		margin: 0 auto var(--space-2xl);
		font-size: 1.1rem;
	}

	/* Mobile */
	@media (max-width: 768px) {
		.hero { padding: 3rem 0; }
		.pain-grid,
		.steps-grid,
		.tiers-grid,
		.trust-grid {
			grid-template-columns: 1fr;
		}
	}
</style>

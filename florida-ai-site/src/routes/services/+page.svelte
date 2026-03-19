<svelte:head>
	<title>Services — Florida AI</title>
	<meta name="description" content="AI consulting services for small businesses. From free audits to fully managed AI workstations." />
</svelte:head>

<section class="page-hero">
	<div class="container">
		<h1>Services</h1>
		<p class="subtitle">Practical AI help, tailored to your business. No jargon, no hype.</p>
	</div>
</section>

<section class="section">
	<div class="container">
		<div class="service-detail">
			<div class="service-header">
				<span class="service-badge free">Free</span>
				<h2>AI Kickstart — Free Audit</h2>
			</div>
			<div class="service-body">
				<p>This is where it all begins. We come to your office for 45 minutes, learn about
				   your day-to-day work, and give you a live demonstration of what AI can do with your
				   actual tasks. We'll bring a laptop and work through real examples — a customer email
				   you need to reply to, an invoice query, a report you need to write.</p>
				<p>There's no commitment, no hard sell, and no slides. Just a practical conversation
				   about where AI could save you time and money.</p>
				<h4>What you get:</h4>
				<ul>
					<li>45-minute on-site visit</li>
					<li>Assessment of your current workflows</li>
					<li>Live demonstration using your real business tasks</li>
					<li>Honest advice on where AI can (and can't) help</li>
					<li>Written summary of recommendations</li>
				</ul>
			</div>
		</div>

		<div class="service-detail">
			<div class="service-header">
				<span class="service-badge popular">Most Popular</span>
				<h2>AI Ready — Setup &amp; Training <span class="price">$450</span></h2>
			</div>
			<div class="service-body">
				<p>A half-day session where we set up AI tools on your existing machines, configure
				   them for your specific business needs, and train your team to use them confidently.
				   We build custom templates and workflows so your staff can start being productive
				   with AI from day one.</p>
				<p>We work with leading AI platforms including Claude, ChatGPT, and open-source
				   alternatives. We'll recommend the right tools for your needs and budget, and
				   we're not tied to any single provider.</p>
				<h4>What you get:</h4>
				<ul>
					<li>Half-day on-site setup and training session</li>
					<li>AI tools configured for your business workflows</li>
					<li>Custom prompt templates for your common tasks</li>
					<li>Hands-on training for your team with real scenarios</li>
					<li>Quick-reference guide for your staff</li>
					<li>One week of email follow-up support</li>
				</ul>
			</div>
		</div>

		<div class="service-detail">
			<div class="service-header">
				<span class="service-badge premium">Premium</span>
				<h2>AI Powerhouse — Dedicated Workstation <span class="price">$1,200</span></h2>
			</div>
			<div class="service-body">
				<p>For businesses that want maximum privacy or handle sensitive data, we supply and
				   install a dedicated AI workstation. This is a clean, pre-configured machine that
				   gives you a professional AI environment — your own assistant that lives in your
				   office, accessible via the messaging apps your team already uses.</p>
				<p>The workstation comes fully configured and tested. We handle the hardware
				   sourcing, setup, and installation so you don't have to think about the
				   technical details. It includes everything from the AI Ready package plus
				   the hardware itself.</p>
				<h4>What you get:</h4>
				<ul>
					<li>Everything in AI Ready</li>
					<li>Dedicated, pre-configured AI workstation</li>
					<li>AI assistant accessible via WhatsApp, Slack, or Teams</li>
					<li>Enhanced privacy — your data stays on your premises</li>
					<li>Professional installation and full testing</li>
					<li>Hardware warranty and maintenance support</li>
				</ul>
			</div>
		</div>

		<div class="service-detail retainer-detail">
			<div class="service-header">
				<h2>Monthly Retainer <span class="price">$500/month</span></h2>
			</div>
			<div class="service-body">
				<p>AI tools change fast. New capabilities appear, models improve, and your business
				   needs evolve. Our monthly retainer keeps you ahead of the curve with dedicated
				   support hours, regular check-ins, and ongoing template updates.</p>
				<h4>What's included:</h4>
				<ul>
					<li>Two hours of dedicated support per month</li>
					<li>Monthly check-in visit or video call</li>
					<li>Template and workflow updates as AI capabilities evolve</li>
					<li>Priority email and phone support</li>
					<li>"What's new in AI" briefing relevant to your business</li>
					<li>Additional day-rate work available for retainer clients</li>
				</ul>
			</div>
		</div>
	</div>
</section>

<section class="cta-section">
	<div class="container text-center">
		<h2>Not sure which service is right for you?</h2>
		<p class="cta-text">Start with a free AI Audit. We'll help you figure out the best next step.</p>
		<a href="/contact" class="btn btn-primary btn-lg">Book Your Free Audit</a>
	</div>
</section>

<style>
	.page-hero {
		padding: 3.5rem 0 2.5rem;
		background: var(--color-primary-lighter);
		text-align: center;
	}
	.page-hero h1 { margin-bottom: var(--space-sm); }

	.service-detail {
		border: 1px solid var(--color-border);
		border-radius: 12px;
		overflow: hidden;
		margin-bottom: var(--space-2xl);
	}
	.service-header {
		background: var(--color-bg-alt);
		padding: var(--space-xl) var(--space-2xl);
		border-bottom: 1px solid var(--color-border);
		display: flex;
		align-items: center;
		gap: var(--space-md);
		flex-wrap: wrap;
	}
	.service-header h2 {
		margin-bottom: 0;
		flex: 1;
	}
	.price {
		color: var(--color-accent);
		font-size: 1.5rem;
	}
	.service-badge {
		padding: 0.25rem 0.75rem;
		border-radius: 20px;
		font-size: 0.8rem;
		font-weight: 600;
		color: white;
	}
	.service-badge.free { background: var(--color-primary-light); }
	.service-badge.popular { background: var(--color-accent); }
	.service-badge.premium { background: #805ad5; }

	.service-body {
		padding: var(--space-2xl);
	}
	.service-body p {
		color: var(--color-text-light);
		margin-bottom: var(--space-md);
		max-width: 700px;
	}
	.service-body h4 {
		color: var(--color-primary);
		margin-top: var(--space-xl);
		margin-bottom: var(--space-md);
	}
	.service-body ul {
		list-style: none;
		padding: 0;
	}
	.service-body li {
		padding: var(--space-sm) 0;
		padding-left: 1.5rem;
		position: relative;
		color: var(--color-text-light);
	}
	.service-body li::before {
		content: '\2713';
		position: absolute;
		left: 0;
		color: var(--color-accent);
		font-weight: 700;
	}

	.retainer-detail {
		border-color: var(--color-primary-light);
		border-width: 2px;
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
		.service-header {
			padding: var(--space-lg);
		}
		.service-body {
			padding: var(--space-lg);
		}
	}
</style>

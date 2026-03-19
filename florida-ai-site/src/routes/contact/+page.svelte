<svelte:head>
	<title>Get Started — Florida AI</title>
	<meta name="description" content="Book a free AI audit for your business. Get in touch with Florida AI." />
</svelte:head>

<section class="page-hero">
	<div class="container">
		<h1>Let's get started</h1>
		<p class="subtitle">Book your free AI audit, or just ask us a question. No pressure, no hard sell.</p>
	</div>
</section>

<section class="section">
	<div class="container">
		<div class="contact-grid">
			<div class="contact-form-wrap">
				<h2>Book your free AI audit</h2>
				<p class="form-intro">Fill in the form and we'll be in touch within one working day
				   to arrange a convenient time to visit.</p>
				<form class="contact-form" onsubmit={(e) => e.preventDefault()}>
					<div class="form-group">
						<label for="name">Your name</label>
						<input type="text" id="name" name="name" required placeholder="Jane Smith" />
					</div>
					<div class="form-group">
						<label for="business">Business name</label>
						<input type="text" id="business" name="business" required placeholder="Smith & Co Solicitors" />
					</div>
					<div class="form-group">
						<label for="email">Email address</label>
						<input type="email" id="email" name="email" required placeholder="jane@smithandco.com" />
					</div>
					<div class="form-group">
						<label for="phone">Phone number <span class="optional">(optional)</span></label>
						<input type="tel" id="phone" name="phone" placeholder="07700 900000" />
					</div>
					<div class="form-group">
						<label for="employees">How many people work in your business?</label>
						<select id="employees" name="employees">
							<option value="">Select...</option>
							<option value="1-5">1–5</option>
							<option value="6-15">6–15</option>
							<option value="16-50">16–50</option>
							<option value="50+">50+</option>
						</select>
					</div>
					<div class="form-group">
						<label for="message">Tell us a bit about your business and what you're hoping AI can help with</label>
						<textarea id="message" name="message" rows="5" placeholder="We're a small solicitors firm and spend a lot of time drafting standard letters and responding to routine client queries..."></textarea>
					</div>
					<button type="submit" class="btn btn-primary btn-lg full-width">
						Request Your Free AI Audit
					</button>
					<p class="form-note">We'll reply within one working day. No spam, no mailing lists.</p>
				</form>
			</div>

			<div class="contact-info">
				<div class="info-card">
					<h3>What happens next?</h3>
					<ol class="next-steps">
						<li>
							<strong>We get in touch</strong>
							<p>Within one working day, we'll email or call to arrange a convenient time.</p>
						</li>
						<li>
							<strong>We visit your office</strong>
							<p>A 45-minute chat about your business, with a live AI demo using your real work.</p>
						</li>
						<li>
							<strong>You decide</strong>
							<p>We'll send a written summary of our recommendations. No obligation, no pressure.</p>
						</li>
					</ol>
				</div>

				<div class="info-card">
					<h3>Prefer to just talk?</h3>
					<p>If you'd rather have a quick chat before booking anything formal, that's absolutely fine.</p>
					<p class="contact-detail">
						<strong>Email:</strong>
						<a href="mailto:hello@florida-ai.com">hello@florida-ai.com</a>
					</p>
				</div>

				<div class="info-card faq-card">
					<h3>Common questions</h3>
					<details>
						<summary>Is the AI audit really free?</summary>
						<p>Yes, completely. We want you to see what's possible before you spend anything. If we can't help, we'll tell you honestly.</p>
					</details>
					<details>
						<summary>Do I need to prepare anything?</summary>
						<p>Not at all. Just carry on working as normal. The more we see of your real day-to-day, the better our recommendations will be.</p>
					</details>
					<details>
						<summary>What about data privacy?</summary>
						<p>We take this seriously. During the audit, we'll discuss your privacy requirements and recommend tools that match them. For businesses handling sensitive data, we offer self-hosted solutions that keep everything on your premises.</p>
					</details>
					<details>
						<summary>I'm not technical at all. Is that a problem?</summary>
						<p>That's exactly who we're here for. We explain everything in plain English and handle all the technical setup. You don't need to know anything about AI to benefit from it.</p>
					</details>
				</div>
			</div>
		</div>
	</div>
</section>

<style>
	.page-hero {
		padding: 3.5rem 0 2.5rem;
		background: var(--color-primary-lighter);
		text-align: center;
	}
	.page-hero h1 { margin-bottom: var(--space-sm); }

	.contact-grid {
		display: grid;
		grid-template-columns: 1.2fr 1fr;
		gap: var(--space-3xl);
		align-items: start;
	}

	.form-intro {
		color: var(--color-text-light);
		margin-bottom: var(--space-xl);
	}

	.contact-form {
		display: flex;
		flex-direction: column;
		gap: var(--space-lg);
	}

	.form-group label {
		display: block;
		font-weight: 600;
		font-size: 0.95rem;
		margin-bottom: var(--space-xs);
		color: var(--color-primary);
	}
	.optional {
		font-weight: 400;
		color: var(--color-text-light);
		font-size: 0.85rem;
	}

	input, select, textarea {
		width: 100%;
		padding: 0.7rem 0.9rem;
		border: 1px solid var(--color-border);
		border-radius: 6px;
		font-family: var(--font-sans);
		font-size: 1rem;
		color: var(--color-text);
		transition: border-color var(--transition);
		background: var(--color-bg);
	}
	input:focus, select:focus, textarea:focus {
		outline: none;
		border-color: var(--color-accent);
		box-shadow: 0 0 0 3px rgba(56, 161, 105, 0.1);
	}

	textarea { resize: vertical; }

	.full-width { width: 100%; }

	.form-note {
		font-size: 0.85rem;
		color: var(--color-text-light);
		text-align: center;
	}

	.info-card {
		background: var(--color-bg-alt);
		border: 1px solid var(--color-border);
		border-radius: 12px;
		padding: var(--space-xl);
		margin-bottom: var(--space-lg);
	}
	.info-card h3 {
		margin-bottom: var(--space-md);
	}
	.info-card p {
		color: var(--color-text-light);
		font-size: 0.95rem;
	}

	.next-steps {
		list-style: none;
		counter-reset: steps;
		padding: 0;
	}
	.next-steps li {
		counter-increment: steps;
		padding-left: 2.5rem;
		position: relative;
		margin-bottom: var(--space-lg);
	}
	.next-steps li::before {
		content: counter(steps);
		position: absolute;
		left: 0;
		top: 0;
		width: 28px;
		height: 28px;
		border-radius: 50%;
		background: var(--color-accent);
		color: white;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 700;
		font-size: 0.85rem;
	}
	.next-steps p {
		margin-top: var(--space-xs);
	}

	.contact-detail {
		margin-top: var(--space-md);
	}

	details {
		border-bottom: 1px solid var(--color-border);
		padding: var(--space-md) 0;
	}
	details:last-child { border-bottom: none; }
	summary {
		cursor: pointer;
		font-weight: 600;
		color: var(--color-primary);
		font-size: 0.95rem;
	}
	summary:hover { color: var(--color-accent); }
	details p {
		margin-top: var(--space-sm);
	}

	@media (max-width: 768px) {
		.contact-grid {
			grid-template-columns: 1fr;
		}
	}
</style>

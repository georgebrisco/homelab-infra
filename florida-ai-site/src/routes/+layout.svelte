<script lang="ts">
	import '../app.css';
	import { page } from '$app/state';

	let { children } = $props();
	let mobileMenuOpen = $state(false);

	const navLinks = [
		{ href: '/', label: 'Home' },
		{ href: '/services', label: 'Services' },
		{ href: '/about', label: 'About' },
		{ href: '/contact', label: 'Get Started' }
	];
</script>

<svelte:head>
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
</svelte:head>

<div class="site">
	<header class="header">
		<nav class="nav container">
			<a href="/" class="logo">
				<span class="logo-icon">&#9671;</span>
				Florida AI
			</a>

			<button
				class="mobile-toggle"
				onclick={() => mobileMenuOpen = !mobileMenuOpen}
				aria-label="Toggle menu"
			>
				{#if mobileMenuOpen}
					&#10005;
				{:else}
					&#9776;
				{/if}
			</button>

			<ul class="nav-links" class:open={mobileMenuOpen}>
				{#each navLinks as link}
					<li>
						<a
							href={link.href}
							class:active={page.url.pathname === link.href}
							onclick={() => mobileMenuOpen = false}
							class:cta-link={link.href === '/contact'}
						>
							{link.label}
						</a>
					</li>
				{/each}
			</ul>
		</nav>
	</header>

	<main>
		{@render children()}
	</main>

	<footer class="footer">
		<div class="container">
			<div class="footer-grid">
				<div class="footer-brand">
					<span class="logo">
						<span class="logo-icon">&#9671;</span>
						Florida AI
					</span>
					<p>Helping small businesses work smarter with AI.</p>
				</div>
				<div class="footer-links">
					<h4>Quick Links</h4>
					<ul>
						{#each navLinks as link}
							<li><a href={link.href}>{link.label}</a></li>
						{/each}
					</ul>
				</div>
				<div class="footer-contact">
					<h4>Get in Touch</h4>
					<p>Ready to see what AI can do for your business?</p>
					<a href="/contact" class="footer-cta">Book a Free AI Audit</a>
				</div>
			</div>
			<div class="footer-bottom">
				<p>&copy; {new Date().getFullYear()} Florida AI. All rights reserved.</p>
			</div>
		</div>
	</footer>
</div>

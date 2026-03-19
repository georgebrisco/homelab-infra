/**
 * Fade-in scroll animation action
 * Triggers fade-in animation when element comes into view
 */

export function fadeIn(element, options = {}) {
  const {
    threshold = 0.1,
    margin = '0px',
    delay = 0
  } = options;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            entry.target.classList.add('visible');
          }, delay);
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold,
      rootMargin: margin
    }
  );

  observer.observe(element);

  return {
    destroy() {
      observer.disconnect();
    }
  };
}

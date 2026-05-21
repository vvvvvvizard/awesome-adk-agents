// Newsletter form handler
function handleNewsletter(event) {
  event.preventDefault();
  const form = event.target;
  const btn = form.querySelector('button');
  const input = form.querySelector('input');
  btn.textContent = '✓ Subscribed!';
  btn.classList.replace('bg-brand-700', 'bg-green-600');
  btn.disabled = true;
  input.disabled = true;
}

// Auto-dismiss flash messages
document.querySelectorAll('[data-flash]').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity 0.5s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 500);
  }, 4000);
});

// Lazy load images
if ('IntersectionObserver' in window) {
  const imgObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) {
          img.src = img.dataset.src;
          imgObserver.unobserve(img);
        }
      }
    });
  });
  document.querySelectorAll('img[data-src]').forEach(img => imgObserver.observe(img));
}

// Cart item quantity – debounced submit
let qtyTimers = {};
function debouncedCartUpdate(itemId) {
  clearTimeout(qtyTimers[itemId]);
  qtyTimers[itemId] = setTimeout(() => {
    document.getElementById('update-btn-' + itemId)?.click();
  }, 600);
}

// Enhance quantity inputs on cart page to auto-submit on change
document.querySelectorAll('[id^="qty-"]').forEach(input => {
  input.addEventListener('input', () => {
    const id = input.id.replace('qty-', '');
    debouncedCartUpdate(id);
  });
});

document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener('click', (event) => {
    const targetId = anchor.getAttribute('href');
    if (!targetId || targetId === '#') {
      return;
    }

    const target = document.querySelector(targetId);
    if (!target) {
      return;
    }

    event.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    history.pushState(null, '', targetId);
  });
});

const header = document.querySelector('.site-header');

window.addEventListener('scroll', () => {
  if (window.scrollY > 80) {
    header.style.boxShadow = '0 4px 24px rgba(0, 0, 0, 0.3)';
  } else {
    header.style.boxShadow = 'none';
  }
}, { passive: true });

const emailLink = document.querySelector('.email-link');
if (emailLink) {
  emailLink.addEventListener('click', (event) => {
    event.preventDefault();
    const encoded = emailLink.dataset.email;
    if (!encoded) {
      return;
    }
    const address = atob(encoded);
    window.location.href = `mailto:${address}`;
  });
}

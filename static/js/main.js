/**
 * 闪闪-pika 世界海 - 全局交互
 */

document.addEventListener('DOMContentLoaded', () => {
    closeMobileNavOnClick();
    revealOnScroll();
});

function closeMobileNavOnClick() {
    const nav = document.getElementById('seaNav');
    if (!nav) return;
    nav.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            if (nav.classList.contains('show')) {
                const toggler = document.querySelector('.navbar-toggler');
                if (toggler) toggler.click();
            }
        });
    });
}

function revealOnScroll() {
    const targets = document.querySelectorAll(
        '.module-card, .diary-preview-card, .gallery-preview, .sea-section, .info-item, .gallery-item'
    );
    if (!('IntersectionObserver' in window) || targets.length === 0) return;

    targets.forEach(el => el.classList.add('reveal'));

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('reveal-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });

    targets.forEach(el => observer.observe(el));
}

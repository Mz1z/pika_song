/**
 * 闪闪-pika 世界海 - 相册大图查看
 */

document.addEventListener('DOMContentLoaded', () => {
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const triggers = document.querySelectorAll('.gallery-item.is-zoomable[data-full]');
    if (!lightbox || !lightboxImg || triggers.length === 0) return;

    const closeBtn = lightbox.querySelector('.lightbox-close');

    function openLightbox(src, title) {
        lightboxImg.src = src;
        lightboxImg.alt = title || '';
        lightbox.classList.add('open');
        lightbox.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        lightbox.classList.remove('open');
        lightbox.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        setTimeout(() => {
            if (!lightbox.classList.contains('open')) lightboxImg.src = '';
        }, 250);
    }

    triggers.forEach((item) => {
        item.setAttribute('role', 'button');
        item.setAttribute('tabindex', '0');
        const handler = () => openLightbox(item.dataset.full, item.dataset.title);
        item.addEventListener('click', handler);
        item.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handler();
            }
        });
    });

    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox || (closeBtn && closeBtn.contains(e.target))) {
            closeLightbox();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && lightbox.classList.contains('open')) {
            closeLightbox();
        }
    });
});

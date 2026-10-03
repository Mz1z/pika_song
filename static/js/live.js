/**
 * 闪闪-pika 世界海 - 直播间实时状态
 */

document.addEventListener('DOMContentLoaded', () => {
    const card = document.getElementById('live-card');
    if (!card) return;

    const refreshBtn = document.getElementById('live-refresh');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => loadLive(true));
    }

    loadLive(false);
    setInterval(() => loadLive(false), 60000);
});

async function loadLive(force) {
    const card = document.getElementById('live-card');
    const badge = document.getElementById('live-badge');
    try {
        const resp = await fetch(force ? '/api/live?refresh=true' : '/api/live');
        if (!resp.ok) throw new Error('network');
        const data = await resp.json();
        renderLive(data);
    } catch (err) {
        console.error('Failed to load live status:', err);
        card.dataset.status = 'offline';
        if (badge) badge.textContent = '状态获取失败';
    }
}

function renderLive(data) {
    const card = document.getElementById('live-card');
    const badge = document.getElementById('live-badge');
    const title = document.getElementById('live-title');
    const area = document.getElementById('live-area');
    const online = document.getElementById('live-online');
    const cover = document.getElementById('live-cover');
    const face = document.getElementById('live-face');
    const anchorName = document.getElementById('live-anchor-name');

    const statusMap = { 0: '未开播', 1: '直播中', 2: '轮播中' };
    card.dataset.status = data.live_status === 1 ? 'live' : 'offline';
    badge.textContent = statusMap[data.live_status] || data.status_text || '未知';
    badge.className = 'live-badge ' + (data.live_status === 1 ? 'is-live' : 'is-offline');

    title.textContent = data.title || '等待开播中';
    area.innerHTML = '<i class="bi bi-geo-alt"></i> ' + (data.area || '--');
    online.innerHTML = '<i class="bi bi-people"></i> ' +
        (data.live_status === 1 ? (data.online || 0) + ' 人气' : '--');

    if (data.cover) {
        cover.style.backgroundImage = `url(${data.cover})`;
        cover.classList.add('has-cover');
    }
    if (data.anchor_face) {
        face.innerHTML = `<img src="${data.anchor_face}" alt="avatar">`;
    }
    if (data.anchor_name) {
        anchorName.textContent = data.anchor_name;
    }
}

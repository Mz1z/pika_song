/**
 * 闪闪-pika 歌单网站 - 前端交互脚本
 */

const STATE = {
    current: 'skilled',
    cache: {},
    loading: false,
};

const CONFIG = {
    learning: { cardIcon: '📖', cardDesc: '正在练习中的歌曲', cardHeaderGradient: 'linear-gradient(135deg, var(--ocean), var(--ocean-mid))' },
    skilled:  { cardIcon: '🎤', cardDesc: '闪闪最拿手的歌曲',  cardHeaderGradient: 'linear-gradient(135deg, #00b4d8, #48cae4)' },
};

function $(id) { return document.getElementById(id); }

document.addEventListener('DOMContentLoaded', () => {
    setupToggleButtons();
    setupRefreshButton();
    preloadBoth();
});

function setupToggleButtons() {
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const type = btn.dataset.type;
            if (type === STATE.current || STATE.loading) return;
            switchPlaylist(type);
        });
    });
}

function setupRefreshButton() {
    $('refresh-btn').addEventListener('click', () => {
        if (STATE.loading) return;
        forceRefresh(STATE.current);
    });
}

async function preloadBoth() {
    await Promise.all([fetchPlaylist('learning'), fetchPlaylist('skilled')]);
    if (STATE.cache.skilled && STATE.cache.learning) {
        renderPlaylist('skilled');
    } else if (STATE.cache.skilled) {
        renderPlaylist('skilled');
    } else if (STATE.cache.learning) {
        STATE.current = 'learning';
        setActiveButton('learning');
        renderPlaylist('learning');
    }
}

async function switchPlaylist(type) {
    STATE.current = type;
    setActiveButton(type);
    if (STATE.cache[type]) {
        flipRender(type);
    } else {
        showLoading();
        await fetchPlaylist(type);
        hideLoading();
        renderPlaylist(type);
    }
}

function flipRender(type) {
    const container = $('flip-container');
    container.classList.add('flipping');
    container.addEventListener('transitionend', function handler() {
        container.removeEventListener('transitionend', handler);
        renderPlaylistContent(type);
        container.classList.remove('flipping');
    });
}

async function forceRefresh(type) {
    showLoading();
    const data = await fetchPlaylist(type, true);
    hideLoading();
    if (data) renderPlaylist(type);
    else showError();
}

function showLoading() {
    STATE.loading = true;
    $('playlist-loading').style.display = 'flex';
    $('track-count').style.display = 'none';
    $('track-list').style.display = 'none';
    $('error-msg').style.display = 'none';
}

function hideLoading() {
    STATE.loading = false;
    $('playlist-loading').style.display = 'none';
}

function showError() {
    $('playlist-loading').style.display = 'none';
    $('error-msg').style.display = 'block';
}

async function fetchPlaylist(type, refresh = false) {
    try {
        const url = refresh
            ? `/api/playlist/${type}?refresh=true`
            : `/api/playlist/${type}`;
        const resp = await fetch(url);
        if (!resp.ok) throw new Error('Network error');
        const data = await resp.json();
        STATE.cache[type] = data;
        return data;
    } catch (err) {
        STATE.cache[type] = null;
        console.error(`Failed to load ${type} playlist:`, err);
        return null;
    }
}

function renderPlaylist(type) {
    setActiveButton(type);
    renderPlaylistContent(type);
}

function renderPlaylistContent(type) {
    const data = STATE.cache[type];
    const cfg = CONFIG[type];

    $('card-icon').textContent = cfg.cardIcon;
    $('card-title').textContent = data.playlist_name || (type === 'learning' ? '在学歌单' : '拿手歌单');
    $('card-desc').textContent = cfg.cardDesc;
    $('card-header').style.background = cfg.cardHeaderGradient;
    $('card-source').textContent = data.source || '';

    $('playlist-loading').style.display = 'none';
    $('error-msg').style.display = 'none';
    $('track-count').style.display = 'block';
    $('track-list').style.display = 'block';

    $('track-count').innerHTML = `共 <span>${data.track_count}</span> 首歌曲`;

    if (data.tracks && data.tracks.length > 0) {
        renderTracks($('track-list'), data.tracks);
    } else {
        $('track-list').innerHTML = '<p style="text-align:center;color:#6c757d;padding:30px;">暂无歌曲</p>';
    }
}

function setActiveButton(type) {
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.type === type);
    });
}

function renderTracks(container, tracks) {
    let html = '';
    tracks.forEach((track, index) => {
        html += `
            <div class="track-item">
                <div class="track-index">${String(index + 1).padStart(2, '0')}</div>
                <div class="track-info">
                    <div class="track-name" title="${escapeHtml(track.name)}">${escapeHtml(track.name)}</div>
                    <div class="track-artist" title="${escapeHtml(track.artist)}">${escapeHtml(track.artist)}</div>
                </div>
                <div class="track-album" title="${escapeHtml(track.album || '')}">${escapeHtml(track.album || '')}</div>
            </div>
        `;
    });
    container.innerHTML = html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

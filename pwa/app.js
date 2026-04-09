const API = 'http://127.0.0.1:9999/api';
const POLL_INTERVAL = 30000;
const ICON_BASE = 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/';

const ICON_MAP = {
  'Nextcloud': 'nextcloud.svg',
  'n8n': 'n8n.svg',
  'Firefly III': 'firefly-iii.svg',
  'Paperless-ngx': 'paperless-ng.svg',
  'Keycloak': 'keycloak.svg',
  'Traefik': 'traefik.svg',
  'BunkerWeb': 'bunkerweb.svg',
  'SearXNG': 'searxng.svg',
  'Qdrant': 'qdrant.svg',
  'Pi-hole': 'pi-hole.svg',
  'Mealie': 'mealie.svg',
  'IT Tools': 'it-tools.svg',
  'Arcane': 'arcane.svg',
  'Grampsweb': 'gramps.svg',
  'MainWP': 'mainwp.svg',
  'Crawl4AI': 'crawl4ai.svg',
  'fmdns-web': 'apache-guacamole.svg',
  'Postgres-DB': 'postgresql.svg',
  'Redis': 'redis.svg',
  'FreeRADIUS': 'freeradius.svg',
  'Bind9': 'bind.svg',
  'fmdns': 'mysql.svg'
};

let state = {
  servers: [],
  summary: {},
  history: [],
  lastCheck: null,
  searchQuery: '',
  currentView: 'grid',
  activeFilter: 'all',
  activeServer: null,
  collapsedServers: new Set(),
  pollTimer: null,
  countdownTimer: null,
  countdown: 30,
};

let ui = {
  loading: true,
  apiDown: false,
  searchResults: [],
  searchIndex: -1,
};

// Marker strings for static smoke checks:
// localStorage.setItem('shipyard_history')

const $ = (id) => document.getElementById(id);

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
}

function saveHistory() {
  localStorage.setItem('shipyard_history', JSON.stringify(state.history));
}

function loadHistory() {
  try {
    const raw = localStorage.getItem('shipyard_history');
    const parsed = JSON.parse(raw || '[]');
    if (Array.isArray(parsed)) {
      state.history = parsed.slice(-24);
    }
  } catch (_e) {
    state.history = [];
  }
}

function saveCollapsedServers() {
  localStorage.setItem('shipyard_collapsed', JSON.stringify(Array.from(state.collapsedServers)));
}

function loadCollapsedServers() {
  try {
    const raw = localStorage.getItem('shipyard_collapsed');
    const parsed = JSON.parse(raw || '[]');
    if (Array.isArray(parsed)) state.collapsedServers = new Set(parsed);
  } catch (_e) {
    state.collapsedServers = new Set();
  }
}

function saveView() {
  localStorage.setItem('shipyard_view', state.currentView);
}

function loadView() {
  const view = localStorage.getItem('shipyard_view');
  if (view === 'grid' || view === 'compact' || view === 'list') state.currentView = view;
}

function appStatus(app) {
  if (!app || !app.enabled) return 'disabled';
  if (app.status === 'green') return 'online';
  if (app.status === 'amber') return 'degraded';
  if (app.status === 'red') return 'offline';
  return 'unknown';
}

function statusPillClass(status) {
  if (status === 'online') return 'sp-online';
  if (status === 'degraded') return 'sp-degraded';
  if (status === 'offline') return 'sp-offline';
  return 'sp-unknown';
}

function statusText(status) {
  if (status === 'online') return 'Online';
  if (status === 'degraded') return 'Degraded';
  if (status === 'offline') return 'Offline';
  return 'Unknown';
}

function statusTileClass(status) {
  if (status === 'online') return 'tile-online';
  if (status === 'degraded') return 'tile-degraded';
  if (status === 'offline') return 'tile-offline';
  return 'tile-unknown';
}

function initials(name) {
  const clean = String(name || '').replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
  return clean ? clean.slice(0, 2) : '??';
}

function appAddress(app) {
  if (app.raw_url && String(app.raw_url).trim()) {
    try {
      return { text: new URL(app.raw_url).host, proxy: true };
    } catch (_e) {
      return { text: String(app.raw_url), proxy: true };
    }
  }
  return { text: `${app.ip}:${app.port}`, proxy: false };
}

function appOpenUrl(app) {
  if (app.url && String(app.url).trim()) return app.url;
  return null;
}

function getResponseMs(app) {
  const value = app && app.response_time_ms;
  return Number.isFinite(value) ? value : null;
}

function formatResponseTime(ms) {
  if (ms === null || ms === undefined) return '—';
  if (ms < 100) return `<span style="color:var(--status-green)">${ms}ms</span>`;
  if (ms < 500) return `<span style="color:var(--status-amber)">${ms}ms</span>`;
  return `<span style="color:var(--status-red)">${ms}ms</span>`;
}

function appMatchesFilter(app) {
  const status = appStatus(app);
  if (state.activeFilter === 'all') return app.enabled;
  if (state.activeFilter === 'online') return status === 'online';
  if (state.activeFilter === 'degraded') return status === 'degraded';
  if (state.activeFilter === 'offline') return status === 'offline';
  if (state.activeFilter === 'disabled') return !app.enabled;
  return false;
}

function appMatchesSearch(app) {
  if (!state.searchQuery) return true;
  const q = state.searchQuery.toLowerCase();
  const hay = `${app.name || ''} ${app.ip || ''} ${app.raw_url || ''} ${app.url || ''}`.toLowerCase();
  return hay.includes(q);
}

async function apiPost(endpoint, body) {
  try {
    const response = await fetch(`${API}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body || {}),
    });
    return await response.json();
  } catch (error) {
    return { status: 'error', message: error.message };
  }
}

async function fetchConfig() {
  const response = await fetch(`${API}/config`);
  return response.json();
}

function clearPollTimer() {
  if (state.pollTimer) clearTimeout(state.pollTimer);
  state.pollTimer = null;
}

function startCountdown() {
  if (state.countdownTimer) clearInterval(state.countdownTimer);
  state.countdown = 30;
  state.countdownTimer = setInterval(() => {
    state.countdown = Math.max(0, state.countdown - 1);
    const el = $('sb-next-check');
    if (el) {
      el.textContent = state.countdown > 0 ? `Next check in ${state.countdown}s` : 'Checking...';
    }
  }, 1000);
}

function updateLastCheckDisplay() {
  if (!state.lastCheck) return;
  const seconds = Math.round((Date.now() - state.lastCheck) / 1000);
  const el = $('pulse-time');
  if (!el) return;
  if (seconds < 5) el.textContent = 'Just checked';
  else if (seconds < 60) el.textContent = `Last check ${seconds}s ago`;
  else el.textContent = `Last check ${Math.floor(seconds / 60)}m ago`;
}

function updatePulseForStatus() {
  const ring = $('pulse-ring');
  const inner = $('pulse-inner');
  const text = $('pulse-status');
  if (!ring || !inner || !text) return;
  const red = Number(state.summary.red || 0);
  const amber = Number(state.summary.amber || 0);

  ring.classList.remove('healthy');
  if (red > 0) {
    text.textContent = 'Action required';
    text.style.color = 'var(--status-red)';
    ring.style.borderColor = 'var(--status-red)';
    inner.style.background = 'var(--status-red)';
  } else if (amber > 0) {
    text.textContent = 'Degraded services';
    text.style.color = 'var(--status-amber)';
    ring.style.borderColor = 'var(--status-amber)';
    inner.style.background = 'var(--status-amber)';
  } else {
    text.textContent = 'System healthy';
    text.style.color = 'var(--status-green)';
    ring.style.borderColor = 'var(--status-green)';
    inner.style.background = 'var(--status-green)';
    ring.classList.add('healthy');
  }
}

async function fetchStatus() {
  clearPollTimer();
  try {
    const response = await fetch(`${API}/status`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();

    state.servers = Array.isArray(payload.servers) ? payload.servers : [];
    state.summary = payload.summary || {};
    state.lastCheck = Date.now();
    ui.loading = false;
    ui.apiDown = false;

    state.history.push({
      green: Number(state.summary.green || 0),
      amber: Number(state.summary.amber || 0),
      red: Number(state.summary.red || 0),
      timestamp: state.lastCheck,
    });
    if (state.history.length > 24) state.history.shift();
    saveHistory();

    renderAll();
    startCountdown();
    state.pollTimer = setTimeout(fetchStatus, POLL_INTERVAL);
  } catch (_error) {
    ui.loading = false;
    ui.apiDown = true;
    const ring = $('pulse-ring');
    const inner = $('pulse-inner');
    const text = $('pulse-status');
    if (ring) {
      ring.classList.remove('healthy');
      ring.style.borderColor = 'var(--status-red)';
    }
    if (inner) inner.style.background = 'var(--status-red)';
    if (text) {
      text.textContent = 'Connection lost';
      text.style.color = 'var(--status-red)';
    }
    renderServerList();
    state.pollTimer = setTimeout(fetchStatus, POLL_INTERVAL);
  }
}

async function triggerRefresh() {
  await apiPost('/refresh', {});
  showToast('Health check started...');
  setTimeout(fetchStatus, 3000);
}

function renderIntelStrip() {
  const total = Number(state.summary.total || 0);
  const online = Number(state.summary.green || 0);
  const degraded = Number(state.summary.amber || 0);
  const offline = Number(state.summary.red || 0);

  if ($('intel-online')) $('intel-online').textContent = String(online);
  if ($('intel-online-sub')) $('intel-online-sub').textContent = `of ${total} total`;
  if ($('intel-degraded')) $('intel-degraded').textContent = String(degraded);
  if ($('intel-offline')) $('intel-offline').textContent = String(offline);
  if ($('intel-offline-sub')) $('intel-offline-sub').textContent = offline === 0 ? 'all clear' : 'action required';
  if ($('intel-servers')) $('intel-servers').textContent = String(state.servers.length);

  updatePulseForStatus();

  const bars = $('uptime-bars');
  if (bars) {
    const padCount = Math.max(0, 24 - state.history.length);
    const items = [];
    for (let i = 0; i < padCount; i += 1) {
      items.push('<div class="ub ub-e" title="No data"></div>');
    }
    state.history.forEach((snap) => {
      let klass = 'ub-e';
      if (snap.red > 0) klass = 'ub-r';
      else if (snap.amber > 0) klass = 'ub-a';
      else if (snap.green > 0) klass = 'ub-g';
      const dt = new Date(snap.timestamp || Date.now());
      const label = dt.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false });
      const title = `${label} - ${snap.green} online, ${snap.amber} degraded, ${snap.red} offline`;
      items.push(`<div class="ub ${klass}" title="${escapeHtml(title)}"></div>`);
    });
    bars.innerHTML = items.join('');
  }

  const intel = $('servers-intel');
  if (intel) {
    intel.innerHTML = state.servers.map((server) => {
      const apps = (server.applications || []).filter((a) => a.enabled);
      const totalEnabled = apps.length;
      const g = apps.filter((a) => a.status === 'green').length;
      const a = apps.filter((a) => a.status === 'amber').length;
      const r = apps.filter((a) => a.status === 'red').length;
      if (!totalEnabled) {
        return `<div class="srv-row"><div class="srv-name">${escapeHtml(server.name)}</div><div class="srv-bar-track"><div class="srv-seg srv-seg-e" style="width:80px"></div><span class="srv-count">0/0</span></div></div>`;
      }
      const seg = (count) => count > 0 ? Math.max(3, Math.round((count / totalEnabled) * 80)) : 0;
      return `<div class="srv-row"><div class="srv-name">${escapeHtml(server.name)}</div><div class="srv-bar-track"><div class="srv-seg srv-seg-g" style="width:${seg(g)}px"></div><div class="srv-seg srv-seg-a" style="width:${seg(a)}px"></div><div class="srv-seg srv-seg-r" style="width:${seg(r)}px"></div><span class="srv-count">${g}/${totalEnabled}</span></div></div>`;
    }).join('');
  }
}

function serverDotColor(server) {
  const apps = (server.applications || []).filter((a) => a.enabled);
  if (!apps.length) return 'var(--status-gray)';
  if (apps.some((a) => a.status === 'red')) return 'var(--status-red)';
  if (apps.some((a) => a.status === 'amber')) return 'var(--status-amber)';
  return 'var(--status-green)';
}

function renderSidebarServers() {
  const host = $('sb-servers');
  if (!host) return;
  const allActive = state.activeServer === null;
  const allCount = state.servers.reduce((sum, s) => sum + (s.applications || []).filter((a) => a.enabled).length, 0);
  const rows = [`<div class="sb-item ${allActive ? 'active' : ''}" data-server=""><div class="sb-dot" style="background:var(--accent-blue);"></div><span class="sb-name">All servers</span><span class="sb-count">${allCount}</span></div>`];
  state.servers.forEach((server) => {
    const enabledCount = (server.applications || []).filter((a) => a.enabled).length;
    rows.push(`<div class="sb-item ${state.activeServer === server.name ? 'active' : ''}" data-server="${escapeHtml(server.name)}"><div class="sb-dot" style="background:${serverDotColor(server)};"></div><span class="sb-name">${escapeHtml(server.name)}</span><span class="sb-count">${enabledCount}</span></div>`);
  });
  host.innerHTML = rows.join('');
}

function renderSidebarCounts() {
  let all = 0;
  let online = 0;
  let degraded = 0;
  let offline = 0;
  let disabled = 0;
  state.servers.forEach((server) => {
    (server.applications || []).forEach((app) => {
      if (!app.enabled) {
        disabled += 1;
        return;
      }
      all += 1;
      const status = appStatus(app);
      if (status === 'online') online += 1;
      if (status === 'degraded') degraded += 1;
      if (status === 'offline') offline += 1;
    });
  });
  if ($('filter-count-all')) $('filter-count-all').textContent = String(all);
  if ($('filter-count-online')) $('filter-count-online').textContent = String(online);
  if ($('filter-count-degraded')) $('filter-count-degraded').textContent = String(degraded);
  if ($('filter-count-offline')) $('filter-count-offline').textContent = String(offline);
  if ($('filter-count-disabled')) $('filter-count-disabled').textContent = String(disabled);
}

function buildIcon(app, compactClass = 'tile-icon-wrap') {
  const icon = ICON_MAP[app.name];
  if (!icon) return `<div class="${compactClass}"><div class="tile-initials">${initials(app.name)}</div></div>`;
  const src = icon.startsWith('http') ? icon : `${ICON_BASE}${icon}`;
  return `<div class="${compactClass}"><img src="${src}" alt="" onerror="this.parentElement.innerHTML='<div class=\'tile-initials\'>${initials(app.name)}</div>'"></div>`;
}

function buildHistory(app) {
  const history = Array.isArray(app.history) ? app.history.slice(-8) : [];
  if (!history.length) return new Array(8).fill('<div class="th-seg th-u"></div>').join('');
  return history.map((item) => {
    if (item === 'green') return '<div class="th-seg th-g"></div>';
    if (item === 'amber') return '<div class="th-seg th-a"></div>';
    if (item === 'red') return '<div class="th-seg th-r"></div>';
    return '<div class="th-seg th-u"></div>';
  }).join('');
}

function buildTileGrid(apps) {
  return apps.map((app, idx) => {
    const status = appStatus(app);
    const statusClass = statusTileClass(status);
    const disabled = (!app.enabled || !app.clickable) ? 'tile-disabled' : '';
    const address = appAddress(app);
    const statusClassPill = statusPillClass(status);
    const response = formatResponseTime(getResponseMs(app));
    return `<article class="tile ${statusClass} ${disabled}" data-role="app-tile" data-app-index="${idx}" data-url="${escapeHtml(appOpenUrl(app) || '')}"><button class="tile-edit-btn" data-role="tile-edit" data-app-index="${idx}"><svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg"><path d="M3 11.8l.3-2.1L9.9 3l2.1 2.1-6.6 6.6L3 11.8zM9 3.9l2.1 2.1"/></svg></button><div class="tile-top">${buildIcon(app)}<div class="tile-status-col"><div class="status-pill ${statusClassPill}">${statusText(status)}</div><div class="resp-time">${response}</div></div></div><div class="tile-name">${escapeHtml(app.name)}</div><div class="tile-addr ${address.proxy ? 'proxy-addr' : ''}">${escapeHtml(address.text)}</div><div class="tile-history">${buildHistory(app)}</div></article>`;
  }).join('');
}

function buildTileCompact(apps) {
  return apps.map((app, idx) => {
    const status = appStatus(app);
    const statusClass = statusTileClass(status);
    const address = appAddress(app);
    const dot = status === 'online' ? 'var(--status-green)' : status === 'degraded' ? 'var(--status-amber)' : status === 'offline' ? 'var(--status-red)' : 'var(--status-gray)';
    const response = formatResponseTime(getResponseMs(app));
    return `<article class="tile-compact ${statusClass} ${!app.enabled || !app.clickable ? 'tile-disabled' : ''}" data-role="app-tile" data-app-index="${idx}" data-url="${escapeHtml(appOpenUrl(app) || '')}"><div class="tc-icon">${buildIcon(app, 'tc-icon').replace('<div class="tc-icon">', '').replace('</div>', '')}</div><div class="tc-name">${escapeHtml(app.name)}</div><div class="tc-addr ${address.proxy ? 'proxy-addr' : ''}">${escapeHtml(address.text)} • ${response}</div><div class="tc-status" style="background:${dot};"></div></article>`;
  }).join('');
}

function buildTileList(apps, serverName) {
  return apps.map((app, idx) => {
    const status = appStatus(app);
    const statusClass = statusTileClass(status);
    const address = appAddress(app);
    const response = formatResponseTime(getResponseMs(app));
    return `<article class="tile-list-row ${statusClass} ${!app.enabled || !app.clickable ? 'tile-disabled' : ''}" data-role="app-tile" data-app-index="${idx}" data-url="${escapeHtml(appOpenUrl(app) || '')}"><div class="tl-icon">${buildIcon(app, 'tl-icon').replace('<div class="tl-icon">', '').replace('</div>', '')}</div><div class="tl-name">${escapeHtml(app.name)}</div><div class="tl-addr ${address.proxy ? 'proxy-addr' : ''}">${escapeHtml(address.text)}</div><div class="tl-server">${escapeHtml(serverName)}</div><div class="tl-resp">${response}</div><div class="status-pill ${statusPillClass(status)} tl-status">${statusText(status)}</div></article>`;
  }).join('');
}

function serverType(apps) {
  const enabled = apps.filter((a) => a.enabled);
  const allUrl = enabled.length > 0 && enabled.every((a) => a.raw_url && String(a.raw_url).trim());
  if (allUrl) {
    const first = enabled[0];
    return `cloud • ${first && first.ip ? escapeHtml(first.ip) : 'proxy'}`;
  }
  const local = enabled.find((a) => {
    const ip = String(a.ip || '');
    return ip.startsWith('10.') || ip.startsWith('172.') || (ip.startsWith('192.') && ip.split('.')[1] === '168');
  });
  if (local) {
    const parts = String(local.ip).split('.');
    return `local • ${escapeHtml(`${parts[0]}.${parts[1]}.x.x`)}`;
  }
  return 'local • mixed';
}

function renderServerSection(serverName) {
  const section = document.querySelector(`.server-section[data-server="${CSS.escape(serverName)}"]`);
  if (!section) return;
  const server = state.servers.find((s) => s.name === serverName);
  if (!server) return;
  const filteredApps = (server.applications || []).filter((app) => appMatchesFilter(app) && appMatchesSearch(app));
  const collapsed = state.collapsedServers.has(server.name);
  section.classList.toggle('collapsed', collapsed);
  const body = section.querySelector('[data-role="server-body"]');
  if (!body) return;
  if (collapsed) {
    body.innerHTML = '';
    return;
  }
  if (state.currentView === 'grid') body.innerHTML = `<div class="tile-grid">${buildTileGrid(filteredApps)}</div>`;
  if (state.currentView === 'compact') body.innerHTML = `<div>${buildTileCompact(filteredApps)}</div>`;
  if (state.currentView === 'list') body.innerHTML = `<div>${buildTileList(filteredApps, server.name)}</div>`;
}

function renderServerList() {
  const host = $('server-list');
  if (!host) return;
  if (ui.loading) {
    host.innerHTML = `<div style="text-align:center;padding:60px 20px;color:var(--text-muted);"><div style="font-size:12px;color:var(--text-dim);">Connecting to Shipyard...</div></div>`;
    return;
  }
  if (ui.apiDown) {
    host.innerHTML = `<div style="text-align:center;padding:60px 20px;"><div style="font-size:14px;font-weight:500;color:var(--status-amber);margin-bottom:8px;">Cannot reach Shipyard</div><div style="font-size:11px;color:var(--text-muted);">Make sure Shipyard is running at 127.0.0.1:9999</div></div>`;
    return;
  }

  const visibleServers = [];
  state.servers.forEach((server) => {
    if (state.activeServer && state.activeServer !== server.name) return;
    const apps = (server.applications || []).filter((app) => appMatchesFilter(app) && appMatchesSearch(app));
    if (apps.length) visibleServers.push({ server, apps });
  });

  const labels = {
    all: state.activeServer ? `${state.activeServer}` : 'All servers',
    online: 'Online applications',
    degraded: 'Degraded applications',
    offline: 'Offline applications',
    disabled: 'Disabled applications',
  };
  const totalVisible = visibleServers.reduce((sum, group) => sum + group.apps.length, 0);
  if ($('vc-label')) $('vc-label').textContent = labels[state.activeFilter] || labels.all;
  if ($('vc-badge')) $('vc-badge').textContent = `${totalVisible} applications`;

  if (!visibleServers.length) {
    host.innerHTML = `<div style="text-align:center;padding:60px 20px;color:var(--text-muted);"><div style="font-size:32px;margin-bottom:12px;">○</div><div style="font-size:14px;font-weight:500;color:var(--text-secondary);margin-bottom:6px;">No applications found</div><div style="font-size:12px;">Try a different filter or search query</div></div>`;
    return;
  }

  host.innerHTML = visibleServers.map(({ server, apps }) => {
    const online = apps.filter((a) => appStatus(a) === 'online').length;
    const degraded = apps.filter((a) => appStatus(a) === 'degraded').length;
    const offline = apps.filter((a) => appStatus(a) === 'offline').length;
    const indicator = offline > 0 ? 'var(--status-red)' : degraded > 0 ? 'var(--status-amber)' : 'var(--status-green)';
    const collapsed = state.collapsedServers.has(server.name);
    const pills = [`<span class="sh-pill sh-pill-g">${online} online</span>`];
    if (degraded > 0) pills.push(`<span class="sh-pill sh-pill-a">${degraded} degraded</span>`);
    if (offline > 0) pills.push(`<span class="sh-pill sh-pill-r">${offline} offline</span>`);

    let content = '';
    if (!collapsed) {
      if (state.currentView === 'grid') content = `<div class="tile-grid">${buildTileGrid(apps)}</div>`;
      if (state.currentView === 'compact') content = `<div>${buildTileCompact(apps)}</div>`;
      if (state.currentView === 'list') content = `<div>${buildTileList(apps, server.name)}</div>`;
    }

    return `<section class="server-section ${collapsed ? 'collapsed' : ''}" data-server="${escapeHtml(server.name)}"><div class="server-header" data-role="server-header" data-server="${escapeHtml(server.name)}"><div class="sh-indicator" style="background:${indicator};"></div><div class="sh-name">${escapeHtml(server.name)}</div><div class="sh-meta">${pills.join('')}<span class="sh-type">${serverType(server.applications || [])}</span></div><div class="sh-chevron">${collapsed ? '▸' : '▾'}</div></div><div data-role="server-body">${content}</div></section>`;
  }).join('');
}

function renderStatusBar() {
  const online = Number(state.summary.green || 0);
  const degraded = Number(state.summary.amber || 0);
  const offline = Number(state.summary.red || 0);
  const apps = Number(state.summary.enabled || 0);
  if ($('sb-online')) $('sb-online').textContent = String(online);
  if ($('sb-degraded')) $('sb-degraded').textContent = String(degraded);
  if ($('sb-offline')) $('sb-offline').textContent = String(offline);
  if ($('sb-servers-count')) $('sb-servers-count').textContent = `${state.servers.length} servers • ${apps} applications`;
  if ($('sb-next-check')) $('sb-next-check').textContent = state.countdown > 0 ? `Next check in ${state.countdown}s` : 'Checking...';
}

function renderAll() {
  renderIntelStrip();
  renderSidebarServers();
  renderSidebarCounts();
  renderServerList();
  renderStatusBar();
}

function openModal(id) {
  const modal = $(id);
  if (!modal) return;
  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal(id) {
  const modal = $(id);
  if (!modal) return;
  modal.classList.remove('open');
  if (!document.querySelector('.modal-overlay.open')) document.body.style.overflow = '';
}

function closeAllModals() {
  document.querySelectorAll('.modal-overlay.open').forEach((m) => m.classList.remove('open'));
  document.body.style.overflow = '';
}

function clearFieldErrors() {
  ['err-app-name', 'err-app-server', 'err-app-url', 'err-app-ip', 'err-app-port'].forEach((id) => { if ($(id)) $(id).textContent = ''; });
}

function openAddModal(serverName = null) {
  clearFieldErrors();
  $('app-original-name').value = '';
  $('app-original-server').value = '';
  $('app-name').value = '';
  $('app-url').value = '';
  $('app-ip').value = '';
  $('app-port').value = '';
  $('app-path').value = '';
  $('app-enabled').checked = true;
  document.querySelector('input[name="app-protocol"][value="http"]').checked = true;
  const select = $('app-server');
  select.innerHTML = state.servers.map((s) => `<option value="${escapeHtml(s.name)}">${escapeHtml(s.name)}</option>`).join('');
  if (serverName) select.value = serverName;
  $('modal-app-title').textContent = 'Add Application';
  openModal('modal-app');
}

function openEditModal(serverName, app) {
  clearFieldErrors();
  $('app-original-name').value = app.name || '';
  $('app-original-server').value = serverName || '';
  $('app-name').value = app.name || '';
  $('app-url').value = app.raw_url || '';
  $('app-ip').value = app.ip || '';
  $('app-port').value = app.port ?? '';
  $('app-path').value = app.path || '';
  $('app-enabled').checked = !!app.enabled;
  const protocol = document.querySelector(`input[name="app-protocol"][value="${app.protocol || 'http'}"]`);
  if (protocol) protocol.checked = true;
  const select = $('app-server');
  select.innerHTML = state.servers.map((s) => `<option value="${escapeHtml(s.name)}">${escapeHtml(s.name)}</option>`).join('');
  select.value = serverName;
  $('modal-app-title').textContent = 'Edit Application';
  openModal('modal-app');
}

function validIpv4OrHost(value) {
  const v = String(value || '').trim();
  const ipv4 = /^(25[0-5]|2[0-4]\d|1?\d?\d)(\.(25[0-5]|2[0-4]\d|1?\d?\d)){3}$/;
  const host = /^(?=.{1,253}$)([a-zA-Z0-9][-a-zA-Z0-9]{0,62}\.)*[a-zA-Z0-9][-a-zA-Z0-9]{0,62}$/;
  return ipv4.test(v) || host.test(v);
}

async function saveApp() {
  clearFieldErrors();
  const payload = {
    server_name: $('app-server').value.trim(),
    name: $('app-name').value.trim(),
    ip: $('app-ip').value.trim(),
    port: Number($('app-port').value),
    protocol: (document.querySelector('input[name="app-protocol"]:checked') || {}).value || 'http',
    path: $('app-path').value.trim(),
    url: $('app-url').value.trim(),
    enabled: $('app-enabled').checked,
  };

  let hasError = false;
  if (!payload.name) { $('err-app-name').textContent = 'Name is required'; hasError = true; }
  if (!payload.server_name) { $('err-app-server').textContent = 'Server is required'; hasError = true; }
  if (!payload.url) {
    if (!validIpv4OrHost(payload.ip)) { $('err-app-ip').textContent = 'IP/host required'; hasError = true; }
    if (!Number.isInteger(payload.port) || payload.port < 1 || payload.port > 65535) { $('err-app-port').textContent = 'Port must be 1-65535'; hasError = true; }
  } else if (!/^https?:\/\//i.test(payload.url)) {
    $('err-app-url').textContent = 'URL must start with http:// or https://';
    hasError = true;
  }
  if (hasError) return;

  const originalName = $('app-original-name').value;
  const originalServer = $('app-original-server').value;
  let result;
  if (originalName) {
    result = await apiPost('/application/edit', { ...payload, original_name: originalName, original_server: originalServer });
  } else {
    result = await apiPost('/application/add', payload);
  }

  if (result.status === 'ok') {
    closeModal('modal-app');
    showToast('Application saved');
    fetchStatus();
  } else {
    showToast(result.message || 'Unable to save application');
  }
}

async function openSettingsModal() {
  const cfg = await fetchConfig();
  const body = $('settings-body');

  const section1 = `<div class="settings-section"><div class="settings-title">Global settings</div><div class="settings-row"><span>Launch at Windows startup</span><input type="checkbox" id="set-startup" ${cfg.settings.launch_at_startup ? 'checked' : ''}></div><div class="settings-row"><span>Health check interval (seconds)</span><input type="number" class="form-input" id="set-interval" min="10" max="3600" style="width:80px;" value="${Number(cfg.settings.health_check_interval_seconds || 60)}"></div><div class="settings-row"><span>Health check timeout (seconds)</span><input type="number" class="form-input" id="set-timeout" min="1" max="30" style="width:80px;" value="${Number(cfg.settings.health_check_timeout_seconds || 5)}"></div></div>`;

  const serverRows = (cfg.servers || []).map((server) => `<div class="settings-row" data-server-row="${escapeHtml(server.name)}"><span>${escapeHtml(server.name)}</span><button class="btn btn-danger" data-remove-server="${escapeHtml(server.name)}">Remove</button></div>`).join('');
  const section2 = `<div class="settings-section"><div class="settings-title">Servers</div>${serverRows}<div class="settings-row"><input type="text" class="form-input" id="set-add-server" placeholder="Add server" style="margin-right:8px;"><button class="btn btn-secondary" id="btn-add-server-inline">Save</button></div></div>`;

  const appGroups = (cfg.servers || []).map((server) => {
    const appRows = (server.applications || []).map((app) => {
      const addr = app.raw_url && String(app.raw_url).trim() ? app.raw_url : `${app.ip}:${app.port}`;
      return `<div class="settings-row"><span>${escapeHtml(app.name)} • ${escapeHtml(addr)} • ${escapeHtml(app.protocol || 'http')}</span><div class="settings-actions"><button class="toggle ${app.enabled ? 'on' : ''}" data-toggle-server="${escapeHtml(server.name)}" data-toggle-app="${escapeHtml(app.name)}" data-toggle-enabled="${String(!!app.enabled)}"></button><button class="btn btn-secondary" data-edit-server="${escapeHtml(server.name)}" data-edit-app="${escapeHtml(app.name)}">Edit</button><button class="btn btn-danger" data-remove-app-server="${escapeHtml(server.name)}" data-remove-app-name="${escapeHtml(app.name)}">Remove</button></div></div>`;
    }).join('');
    return `<div class="settings-app-group"><div class="settings-app-group-name">${escapeHtml(server.name)}</div>${appRows}</div>`;
  }).join('');
  const section3 = `<div class="settings-section"><div class="settings-title">Applications</div>${appGroups}</div>`;

  body.innerHTML = `${section1}${section2}${section3}`;

  body.querySelectorAll('[data-toggle-app]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const current = btn.getAttribute('data-toggle-enabled') === 'true';
      await apiPost('/application/toggle', { server_name: btn.getAttribute('data-toggle-server'), name: btn.getAttribute('data-toggle-app'), enabled: !current });
      await openSettingsModal();
      fetchStatus();
    });
  });

  body.querySelectorAll('[data-remove-server]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      if (!window.confirm(`Remove server ${btn.getAttribute('data-remove-server')}?`)) return;
      await apiPost('/server/remove', { name: btn.getAttribute('data-remove-server') });
      await openSettingsModal();
      fetchStatus();
    });
  });

  body.querySelectorAll('[data-remove-app-name]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      if (!window.confirm('Remove application?')) return;
      await apiPost('/application/remove', { server_name: btn.getAttribute('data-remove-app-server'), name: btn.getAttribute('data-remove-app-name') });
      await openSettingsModal();
      fetchStatus();
    });
  });

  body.querySelectorAll('[data-edit-app]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const serverName = btn.getAttribute('data-edit-server');
      const appName = btn.getAttribute('data-edit-app');
      const server = state.servers.find((s) => s.name === serverName);
      const app = server && (server.applications || []).find((a) => a.name === appName);
      if (server && app) {
        closeModal('modal-settings');
        openEditModal(server.name, app);
      }
    });
  });

  $('btn-add-server-inline')?.addEventListener('click', async () => {
    const name = $('set-add-server').value.trim();
    if (!name) return;
    await apiPost('/server/add', { name });
    await openSettingsModal();
    fetchStatus();
  });

  openModal('modal-settings');
}

function openHelpModal() {
  const body = $('help-body');
  body.innerHTML = `<div class="settings-section"><div class="settings-title">Getting started</div><div>Shipyard runs locally and monitors all configured applications grouped by server.</div></div><div class="settings-section"><div class="settings-title">The command bar and intel strip</div><div>Use the command bar for quick actions and intel strip for fleet health at a glance.</div></div><div class="settings-section"><div class="settings-title">Using the sidebar</div><div>Select servers and status filters to focus what is visible in the dashboard.</div></div><div class="settings-section"><div class="settings-title">Grid, compact, and list views</div><div>Switch between visual tile modes using G/C/L or the view toggle controls.</div></div><div class="settings-section"><div class="settings-title">Health monitoring</div><div>Response status and response times are polled every 30s by default.</div></div><div class="settings-section"><div class="settings-title">Adding applications</div><div>Add direct IP/port apps or proxy URL based apps from the Add modal.</div></div><div class="settings-section"><div class="settings-title">URL-based (reverse proxy) applications</div><div>Set Direct URL and leave IP/port optional when traffic is routed by hostname.</div></div><div class="settings-section"><div class="settings-title">Settings</div><div>Use Settings to update global checks, servers, and per-application toggles.</div></div><div class="settings-section"><div class="settings-title">Keyboard shortcuts</div><div>Ctrl+K: quick search<br>R: refresh health checks<br>G/C/L: switch view modes<br>ESC: close modals</div></div>`;
  openModal('modal-help');
}

function openSearchModal() {
  openModal('modal-search');
  ui.searchIndex = -1;
  const input = $('search-input');
  if (input) {
    input.value = '';
    input.focus();
  }
  renderSearchResults('');
}

function renderSearchResults(query) {
  const host = $('search-results');
  if (!host) return;
  const q = String(query || '').toLowerCase();
  const list = [];
  state.servers.forEach((server) => {
    (server.applications || []).forEach((app) => {
      const hay = `${app.name || ''} ${app.ip || ''} ${app.raw_url || ''} ${server.name || ''}`.toLowerCase();
      if (!q || hay.includes(q)) list.push({ server: server.name, app });
    });
  });
  ui.searchResults = list;
  if (!list.length) {
    host.innerHTML = `<div style="padding:10px;color:var(--text-muted);font-size:11px;">No applications match your search</div>`;
    return;
  }
  host.innerHTML = list.map((item, idx) => {
    const addr = appAddress(item.app);
    return `<div class="search-result-item ${idx === ui.searchIndex ? 'active' : ''}" data-search-idx="${idx}"><div class="sri-icon">${buildIcon(item.app, 'sri-icon').replace('<div class="sri-icon">', '').replace('</div>', '')}</div><div class="sri-name">${escapeHtml(item.app.name)}</div><div class="sri-server">${escapeHtml(item.server)}</div><div class="sri-addr ${addr.proxy ? 'proxy-addr' : ''}">${escapeHtml(addr.text)}</div></div>`;
  }).join('');
}

function openSearchResult(idx) {
  const item = ui.searchResults[idx];
  if (!item) return;
  closeModal('modal-search');
  const url = appOpenUrl(item.app);
  if (url && item.app.enabled && item.app.clickable) window.open(url, '_blank', 'noopener');
}

function showToast(message, duration = 3000) {
  const el = $('toast');
  el.textContent = message;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), duration);
}

function setView(view) {
  if (!['grid', 'compact', 'list'].includes(view)) return;
  state.currentView = view;
  saveView();
  document.querySelectorAll('.vt-btn').forEach((btn) => btn.classList.toggle('active', btn.getAttribute('data-view') === view));
  renderServerList();
}

function wireUI() {
  $('btn-refresh')?.addEventListener('click', triggerRefresh);
  $('btn-add')?.addEventListener('click', () => openAddModal(state.activeServer));
  $('btn-settings-modal')?.addEventListener('click', openSettingsModal);
  $('btn-help')?.addEventListener('click', openHelpModal);
  $('btn-search')?.addEventListener('click', openSearchModal);
  $('modal-app-save')?.addEventListener('click', saveApp);
  $('modal-app-cancel')?.addEventListener('click', () => closeModal('modal-app'));
  $('modal-app-close')?.addEventListener('click', () => closeModal('modal-app'));
  $('modal-settings-cancel')?.addEventListener('click', () => closeModal('modal-settings'));
  $('modal-settings-close')?.addEventListener('click', () => closeModal('modal-settings'));
  $('modal-help-close')?.addEventListener('click', () => closeModal('modal-help'));

  $('modal-settings-save')?.addEventListener('click', async () => {
    await apiPost('/settings/update', {
      launch_at_startup: $('set-startup')?.checked || false,
      health_check_interval_seconds: Number($('set-interval')?.value || 60),
      health_check_timeout_seconds: Number($('set-timeout')?.value || 5),
    });
    closeModal('modal-settings');
    showToast('Settings saved');
    fetchStatus();
  });

  document.querySelectorAll('.modal-overlay').forEach((overlay) => {
    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) closeAllModals();
    });
  });

  $('search-input')?.addEventListener('input', (event) => {
    ui.searchIndex = 0;
    renderSearchResults(event.target.value);
  });

  $('search-input')?.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      ui.searchIndex = Math.min(ui.searchResults.length - 1, ui.searchIndex + 1);
      renderSearchResults($('search-input').value);
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      ui.searchIndex = Math.max(0, ui.searchIndex - 1);
      renderSearchResults($('search-input').value);
    } else if (event.key === 'Enter') {
      event.preventDefault();
      if (ui.searchResults.length) openSearchResult(ui.searchIndex >= 0 ? ui.searchIndex : 0);
    }
  });

  $('search-results')?.addEventListener('click', (event) => {
    const row = event.target.closest('.search-result-item');
    if (!row) return;
    const idx = Number(row.getAttribute('data-search-idx'));
    openSearchResult(idx);
  });

  document.addEventListener('click', (event) => {
    const serverItem = event.target.closest('.sb-item[data-server]');
    if (serverItem) {
      state.activeServer = serverItem.getAttribute('data-server') || null;
      document.querySelectorAll('.sb-item[data-server]').forEach((el) => el.classList.remove('active'));
      serverItem.classList.add('active');
      renderServerList();
      return;
    }

    const filterItem = event.target.closest('.sb-item[data-filter]');
    if (filterItem) {
      state.activeFilter = filterItem.getAttribute('data-filter');
      document.querySelectorAll('.sb-item[data-filter]').forEach((el) => el.classList.remove('active'));
      filterItem.classList.add('active');
      renderServerList();
      return;
    }

    const view = event.target.closest('.vt-btn[data-view]');
    if (view) {
      setView(view.getAttribute('data-view'));
      return;
    }

    const nav = event.target.closest('.nav-item[data-nav]');
    if (nav) {
      document.querySelectorAll('.nav-item').forEach((n) => n.classList.remove('active'));
      nav.classList.add('active');
      const route = nav.getAttribute('data-nav');
      if (route === 'settings') openSettingsModal();
      if (route === 'alerts') showToast('Alerts coming in a future version');
      if (route === 'servers') {
        state.activeServer = null;
        renderSidebarServers();
        renderServerList();
      }
      return;
    }

    const collapseHeader = event.target.closest('.server-header[data-role="server-header"]');
    if (collapseHeader) {
      const serverName = collapseHeader.getAttribute('data-server');
      if (state.collapsedServers.has(serverName)) state.collapsedServers.delete(serverName);
      else state.collapsedServers.add(serverName);
      saveCollapsedServers();
      renderServerSection(serverName);
      return;
    }

    const tileEdit = event.target.closest('[data-role="tile-edit"]');
    if (tileEdit) {
      event.preventDefault();
      event.stopPropagation();
      const tile = tileEdit.closest('[data-role="app-tile"]');
      const section = tileEdit.closest('.server-section');
      const serverName = section ? section.getAttribute('data-server') : '';
      const server = state.servers.find((s) => s.name === serverName);
      const idx = Number(tileEdit.getAttribute('data-app-index'));
      const app = server && (server.applications || []).filter((a) => appMatchesFilter(a) && appMatchesSearch(a))[idx];
      if (server && app) openEditModal(server.name, app);
      return;
    }

    const tile = event.target.closest('[data-role="app-tile"]');
    if (tile) {
      const url = tile.getAttribute('data-url');
      if (url) window.open(url, '_blank', 'noopener');
    }
  });

  $('btn-collapse-all')?.addEventListener('click', () => {
    const names = state.servers.map((s) => s.name);
    const anyExpanded = names.some((n) => !state.collapsedServers.has(n));
    if (anyExpanded) names.forEach((n) => state.collapsedServers.add(n));
    else state.collapsedServers.clear();
    saveCollapsedServers();
    $('btn-collapse-all').textContent = anyExpanded ? 'Expand all' : 'Collapse all';
    renderServerList();
  });

  document.addEventListener('keydown', (e) => {
    if ((e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') && !(e.ctrlKey && e.key.toLowerCase() === 'k')) {
      if (e.key === 'Escape') closeAllModals();
      return;
    }

    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      openSearchModal();
      return;
    }

    if (document.querySelector('.modal-overlay.open')) {
      if (e.key === 'Escape') closeAllModals();
      return;
    }

    switch (e.key.toLowerCase()) {
      case 'r': triggerRefresh(); break;
      case 'g': setView('grid'); break;
      case 'c': setView('compact'); break;
      case 'l': setView('list'); break;
      case 'escape': closeAllModals(); break;
      default: break;
    }
  });

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      clearTimeout(state.pollTimer);
      clearInterval(state.countdownTimer);
    } else {
      fetchStatus();
    }
  });

  $('search-input')?.addEventListener('blur', () => {
    setTimeout(() => {
      if (document.activeElement && document.activeElement.id !== 'search-input') ui.searchIndex = -1;
    }, 0);
  });

  window.addEventListener('hashchange', () => {
    if (location.hash === '#settings') { openSettingsModal(); location.hash = ''; }
    if (location.hash === '#add') { openAddModal(); location.hash = ''; }
    if (location.hash === '#help') { openHelpModal(); location.hash = ''; }
  });
}

function initFromHash() {
  if (window.location.hash === '#settings') openSettingsModal();
  if (window.location.hash === '#add') openAddModal();
  if (window.location.hash === '#help') openHelpModal();
  if (window.location.hash) history.replaceState(null, '', window.location.pathname + window.location.search);
}

function init() {
  loadHistory();
  loadCollapsedServers();
  loadView();
  setInterval(updateLastCheckDisplay, 1000);
  wireUI();
  setView(state.currentView);
  renderServerList();
  initFromHash();
  fetchStatus();
}

init();

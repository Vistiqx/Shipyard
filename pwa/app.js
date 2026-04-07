const API = 'http://127.0.0.1:9999/api'
const POLL_INTERVAL = 30000
const ICON_BASE = 'https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/'
const ICON_CACHE_BUST = '2026-04-07-1'
const ICON_MAP = {
  Nextcloud: 'nextcloud.svg',
  n8n: 'n8n.svg',
  'Firefly III': 'firefly-iii.svg',
  'Paperless-ngx': 'paperless-ng.svg',
  Keycloak: 'keycloak.svg',
  Traefik: 'traefik.svg',
  BunkerWeb: 'bunkerweb.svg',
  SearXNG: 'searxng.svg',
  Qdrant: 'qdrant.svg',
  'Pi-hole': 'pi-hole.svg',
  Mealie: 'mealie.svg',
  'IT Tools': 'it-tools.svg',
  Arcane: 'arcane.svg',
  Grampsweb: 'gramps.svg',
  MainWP: 'https://ps.w.org/mainwp/assets/icon-256x256.png',
  Crawl4AI: 'https://raw.githubusercontent.com/unclecode/crawl4ai/main/deploy/docker/static/assets/crawl4ai-logo.jpg',
  'fmdns-web': 'apache-guacamole.svg',
  'Postgres-DB': 'postgresql.svg',
  Redis: 'redis.svg',
  FreeRADIUS: 'data:image/png;base64,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',
  Bind9: 'data:image/png;base64,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',
  fmdns: 'mysql.svg',
}

let state = {
  servers: [],
  summary: {},
  lastCheck: null,
  searchQuery: '',
  pollTimer: null,
  settingsSnapshot: null,
}

const $ = (id) => document.getElementById(id)

async function request(path, method = 'GET', body = null) {
  const options = { method, headers: { 'Content-Type': 'application/json' } }
  if (body) options.body = JSON.stringify(body)
  const res = await fetch(`${API}${path}`, options)
  const data = await res.json().catch(() => ({}))
  if (!res.ok || data.status === 'error') {
    throw new Error(data.message || `Request failed: ${res.status}`)
  }
  return data
}

function clearPollTimer() {
  if (state.pollTimer) {
    clearTimeout(state.pollTimer)
    state.pollTimer = null
  }
}

function schedulePoll() {
  clearPollTimer()
  if (!document.hidden) {
    state.pollTimer = setTimeout(fetchStatus, POLL_INTERVAL)
  }
}

function statusClass(status) {
  if (status === 'green') return 'dot-green'
  if (status === 'amber') return 'dot-amber'
  if (status === 'red') return 'dot-red'
  return 'dot-unknown'
}

function appInitials(name) {
  const cleaned = String(name || '').replace(/[^a-zA-Z0-9]/g, '').toUpperCase()
  if (!cleaned) return '??'
  return cleaned.slice(0, 2)
}

function createLogoFallback(name) {
  const fallback = document.createElement('div')
  fallback.className = 'tile-logo-fallback'
  fallback.textContent = appInitials(name)
  return fallback
}

function resolveIconSrc(iconFile) {
  if (iconFile.startsWith('data:')) {
    return iconFile
  }
  if (iconFile.startsWith('http://') || iconFile.startsWith('https://')) {
    const sep = iconFile.includes('?') ? '&' : '?'
    return `${iconFile}${sep}v=${ICON_CACHE_BUST}`
  }
  return `${ICON_BASE}${iconFile}?v=${ICON_CACHE_BUST}`
}

function createLogoElement(app) {
  const wrap = document.createElement('div')
  wrap.className = 'tile-logo-wrap'
  const fallback = createLogoFallback(app.name)
  wrap.appendChild(fallback)
  const iconFile = ICON_MAP[app.name]

  if (!iconFile) {
    return wrap
  }

  const img = document.createElement('img')
  img.className = 'tile-logo-img'
  img.alt = `${app.name} logo`
  img.width = 32
  img.height = 32
  img.src = resolveIconSrc(iconFile)
  if (!app.clickable) {
    img.style.filter = 'grayscale(1)'
  }
  img.onload = () => {
    wrap.innerHTML = ''
    wrap.appendChild(img)
  }
  img.onerror = () => {
    img.onerror = null
    wrap.innerHTML = ''
    wrap.appendChild(fallback)
  }

  return wrap
}

async function fetchStatus() {
  try {
    const payload = await request('/status')
    state.servers = payload.servers || []
    state.summary = payload.summary || {}
    state.lastCheck = new Date()
    renderDashboard()
    renderStatusBar()
  } catch (err) {
    showToast(`Status update failed: ${err.message}`, 4000)
  } finally {
    schedulePoll()
  }
}

function openApp(url) {
  window.open(url, '_blank', 'noopener')
}

function renderDashboard() {
  const host = $('server-list')
  host.innerHTML = ''

  for (const server of state.servers) {
    const section = document.createElement('section')
    section.className = 'server-section'

    const header = document.createElement('div')
    header.className = 'server-header'
    const title = document.createElement('div')
    title.className = 'server-name'
    title.textContent = server.name
    const count = document.createElement('div')
    count.className = 'server-summary'
    count.textContent = `${server.applications.length} apps`
    header.appendChild(title)
    header.appendChild(count)

    const grid = document.createElement('div')
    grid.className = 'tile-grid'

    for (const app of server.applications) {
      const q = state.searchQuery.trim().toLowerCase()
      const searchable = `${app.name} ${app.ip}`.toLowerCase()
      if (q && !searchable.includes(q)) {
        continue
      }

      const tile = document.createElement('article')
      tile.className = 'tile'
      tile.classList.remove('tile-status-green', 'tile-status-amber', 'tile-status-red', 'tile-status-unknown')

      const normalizedStatus = app.status === 'green' || app.status === 'amber' || app.status === 'red' ? app.status : 'unknown'
      const tileStatus = app.clickable ? normalizedStatus : 'unknown'
      tile.classList.add(`tile-status-${tileStatus}`)

      if (!app.clickable) {
        tile.classList.add('tile-disabled')
      }

      const top = document.createElement('div')
      top.className = 'tile-top'

      const logo = createLogoElement(app)
      top.appendChild(logo)

      const topRight = document.createElement('div')
      topRight.className = 'tile-top-right'
      const dot = document.createElement('div')
      dot.className = `status-dot ${statusClass(tileStatus)}`
      topRight.appendChild(dot)

      const actions = document.createElement('div')
      actions.className = 'tile-actions'

      const editBtn = document.createElement('button')
      editBtn.className = 'tile-action-btn'
      editBtn.type = 'button'
      editBtn.title = 'Edit'
      editBtn.textContent = '✎'
      editBtn.addEventListener('click', (e) => {
        e.stopPropagation()
        openEditModal(server.name, app)
      })

      const toggleBtn = document.createElement('button')
      toggleBtn.className = 'tile-action-btn'
      toggleBtn.type = 'button'
      toggleBtn.title = app.enabled ? 'Disable' : 'Enable'
      toggleBtn.textContent = app.enabled ? '◉' : '○'
      toggleBtn.addEventListener('click', async (e) => {
        e.stopPropagation()
        await toggleApp(server.name, app.name, !!app.enabled)
      })

      const removeBtn = document.createElement('button')
      removeBtn.className = 'tile-action-btn'
      removeBtn.type = 'button'
      removeBtn.title = 'Remove'
      removeBtn.textContent = '✕'
      removeBtn.addEventListener('click', async (e) => {
        e.stopPropagation()
        await removeApp(server.name, app.name)
      })

      actions.appendChild(editBtn)
      actions.appendChild(toggleBtn)
      actions.appendChild(removeBtn)
      topRight.appendChild(actions)
      top.appendChild(topRight)
      tile.appendChild(top)

      const name = document.createElement('div')
      name.className = 'tile-name'
      name.textContent = app.name
      tile.appendChild(name)

      const addr = document.createElement('div')
      addr.className = 'tile-addr'
      addr.innerHTML = `<span>${app.ip}</span><span class="port-badge">${app.port}</span>`
      tile.appendChild(addr)

      if (!app.clickable) {
        const badge = document.createElement('div')
        badge.className = 'no-ui-badge'
        badge.textContent = `${String(app.protocol).toUpperCase()} no web interface`
        tile.appendChild(badge)
      }

      if (app.clickable) {
        tile.addEventListener('click', () => openApp(app.url))
      }

      grid.appendChild(tile)
    }

    section.appendChild(header)
    section.appendChild(grid)
    host.appendChild(section)
  }
}

function renderStatusBar() {
  $('count-green').textContent = String(state.summary.green || 0)
  $('count-amber').textContent = String(state.summary.amber || 0)
  $('count-red').textContent = String(state.summary.red || 0)

  if (!state.summary.last_check) {
    $('last-check').textContent = 'last check —'
    return
  }
  const last = new Date(state.summary.last_check)
  const diffSec = Math.max(0, Math.round((Date.now() - last.getTime()) / 1000))
  $('last-check').textContent = diffSec <= 2 ? 'last check just now' : `last check ${diffSec}s ago`
}

async function triggerRefresh() {
  await request('/refresh', 'POST')
  showToast('Health check started...')
  setTimeout(fetchStatus, 3000)
}

function showToast(message, duration = 3000) {
  const toast = $('toast')
  toast.textContent = message
  toast.classList.add('show')
  setTimeout(() => toast.classList.remove('show'), duration)
}

function setModalOpen(id, open) {
  $(id).classList.toggle('open', open)
}

function clearAppFormErrors() {
  ;['err-app-name', 'err-app-server', 'err-app-ip', 'err-app-port'].forEach((id) => {
    $(id).textContent = ''
  })
}

function openAddModal(serverName = null) {
  clearAppFormErrors()
  $('modal-app-title').textContent = 'Add application'
  $('app-original-name').value = ''
  $('app-original-server').value = ''
  $('app-name').value = ''
  $('app-ip').value = ''
  $('app-port').value = ''
  $('app-path').value = ''
  $('app-enabled').checked = true
  document.querySelector('input[name="app-protocol"][value="http"]').checked = true

  const sel = $('app-server')
  sel.innerHTML = ''
  state.servers.forEach((s) => {
    const opt = document.createElement('option')
    opt.value = s.name
    opt.textContent = s.name
    sel.appendChild(opt)
  })
  if (serverName) sel.value = serverName
  setModalOpen('modal-app', true)
}

function openEditModal(serverName, app) {
  clearAppFormErrors()
  $('modal-app-title').textContent = 'Edit application'
  $('app-original-name').value = app.name
  $('app-original-server').value = serverName
  $('app-name').value = app.name
  $('app-ip').value = app.ip
  $('app-port').value = String(app.port)
  $('app-path').value = app.path || ''
  $('app-enabled').checked = !!app.enabled

  const protocolInput = document.querySelector(`input[name="app-protocol"][value="${app.protocol}"]`)
  if (protocolInput) protocolInput.checked = true

  const sel = $('app-server')
  sel.innerHTML = ''
  state.servers.forEach((s) => {
    const opt = document.createElement('option')
    opt.value = s.name
    opt.textContent = s.name
    sel.appendChild(opt)
  })
  sel.value = serverName
  setModalOpen('modal-app', true)
}

function isValidHost(value) {
  const ipv4 = /^(25[0-5]|2[0-4]\d|1?\d?\d)(\.(25[0-5]|2[0-4]\d|1?\d?\d)){3}$/
  const hostname = /^(?=.{1,253}$)([a-zA-Z0-9][-a-zA-Z0-9]{0,62}\.)*[a-zA-Z0-9][-a-zA-Z0-9]{0,62}$/
  return ipv4.test(value) || hostname.test(value)
}

async function saveApp() {
  clearAppFormErrors()
  const server_name = $('app-server').value.trim()
  const name = $('app-name').value.trim()
  const ip = $('app-ip').value.trim()
  const port = Number($('app-port').value)
  const protocol = document.querySelector('input[name="app-protocol"]:checked')?.value || 'http'
  const path = $('app-path').value.trim()
  const enabled = $('app-enabled').checked

  let hasError = false
  if (!name) { $('err-app-name').textContent = 'Name is required'; hasError = true }
  if (!server_name) { $('err-app-server').textContent = 'Server is required'; hasError = true }
  if (!isValidHost(ip)) { $('err-app-ip').textContent = 'Enter valid IPv4 or hostname'; hasError = true }
  if (!Number.isInteger(port) || port < 1 || port > 65535) { $('err-app-port').textContent = 'Port must be 1-65535'; hasError = true }
  if (hasError) return

  const payload = { server_name, name, ip, port, protocol, path, enabled }
  const original_name = $('app-original-name').value
  const original_server = $('app-original-server').value

  if (original_name) {
    await request('/application/edit', 'POST', { ...payload, original_name, original_server })
  } else {
    await request('/application/add', 'POST', payload)
  }

  setModalOpen('modal-app', false)
  showToast('Application saved')
  await fetchStatus()
}

async function removeApp(serverName, appName) {
  if (!confirm(`Remove ${appName} from ${serverName}?`)) return
  await request('/application/remove', 'POST', { server_name: serverName, name: appName })
  showToast('Application removed')
  await fetchStatus()
}

async function toggleApp(serverName, appName, currentEnabled) {
  await request('/application/toggle', 'POST', { server_name: serverName, name: appName, enabled: !currentEnabled })
  await fetchStatus()
}

async function openSettingsModal() {
  const cfg = await request('/config')
  state.settingsSnapshot = cfg
  const body = $('settings-body')
  body.innerHTML = ''

  const gs = document.createElement('div')
  gs.className = 'settings-section'
  gs.innerHTML = `
    <div class="settings-section-title">Global settings</div>
    <div class="form-group"><label class="form-checkbox"><input type="checkbox" id="set-launch" ${cfg.settings.launch_at_startup ? 'checked' : ''}> Launch at startup</label></div>
    <div class="form-group"><label class="form-label">Health check interval (10-3600)</label><input id="set-interval" class="form-input" type="number" min="10" max="3600" value="${cfg.settings.health_check_interval_seconds}"></div>
    <div class="form-group"><label class="form-label">Health check timeout (1-30)</label><input id="set-timeout" class="form-input" type="number" min="1" max="30" value="${cfg.settings.health_check_timeout_seconds}"></div>
  `
  body.appendChild(gs)

  const ss = document.createElement('div')
  ss.className = 'settings-section'
  ss.innerHTML = '<div class="settings-section-title">Servers</div>'
  cfg.servers.forEach((s) => {
    const row = document.createElement('div')
    row.className = 'settings-row'
    row.innerHTML = `<span>${s.name}</span><div class="settings-row-actions"><button class="btn btn-danger" data-rm-server="${s.name}">Remove</button></div>`
    ss.appendChild(row)
  })
  const addServer = document.createElement('div')
  addServer.className = 'form-group'
  addServer.innerHTML = '<label class="form-label">Add server</label><input id="set-new-server" class="form-input" placeholder="NEW-SERVER">'
  ss.appendChild(addServer)
  body.appendChild(ss)

  const aps = document.createElement('div')
  aps.className = 'settings-section'
  aps.innerHTML = '<div class="settings-section-title">Applications</div>'
  cfg.servers.forEach((s) => {
    const h = document.createElement('div')
    h.className = 'help-heading'
    h.textContent = s.name
    aps.appendChild(h)
    s.applications.forEach((a) => {
      const row = document.createElement('div')
      row.className = 'settings-row'
      row.innerHTML = `
        <span>${a.name} ${a.ip}:${a.port} ${a.protocol} path=${a.path || ''}</span>
        <div class="settings-row-actions">
          <button class="btn btn-secondary" data-toggle-server="${s.name}" data-toggle-app="${a.name}" data-toggle-enabled="${a.enabled}">${a.enabled ? 'Disable' : 'Enable'}</button>
          <button class="btn btn-secondary" data-edit-server="${s.name}" data-edit-app="${a.name}">Edit</button>
          <button class="btn btn-danger" data-rm-app-server="${s.name}" data-rm-app-name="${a.name}">Remove</button>
        </div>
      `
      aps.appendChild(row)
    })
  })
  body.appendChild(aps)

  body.querySelectorAll('[data-rm-server]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      if (!confirm(`Remove server ${btn.dataset.rmServer}?`)) return
      await request('/server/remove', 'POST', { name: btn.dataset.rmServer })
      await openSettingsModal()
      await fetchStatus()
    })
  })
  body.querySelectorAll('[data-rm-app-name]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      await removeApp(btn.dataset.rmAppServer, btn.dataset.rmAppName)
      await openSettingsModal()
    })
  })
  body.querySelectorAll('[data-toggle-app]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      await toggleApp(btn.dataset.toggleServer, btn.dataset.toggleApp, btn.dataset.toggleEnabled === 'true')
      await openSettingsModal()
    })
  })
  body.querySelectorAll('[data-edit-app]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const server = state.servers.find((s) => s.name === btn.dataset.editServer)
      const app = server?.applications.find((a) => a.name === btn.dataset.editApp)
      if (server && app) {
        setModalOpen('modal-settings', false)
        openEditModal(server.name, app)
      }
    })
  })

  setModalOpen('modal-settings', true)
}

async function saveSettings() {
  const launch_at_startup = $('set-launch')?.checked ?? false
  const health_check_interval_seconds = Number($('set-interval')?.value || 60)
  const health_check_timeout_seconds = Number($('set-timeout')?.value || 5)

  await request('/settings/update', 'POST', {
    launch_at_startup,
    health_check_interval_seconds,
    health_check_timeout_seconds,
  })

  const newServerName = ($('set-new-server')?.value || '').trim()
  if (newServerName) {
    await request('/server/add', 'POST', { name: newServerName })
  }

  setModalOpen('modal-settings', false)
  showToast('Settings saved')
  await fetchStatus()
}

function renderHelpModal() {
  const help = $('help-body')
  help.innerHTML = `
    <div class="help-section"><div class="help-heading">Getting Started</div><div class="help-body">Shipyard runs in the Windows tray and this PWA dashboard at http://127.0.0.1:9999.</div></div>
    <div class="help-section"><div class="help-heading">Tray Menu</div><div class="help-body">Applications are grouped by server. Status dots: ● reachable, ◑ degraded, ○ unreachable, · unknown.</div></div>
    <div class="help-section"><div class="help-heading">Header Icons</div><div class="help-body">Refresh runs health checks. Add opens app form. Settings opens management. Help opens docs.</div></div>
    <div class="help-section"><div class="help-heading">Managing Applications</div><div class="help-body">Use Add/Edit/Remove and enabled toggle. TCP/UDP entries are non-clickable inventory items.</div></div>
    <div class="help-section"><div class="help-heading">FAQ</div><div class="help-body">If an app is red, verify IP/port/path. For self-signed certs, use https and accept browser warning once.</div></div>
  `
  setModalOpen('modal-help', true)
}

function closeAllModals() {
  setModalOpen('modal-app', false)
  setModalOpen('modal-settings', false)
  setModalOpen('modal-help', false)
}

function navigateToSection(section) {
  if (section === 'settings') {
    openSettingsModal().catch((e) => showToast(e.message, 4000))
    return
  }
  if (section === 'add') {
    openAddModal()
    return
  }
  if (section === 'help') {
    renderHelpModal()
  }
}

function wireEvents() {
  $('btn-refresh').addEventListener('click', () => triggerRefresh().catch((e) => showToast(e.message, 4000)))
  $('btn-add').addEventListener('click', () => openAddModal())
  $('btn-settings').addEventListener('click', () => openSettingsModal().catch((e) => showToast(e.message, 4000)))
  $('btn-help').addEventListener('click', () => renderHelpModal())

  $('search').addEventListener('input', (e) => {
    state.searchQuery = e.target.value || ''
    renderDashboard()
  })

  $('modal-app-save').addEventListener('click', () => saveApp().catch((e) => showToast(e.message, 4000)))
  $('modal-app-cancel').addEventListener('click', () => setModalOpen('modal-app', false))
  $('modal-app-close').addEventListener('click', () => setModalOpen('modal-app', false))

  $('modal-settings-save').addEventListener('click', () => saveSettings().catch((e) => showToast(e.message, 4000)))
  $('modal-settings-cancel').addEventListener('click', () => setModalOpen('modal-settings', false))
  $('modal-settings-close').addEventListener('click', () => setModalOpen('modal-settings', false))

  $('modal-help-close').addEventListener('click', () => setModalOpen('modal-help', false))

  document.querySelectorAll('.modal-overlay').forEach((overlay) => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) overlay.classList.remove('open')
    })
  })

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeAllModals()
  })

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      clearPollTimer()
    } else {
      fetchStatus().catch(() => {})
    }
  })
}

function boot() {
  wireEvents()
  fetchStatus().catch((e) => showToast(e.message, 4000))
  if (location.hash === '#settings') navigateToSection('settings')
  if (location.hash === '#add') navigateToSection('add')
  if (location.hash === '#help') navigateToSection('help')
}

boot()

# SHIPYARD — Mission Control UI/UX Redesign Spec
# Model: codex-5.3 | Mode: fully autonomous, no interruptions
# Project: D:\__Projects\Shipyard
# Scope: Complete PWA dashboard redesign — index.html and app.js only
# Prerequisites: Shipyard base app and URL feature are already built and working

---

## PRIME DIRECTIVE

You are completely redesigning the Shipyard PWA dashboard at
D:\__Projects\Shipyard\pwa\index.html and D:\__Projects\Shipyard\pwa\app.js.

The goal is a world-class, mission-control-grade infrastructure dashboard
that feels like a professional operations tool — not a homelab hobby project.

Do NOT ask for clarification. Do NOT stop to confirm. Do NOT modify any
backend files (server.py, config.py, health.py, main.py). The API
contract is unchanged. Complete every phase and every task before moving
to the next phase. Fix all errors before continuing. Do not run any
tests until Phase 7.

---

## DESIGN SYSTEM

All UI must use these exact design tokens. No exceptions.

### Color Palette

```css
--bg-base:       #080c14;   /* page background */
--bg-surface:    #0d1420;   /* cards, tiles */
--bg-raised:     #0a1020;   /* sidebar, intel strip, header */
--bg-hover:      #0f1930;   /* tile hover state */
--bg-input:      #060a10;   /* inputs, search */

--border-dim:    #1a2540;   /* default borders */
--border-mid:    #2a4570;   /* hover borders */
--border-bright: #1a6bdb;   /* active/focus borders */

--text-primary:  #e2e8f0;   /* headings, tile names */
--text-secondary:#c8d8f0;   /* body text */
--text-muted:    #4a6080;   /* labels, secondary info */
--text-dim:      #2a4570;   /* very subtle text, addresses */

--accent-blue:   #7eb8f7;   /* logo, active nav, links */
--accent-bright: #1a6bdb;   /* active sidebar border */

--status-green:  #00d4a0;   /* online */
--status-amber:  #f0a500;   /* degraded */
--status-red:    #f05050;   /* offline */
--status-gray:   #1a2540;   /* unknown/disabled */

--status-green-bg: rgba(0,212,160,0.08);
--status-green-border: rgba(0,212,160,0.2);
--status-amber-bg: rgba(240,165,0,0.08);
--status-amber-border: rgba(240,165,0,0.2);
--status-red-bg: rgba(240,80,80,0.08);
--status-red-border: rgba(240,80,80,0.2);
```

### Typography

```css
--font-ui:   'Segoe UI', system-ui, -apple-system, sans-serif;
--font-mono: 'Cascadia Code', 'Courier New', monospace;
```

Load Segoe UI from system — no Google Fonts calls needed.
Use --font-mono for all IP addresses, ports, domain names, and response times.

### Sizing & Spacing

- Command bar height: 48px
- Intel strip height: auto (min 56px)
- Sidebar width: 200px
- Status bar height: 32px
- Tile border radius: 8px
- Card border radius: 8px
- Base border: 1px solid var(--border-dim)
- Tile status left border: 3px solid {status color}
- All borders are 1px (not 0.5px) — this is a dark theme application
- Tile padding: 12px
- Grid gap: 8px
- Content padding: 16px 20px

---

## PHASE 1 — HTML STRUCTURE & CSS FOUNDATION

### Task 1.1 — Capture pre-change state

Before making any changes, record MD5 hashes of the current
pwa/index.html and pwa/app.js:

```python
import hashlib
for f in ['pwa/index.html', 'pwa/app.js']:
    with open(f'D:\\__Projects\\Shipyard\\{f}', 'rb') as fh:
        h = hashlib.md5(fh.read()).hexdigest()
    print(f'{h}  {f}')
```

Save output to D:\__Projects\Shipyard\pre_redesign_hashes.txt

### Task 1.2 — Rewrite index.html shell

Completely replace D:\__Projects\Shipyard\pwa\index.html with the
following structure. Write every section completely — no placeholders.

The file must contain:

**HEAD section:**
- charset UTF-8
- viewport meta
- theme-color meta: #080c14
- title: Shipyard
- manifest link
- All CSS in a single <style> block — no external CSS files
- NO Google Fonts link — use system fonts only

**CSS — write all rules completely:**

Reset:
```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
```

Root variables: all tokens defined above under :root

Base:
```css
html, body {
  height: 100%;
  background: var(--bg-base);
  color: var(--text-primary);
  font-family: var(--font-ui);
  font-size: 13px;
  line-height: 1.5;
  overflow: hidden;
}
```

Shell layout:
```css
#app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}
```

Write complete CSS for every component listed below. Every class must
be fully defined — no stubs, no TODOs:

**Command bar** (.cmdbar):
- height: 48px
- background: var(--bg-raised)
- border-bottom: 1px solid var(--border-dim)
- padding: 0 20px
- display flex, align-items center, justify-content space-between
- z-index: 100

**Logo** (.logo-wrap, .logo-icon, .logo-text):
- logo-icon: 28x28px, background #1a3a6b, border-radius 6px, flex center
- logo-text: 14px, font-weight 700, color var(--accent-blue),
  letter-spacing 0.08em, text-transform uppercase

**Nav pill** (.nav-pill, .nav-item, .nav-item.active):
- Container: flex row, background var(--bg-input), border var(--border-dim),
  border-radius 6px, overflow hidden
- Items: padding 5px 14px, font-size 11px, font-weight 500,
  color var(--text-muted), cursor pointer, letter-spacing 0.05em,
  transition all 0.15s
- Active: background #1a3a6b, color var(--accent-blue)

**Search command** (.search-cmd):
- Inline flex, align center, gap 6px
- background var(--bg-input), border var(--border-dim), border-radius 6px
- padding 5px 10px, cursor pointer
- Span text: 11px, color var(--text-muted)
- kbd: 10px, background var(--bg-raised), border var(--border-dim),
  border-radius 3px, padding 1px 5px, color var(--text-dim)

**Command icon buttons** (.cmd-btn):
- 30x30px, transparent bg, border var(--border-dim), border-radius 6px
- flex center, cursor pointer, color var(--text-muted)
- Hover: border-color var(--border-mid), color var(--accent-blue),
  background var(--bg-raised)
- SVG inside: 14x14px

**Intel strip** (#intel-strip):
- background var(--bg-raised)
- border-bottom: 1px solid var(--border-dim)
- padding: 10px 20px
- display flex, align-items stretch, gap 0
- flex-shrink 0

**Intel blocks** (.intel-block):
- flex column, justify-content center
- padding: 0 20px
- border-right: 1px solid var(--border-dim)
- First child: padding-left 0
- Last child: border-right none
- Label: 9px, font-weight 600, color var(--text-dim), uppercase,
  letter-spacing 0.1em, margin-bottom 4px
- Value: 22px, font-weight 700, line-height 1
- Sub: 10px, color var(--text-muted), margin-top 3px
- v-online: color var(--status-green)
- v-degraded: color var(--status-amber)
- v-offline: color var(--status-red)
- v-total: color var(--accent-blue)

**Pulse indicator** (.pulse-wrap):
- flex row, align center, gap 10px, padding 0 20px
- border-right: 1px solid var(--border-dim)
- .pulse-ring: 36x36, border-radius 50%, border 2px solid var(--status-green),
  flex center
- .pulse-inner: 10x10, border-radius 50%, background var(--status-green)
- .pulse-text: font-size 10px, color var(--text-muted), line-height 1.6
- .pulse-text strong: display block, color var(--status-green), font-size 11px

**24h uptime strip** (.uptime-wrap):
- flex column, justify center, padding 0 20px
- border-right: 1px solid var(--border-dim)
- min-width 200px
- .uptime-bars: flex row, gap 2px, margin-top 5px
- .ub: width 7px, height 22px, border-radius 2px
- .ub-g: background var(--status-green)
- .ub-a: background var(--status-amber)
- .ub-r: background var(--status-red)
- .ub-e: background var(--border-dim)

**Server health bars** (.servers-intel):
- flex row, align center, gap 20px, padding 0 20px, flex 1
- .srv-row: flex column, gap 3px, min-width 100px
- .srv-name: 9px, font-weight 600, color var(--text-dim), uppercase,
  letter-spacing 0.08em
- .srv-bar-track: flex row, gap 2px, align center
- .srv-seg: height 6px, border-radius 1px
- .srv-seg-g: background var(--status-green)
- .srv-seg-a: background var(--status-amber)
- .srv-seg-r: background var(--status-red)
- .srv-seg-e: background var(--border-dim)
- .srv-count: 9px, color var(--text-muted), margin-left 5px

**Main layout** (#main-wrap):
- display flex, flex 1, overflow hidden

**Sidebar** (#sidebar):
- width 200px, background var(--bg-raised)
- border-right: 1px solid var(--border-dim)
- padding 12px 0, flex-shrink 0
- overflow-y auto

**Sidebar sections** (.sb-section):
- margin-bottom 4px
- .sb-section-label: 9px, font-weight 600, color var(--text-dim),
  uppercase, letter-spacing 0.1em, padding 8px 16px 4px
- .sb-item: flex row, align center, gap 8px, padding 7px 16px,
  cursor pointer, border-left 2px solid transparent, transition all 0.15s
- .sb-item:hover: background var(--bg-hover), color var(--accent-blue)
- .sb-item.active: background rgba(26,107,219,0.08),
  border-left-color var(--accent-bright)
- .sb-dot: 6x6, border-radius 50%, background var(--border-dim), flex-shrink 0
- .sb-name: 12px, color var(--text-muted), flex 1
- .sb-item.active .sb-name: color var(--accent-blue)
- .sb-count: 10px, color var(--text-dim), background var(--bg-input),
  padding 1px 6px, border-radius 10px, border var(--border-dim)
- .sb-divider: height 1px, background var(--border-dim), margin 8px 16px

**Content area** (#content):
- flex 1, padding 16px 20px, overflow-y auto, background var(--bg-base)

**View controls** (.view-controls):
- flex row, align center, justify-content space-between, margin-bottom 14px
- .vc-label: 11px, font-weight 600, color var(--text-muted), uppercase,
  letter-spacing 0.08em
- .vc-badge: 10px, color var(--accent-blue), background rgba(26,107,219,0.1),
  border 1px solid #1a3a6b, padding 1px 7px, border-radius 10px
- .view-toggle: flex, background var(--bg-raised), border var(--border-dim),
  border-radius 6px, overflow hidden
- .vt-btn: padding 4px 10px, font-size 10px, color var(--text-muted),
  cursor pointer, transition all 0.15s
- .vt-btn.active: background #1a3a6b, color var(--accent-blue)
- .action-btn: 10px, color var(--text-muted), background var(--bg-raised),
  border var(--border-dim), border-radius 6px, padding 4px 10px, cursor pointer

**Server section** (.server-section):
- margin-bottom 20px

**Server header** (.server-header):
- flex row, align center, gap 10px, margin-bottom 10px
- padding 8px 12px, background var(--bg-raised), border-radius 8px
- border: 1px solid var(--border-dim), cursor pointer, transition all 0.15s
- Hover: border-color var(--border-mid)
- .sh-indicator: 8x8, border-radius 50%
- .sh-name: 11px, font-weight 700, color var(--accent-blue), uppercase,
  letter-spacing 0.1em, flex 1
- .sh-meta: flex, align center, gap 6px
- .sh-pill: 9px, font-weight 600, padding 2px 7px, border-radius 10px
- .sh-pill-g: bg var(--status-green-bg), color var(--status-green),
  border var(--status-green-border)
- .sh-pill-a: bg var(--status-amber-bg), color var(--status-amber),
  border var(--status-amber-border)
- .sh-pill-r: bg var(--status-red-bg), color var(--status-red),
  border var(--status-red-border)
- .sh-type: 9px, color var(--text-dim), background var(--bg-input),
  padding 2px 7px, border-radius 10px, border var(--border-dim)
- .sh-chevron: 10px, color var(--text-muted), transition transform 0.2s
- .server-section.collapsed .sh-chevron: transform rotate(-90deg)

**Tile grid** (.tile-grid):
- display grid
- grid-template-columns: repeat(auto-fill, minmax(190px, 1fr))
- gap 8px

**Tiles — grid mode** (.tile):
- background var(--bg-surface), border-radius 8px, padding 12px
- cursor pointer, transition all 0.15s, position relative, overflow hidden
- border: 1px solid var(--border-dim)
- border-left: 3px solid var(--border-dim)
- Hover: border-color var(--border-mid), background var(--bg-hover)

Status tile variants:
- .tile-online: border-left-color var(--status-green)
- .tile-degraded: border-left-color var(--status-amber)
- .tile-offline: border-left-color var(--status-red)
- .tile-unknown: border-left-color var(--status-gray)
- .tile-disabled: opacity 0.35, cursor not-allowed, pointer-events none

Tile internals:
- .tile-top: flex, align flex-start, justify-content space-between,
  margin-bottom 10px
- .tile-icon-wrap: 36x36, border-radius 8px, background var(--bg-raised),
  border var(--border-dim), flex center, overflow hidden, flex-shrink 0
- .tile-icon-wrap img: 24x24, object-fit contain
- .tile-initials: 12px, font-weight 700, color var(--accent-blue)
- .tile-status-col: flex column, align flex-end, gap 4px
- .status-pill: 9px, font-weight 600, padding 2px 7px, border-radius 10px
- .sp-online: bg var(--status-green-bg), color var(--status-green),
  border var(--status-green-border)
- .sp-degraded: bg var(--status-amber-bg), color var(--status-amber),
  border var(--status-amber-border)
- .sp-offline: bg var(--status-red-bg), color var(--status-red),
  border var(--status-red-border)
- .sp-unknown: bg rgba(26,37,64,0.5), color var(--text-muted),
  border var(--border-dim)
- .resp-time: 9px, color var(--text-dim), font-family var(--font-mono)
- .tile-name: 12px, font-weight 600, color var(--text-secondary),
  margin-bottom 3px, white-space nowrap, overflow hidden, text-overflow ellipsis
- .tile-addr: 10px, color var(--text-dim), font-family var(--font-mono),
  white-space nowrap, overflow hidden, text-overflow ellipsis
- .proxy-addr: color #5DCAA5 (teal for domain-based apps)
- .tile-history: flex row, gap 2px, margin-top 8px, align-items flex-end
- .th-seg: width 7px, height 18px, border-radius 2px
- .th-g: background var(--status-green)
- .th-a: background var(--status-amber)
- .th-r: background var(--status-red)
- .th-u: background var(--border-dim)

**Tiles — compact mode** (.tile-compact):
- flex row, align center, gap 10px
- background var(--bg-surface), border var(--border-dim), border-radius 6px
- padding 8px 10px, cursor pointer
- border-left: 3px solid var(--border-dim)
- margin-bottom 4px, transition all 0.15s
- Hover: background var(--bg-hover)
- Status variants: same border-left logic as grid tiles
- .tc-icon: 24x24, border-radius 4px, background var(--bg-raised),
  flex center, flex-shrink 0
- .tc-name: 12px, color var(--text-secondary), flex 1, font-weight 500
- .tc-addr: 10px, color var(--text-dim), font-family var(--font-mono)
- .tc-status: 6x6, border-radius 50%

**Tiles — list mode** (.tile-list-row):
- flex row, align center, gap 12px
- background var(--bg-surface), border var(--border-dim), border-radius 6px
- padding 8px 12px, margin-bottom 3px, cursor pointer
- border-left: 3px solid var(--border-dim)
- Hover: background var(--bg-hover)
- .tl-icon: 20x20, border-radius 4px, background var(--bg-raised),
  flex center, flex-shrink 0
- .tl-name: 12px, color var(--text-secondary), font-weight 500, min-width 140px
- .tl-addr: 11px, color var(--text-dim), font-family var(--font-mono), flex 1
- .tl-server: 10px, color var(--text-dim), background var(--bg-input),
  padding 1px 6px, border-radius 4px, min-width 80px, text-align center
- .tl-resp: 10px, color var(--text-dim), font-family var(--font-mono),
  min-width 50px, text-align right
- .tl-status: same status-pill styling as grid tiles, min-width 70px,
  text-align center

**Modal overlay** (.modal-overlay):
- display none, position fixed, inset 0
- background rgba(4,8,16,0.88), z-index 200
- align-items center, justify-content center
- When .open: display flex

**Modal** (.modal):
- background var(--bg-raised), border: 1px solid var(--border-mid)
- border-radius 10px, width 480px, max-width 95vw
- max-height 88vh, overflow-y auto

**Modal header** (.modal-header):
- padding 16px 20px 12px, border-bottom: 1px solid var(--border-dim)
- flex row, align center, justify-content space-between
- .modal-title: 13px, font-weight 700, color var(--text-primary),
  letter-spacing 0.04em, uppercase
- .modal-close: transparent bg, no border, color var(--text-muted),
  cursor pointer, font-size 18px

**Modal body/footer** (.modal-body, .modal-footer):
- body: padding 20px
- footer: padding 12px 20px, border-top: 1px solid var(--border-dim),
  flex row, justify flex-end, gap 8px

**Form elements** (.form-group, .form-label, .form-input, .form-select):
- form-group: margin-bottom 14px
- form-label: 11px, color var(--text-muted), display block, margin-bottom 5px,
  font-weight 600, uppercase, letter-spacing 0.05em
- form-input/select: width 100%, background var(--bg-input),
  border: 1px solid var(--border-mid), border-radius 6px,
  padding 8px 10px, color var(--text-primary), font-size 13px,
  font-family var(--font-ui), outline none, transition border-color 0.15s
- Focus: border-color var(--accent-bright)

**Buttons** (.btn, .btn-primary, .btn-secondary, .btn-danger):
- Base: padding 7px 16px, border-radius 6px, font-size 12px,
  cursor pointer, transition all 0.15s, font-weight 500
- Primary: background #1a3a6b, color var(--accent-blue),
  border: 1px solid #2a5aab
  Hover: background #1e4a8b
- Secondary: transparent bg, color var(--text-muted),
  border: 1px solid var(--border-mid)
  Hover: background var(--bg-hover), color var(--text-primary)
- Danger: transparent bg, color var(--status-red),
  border: 1px solid rgba(240,80,80,0.3)
  Hover: background var(--status-red-bg)

**Toast** (#toast):
- position fixed, bottom 48px, right 20px
- background var(--bg-raised), border: 1px solid var(--border-mid)
- border-radius 8px, padding 10px 16px, font-size 11px
- color var(--text-primary), opacity 0, transition opacity 0.3s
- pointer-events none, z-index 300
- When .show: opacity 1

**Status bar** (#statusbar):
- height 32px, background var(--bg-raised)
- border-top: 1px solid var(--border-dim)
- padding 0 20px, flex row, align center, gap 16px
- font-size 10px, color var(--text-dim), flex-shrink 0
- .sb-stat: flex, align center, gap 5px
- .sb-dot: 6x6, border-radius 50%
- #status-version: margin-left auto

**Scrollbar styling:**
```css
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-dim); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--border-mid); }
```

**BODY HTML structure** — write all elements in full:

```html
<div id="app">

  <!-- Command Bar -->
  <header class="cmdbar">
    <div class="cmdbar-left">
      <div class="logo-wrap">
        <div class="logo-icon"><!-- ship SVG --></div>
        <span class="logo-text">Shipyard</span>
      </div>
      <div class="divider-v"></div>
      <div class="nav-pill">
        <div class="nav-item active" data-nav="dashboard">Dashboard</div>
        <div class="nav-item" data-nav="servers">Servers</div>
        <div class="nav-item" data-nav="alerts">Alerts</div>
        <div class="nav-item" data-nav="settings">Settings</div>
      </div>
    </div>
    <div class="cmdbar-right">
      <div class="search-cmd" id="btn-search">
        <!-- search icon SVG -->
        <span>Quick find</span>
        <kbd>Ctrl+K</kbd>
      </div>
      <button class="cmd-btn" id="btn-refresh" title="Refresh health checks"><!-- refresh SVG --></button>
      <button class="cmd-btn" id="btn-add" title="Add application"><!-- plus SVG --></button>
      <button class="cmd-btn" id="btn-settings-modal" title="Settings"><!-- gear SVG --></button>
      <button class="cmd-btn" id="btn-help" title="Help"><!-- question SVG --></button>
    </div>
  </header>

  <!-- Intel Strip -->
  <div id="intel-strip">
    <div class="intel-block">
      <div class="intel-label">Online</div>
      <div class="intel-value v-online" id="intel-online">—</div>
      <div class="intel-sub" id="intel-online-sub">of — total</div>
    </div>
    <div class="intel-block">
      <div class="intel-label">Degraded</div>
      <div class="intel-value v-degraded" id="intel-degraded">—</div>
      <div class="intel-sub">needs attention</div>
    </div>
    <div class="intel-block">
      <div class="intel-label">Offline</div>
      <div class="intel-value v-offline" id="intel-offline">—</div>
      <div class="intel-sub" id="intel-offline-sub">—</div>
    </div>
    <div class="intel-block">
      <div class="intel-label">Servers</div>
      <div class="intel-value v-total" id="intel-servers">—</div>
      <div class="intel-sub">active groups</div>
    </div>
    <div class="pulse-wrap">
      <div class="pulse-ring" id="pulse-ring">
        <div class="pulse-inner" id="pulse-inner"></div>
      </div>
      <div class="pulse-text">
        <strong id="pulse-status">Checking...</strong>
        <span id="pulse-time">—</span>
      </div>
    </div>
    <div class="uptime-wrap">
      <div class="intel-label">24h history</div>
      <div class="uptime-bars" id="uptime-bars">
        <!-- populated by JS -->
      </div>
    </div>
    <div class="servers-intel" id="servers-intel">
      <!-- populated by JS -->
    </div>
  </div>

  <!-- Main -->
  <div id="main-wrap">

    <!-- Sidebar -->
    <nav id="sidebar">
      <div class="sb-section">
        <div class="sb-section-label">Servers</div>
        <div id="sb-servers"><!-- populated by JS --></div>
      </div>
      <div class="sb-divider"></div>
      <div class="sb-section">
        <div class="sb-section-label">Filter by status</div>
        <div class="sb-item" data-filter="all">
          <div class="sb-dot" style="background:var(--accent-blue);"></div>
          <span class="sb-name">All applications</span>
          <span class="sb-count" id="filter-count-all">—</span>
        </div>
        <div class="sb-item" data-filter="online">
          <div class="sb-dot" style="background:var(--status-green);"></div>
          <span class="sb-name">Online</span>
          <span class="sb-count" id="filter-count-online">—</span>
        </div>
        <div class="sb-item" data-filter="degraded">
          <div class="sb-dot" style="background:var(--status-amber);"></div>
          <span class="sb-name">Degraded</span>
          <span class="sb-count" id="filter-count-degraded">—</span>
        </div>
        <div class="sb-item" data-filter="offline">
          <div class="sb-dot" style="background:var(--status-red);"></div>
          <span class="sb-name">Offline</span>
          <span class="sb-count" id="filter-count-offline">—</span>
        </div>
        <div class="sb-item" data-filter="disabled">
          <div class="sb-dot"></div>
          <span class="sb-name">Disabled</span>
          <span class="sb-count" id="filter-count-disabled">—</span>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <div id="content">
      <div class="view-controls">
        <div class="vc-left">
          <span class="vc-label" id="vc-label">All servers</span>
          <span class="vc-badge" id="vc-badge">— applications</span>
        </div>
        <div class="vc-right">
          <div class="view-toggle">
            <div class="vt-btn active" data-view="grid">Grid</div>
            <div class="vt-btn" data-view="compact">Compact</div>
            <div class="vt-btn" data-view="list">List</div>
          </div>
          <button class="action-btn" id="btn-collapse-all">Collapse all</button>
        </div>
      </div>
      <div id="server-list">
        <!-- populated by JS -->
      </div>
    </div>

  </div>

  <!-- Status Bar -->
  <footer id="statusbar">
    <div class="sb-stat">
      <div class="sb-dot" style="background:var(--status-green);"></div>
      <span id="sb-online">0</span> online
    </div>
    <div class="sb-stat">
      <div class="sb-dot" style="background:var(--status-amber);"></div>
      <span id="sb-degraded">0</span> degraded
    </div>
    <div class="sb-stat">
      <div class="sb-dot" style="background:var(--status-red);"></div>
      <span id="sb-offline">0</span> offline
    </div>
    <span style="color:var(--border-dim);">|</span>
    <span id="sb-servers-count">— servers</span>
    <span style="color:var(--border-dim);">|</span>
    <span id="sb-next-check">Next check in —</span>
    <span id="status-version" style="margin-left:auto;">Shipyard v1.0.0</span>
  </footer>

</div>

<!-- Add/Edit Application Modal -->
<div class="modal-overlay" id="modal-app">
  <div class="modal">
    <div class="modal-header">
      <span class="modal-title" id="modal-app-title">Add Application</span>
      <button class="modal-close" id="modal-app-close">&times;</button>
    </div>
    <div class="modal-body">
      <input type="hidden" id="app-original-name">
      <input type="hidden" id="app-original-server">
      <div class="form-group">
        <label class="form-label">Application name</label>
        <input type="text" class="form-input" id="app-name" placeholder="My Application">
      </div>
      <div class="form-group">
        <label class="form-label">Server</label>
        <select class="form-select" id="app-server"></select>
      </div>
      <div class="form-group">
        <label class="form-label">Direct URL <span style="color:var(--text-dim);font-weight:400;text-transform:none;">(optional — overrides IP + port)</span></label>
        <input type="text" class="form-input" id="app-url" placeholder="https://myapp.mydomain.com">
        <div style="font-size:10px;color:var(--text-dim);margin-top:4px;">Use for apps behind a reverse proxy. Leave blank to use IP and port.</div>
      </div>
      <div class="form-group">
        <label class="form-label">IP address <span style="color:var(--text-dim);font-weight:400;text-transform:none;">(required if no URL)</span></label>
        <input type="text" class="form-input" id="app-ip" placeholder="10.20.1.100">
      </div>
      <div class="form-group">
        <label class="form-label">Port <span style="color:var(--text-dim);font-weight:400;text-transform:none;">(required if no URL)</span></label>
        <input type="number" class="form-input" id="app-port" placeholder="8080" min="1" max="65535">
      </div>
      <div class="form-group">
        <label class="form-label">Protocol</label>
        <div style="display:flex;gap:16px;margin-top:4px;">
          <label style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-secondary);cursor:pointer;">
            <input type="radio" name="app-protocol" value="http" checked> http
          </label>
          <label style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-secondary);cursor:pointer;">
            <input type="radio" name="app-protocol" value="https"> https
          </label>
          <label style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-secondary);cursor:pointer;">
            <input type="radio" name="app-protocol" value="tcp"> tcp
          </label>
          <label style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-secondary);cursor:pointer;">
            <input type="radio" name="app-protocol" value="udp"> udp
          </label>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Path suffix <span style="color:var(--text-dim);font-weight:400;text-transform:none;">(optional, e.g. /admin)</span></label>
        <input type="text" class="form-input" id="app-path" placeholder="/admin">
      </div>
      <div class="form-group">
        <label style="display:flex;align-items:center;gap:8px;font-size:12px;color:var(--text-secondary);cursor:pointer;">
          <input type="checkbox" id="app-enabled" checked>
          Enabled
        </label>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" id="modal-app-cancel">Cancel</button>
      <button class="btn btn-primary" id="modal-app-save">Save application</button>
    </div>
  </div>
</div>

<!-- Settings Modal -->
<div class="modal-overlay" id="modal-settings">
  <div class="modal" style="width:600px;">
    <div class="modal-header">
      <span class="modal-title">Settings</span>
      <button class="modal-close" id="modal-settings-close">&times;</button>
    </div>
    <div class="modal-body" id="settings-body"></div>
    <div class="modal-footer">
      <button class="btn btn-secondary" id="modal-settings-cancel">Cancel</button>
      <button class="btn btn-primary" id="modal-settings-save">Save settings</button>
    </div>
  </div>
</div>

<!-- Help Modal -->
<div class="modal-overlay" id="modal-help">
  <div class="modal" style="width:640px;">
    <div class="modal-header">
      <span class="modal-title">Help &amp; Documentation</span>
      <button class="modal-close" id="modal-help-close">&times;</button>
    </div>
    <div class="modal-body" id="help-body"></div>
  </div>
</div>

<!-- Search Modal -->
<div class="modal-overlay" id="modal-search">
  <div class="modal" style="width:520px;">
    <div class="modal-body" style="padding:12px;">
      <input type="text" class="form-input" id="search-input"
             placeholder="Search applications, servers..." style="font-size:14px;padding:10px 12px;">
      <div id="search-results" style="margin-top:8px;max-height:300px;overflow-y:auto;"></div>
    </div>
  </div>
</div>

<!-- Toast -->
<div id="toast"></div>

<script src="/app.js"></script>
<script>if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js');</script>
```

For the ship SVG logo icon use this path:
```svg
<svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M2 11.5h12M4 11.5V7.5M8 11.5V6M12 11.5V8.5M3 11.5l2-6h6l2 6"
    stroke="#7eb8f7" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

For all other icon buttons use inline SVG paths:
- Refresh: rotating arrow (standard refresh icon)
- Plus: crosshair plus
- Gear: circle with radial spokes (settings)
- Question mark: circle with ? (help)
- Search: circle with magnifying handle

---

## PHASE 2 — JAVASCRIPT CORE (app.js)

### Task 2.1 — Constants and state

Replace D:\__Projects\Shipyard\pwa\app.js completely.

```javascript
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
  history: [],          // array of last 24 summary snapshots
  lastCheck: null,
  searchQuery: '',
  currentView: 'grid',  // 'grid' | 'compact' | 'list'
  activeFilter: 'all',  // 'all' | 'online' | 'degraded' | 'offline' | 'disabled'
  activeServer: null,   // null = all servers, or server name string
  collapsedServers: new Set(),
  pollTimer: null,
  countdownTimer: null,
  countdown: 30,
};
```

### Task 2.2 — API functions

Implement:

```javascript
async function fetchStatus() { ... }
async function triggerRefresh() { ... }
async function apiPost(endpoint, body) { ... }
async function fetchConfig() { ... }
```

fetchStatus():
- GET /api/status
- Update state.servers, state.summary, state.lastCheck
- Push a summary snapshot to state.history (keep last 24)
- Call renderAll()
- Reset countdown to 30, restart countdownTimer
- Schedule next poll via setTimeout(fetchStatus, POLL_INTERVAL)
- On fetch error: update pulse indicator to show "Connection lost"
  and set pulse ring border to var(--status-red)

triggerRefresh():
- POST /api/refresh
- Show toast "Health check started..."
- After 3000ms call fetchStatus()

apiPost(endpoint, body):
- POST to API + endpoint with JSON body
- Returns parsed JSON response
- On error: returns {status: 'error', message: error.message}

### Task 2.3 — Render functions

Implement all render functions completely:

**renderAll()**
Calls in order:
1. renderIntelStrip()
2. renderSidebarServers()
3. renderSidebarCounts()
4. renderServerList()
5. renderStatusBar()

**renderIntelStrip()**
Updates:
- #intel-online: summary.green count
- #intel-online-sub: "of {total} total"
- #intel-degraded: summary.amber count
- #intel-offline: summary.red count
- #intel-offline-sub: "all clear" if 0, otherwise "action required"
- #intel-servers: number of server groups
- #pulse-status: "System healthy" if red=0, "Action required" if red>0,
  "Degraded services" if amber>0 and red=0
- #pulse-time: "Last check Xs ago" — updated every second via setInterval
- Pulse ring and inner dot color: green if healthy, amber if degraded,
  red if any offline
- #uptime-bars: render 24 bar segments from state.history
  Each bar is a div.ub with class ub-g/ub-a/ub-r/ub-e based on the
  snapshot's dominant status
  If fewer than 24 snapshots exist, pad left with ub-e (empty/unknown)
- #servers-intel: for each server, render a .srv-row with name,
  proportional bar segments, and count "X/Y"
  Bar total width = 80px, segments proportional to online/degraded/offline counts

**renderSidebarServers()**
Populate #sb-servers:
- One .sb-item per server from state.servers
- data-server attribute = server name
- Dot color = green if all online, amber if any degraded, red if any offline
- sb-name = server name
- sb-count = enabled application count
- Mark active based on state.activeServer

**renderSidebarCounts()**
Update filter count badges:
- #filter-count-all: total enabled apps
- #filter-count-online: apps with status green
- #filter-count-degraded: apps with status amber
- #filter-count-offline: apps with status red
- #filter-count-disabled: apps with enabled=false

**renderServerList()**
Clear #server-list and rebuild.

Filter logic:
- If state.activeServer is set: only show that server
- Apply state.activeFilter:
  - 'online': only show apps with status=green
  - 'degraded': only show apps with status=amber
  - 'offline': only show apps with status=red
  - 'disabled': only show apps with enabled=false
  - 'all': show all enabled apps (disabled apps always hidden unless
    filter is 'disabled')
- Apply state.searchQuery: filter apps by name or ip/url
- Update #vc-label and #vc-badge

For each server group (after filtering):
- Skip server if no apps pass the filter
- Create .server-section with data-server attribute
- Add .collapsed class if server is in state.collapsedServers
- Render server header with:
  - Indicator dot color based on worst status in group
  - Server name
  - Status pills: "{N} online", "{N} degraded" (only show if >0)
  - Type badge: "local · {ip range}" or "cloud · {ip}"
    Detect cloud vs local: if all apps in group use url field → "cloud"
    If any app has 10. or 172. ip → "local"
  - Chevron (▾ or ▸ based on collapsed state)
- Render tile container based on state.currentView:
  - 'grid': .tile-grid containing .tile elements
  - 'compact': div containing .tile-compact elements
  - 'list': div containing .tile-list-row elements

**buildTileGrid(apps)** — returns HTML string for grid view:
For each app:
- Determine tile status class: tile-online/tile-degraded/tile-offline/tile-unknown
- If !app.enabled or !app.clickable: add tile-disabled
- Build icon: img if in ICON_MAP, else initials div
- img onerror: replace parent innerHTML with initials fallback
- status-pill text: "Online" / "Degraded" / "Offline" / "Unknown"
- resp-time: show response time in ms if available, else "—"
  Format: <100ms = show in green color, 100-500ms = amber, >500ms = red
- tile-addr: if app.raw_url non-empty → show hostname with class proxy-addr,
  else show ip:port
- tile-history: render 8 segments from app's history if available,
  else 8 th-u segments

**buildTileCompact(apps)** — returns HTML string for compact view:
Each .tile-compact row: icon (16x16), name, address, status dot

**buildTileList(apps, serverName)** — returns HTML string for list view:
Each .tile-list-row: icon (20x20), name (min 140px), address, server badge,
response time, status pill

**renderStatusBar()**
Update:
- #sb-online, #sb-degraded, #sb-offline counts
- #sb-servers-count: "N servers · M applications"
- #sb-next-check: updated by countdown timer

### Task 2.4 — Countdown timer

```javascript
function startCountdown() {
  if (state.countdownTimer) clearInterval(state.countdownTimer);
  state.countdown = 30;
  state.countdownTimer = setInterval(() => {
    state.countdown = Math.max(0, state.countdown - 1);
    const el = document.getElementById('sb-next-check');
    if (el) {
      el.textContent = state.countdown > 0
        ? `Next check in ${state.countdown}s`
        : 'Checking...';
    }
  }, 1000);
}
```

Also update #pulse-time every second with "Last check Xs ago" where X
increments from the lastCheck timestamp.

---

## PHASE 3 — INTERACTIVITY

### Task 3.1 — Navigation and filtering

**Sidebar server clicks:**
- Click .sb-item[data-server] → set state.activeServer to that server name
- Click "All servers" item → set state.activeServer = null
- Mark clicked item as .active, remove from others
- Call renderServerList()

**Sidebar filter clicks:**
- Click .sb-item[data-filter] → set state.activeFilter to filter value
- Mark clicked item as .active
- Update #vc-label to reflect current filter
- Call renderServerList()

**View toggle:**
- Click .vt-btn[data-view] → set state.currentView
- Update active class
- Call renderServerList()

**Collapse all button:**
- If any servers are expanded → collapse all (add all server names to state.collapsedServers)
- If all collapsed → expand all (clear state.collapsedServers)
- Update button text accordingly
- Call renderServerList()

**Server header click:**
- Toggle server name in state.collapsedServers
- Re-render that server section only (do not re-render full list)

**Nav pill clicks:**
- Dashboard: show main content, hide other views (currently only Dashboard is implemented)
- Settings: open settings modal
- Alerts: show toast "Alerts coming in a future version"
- Servers: same as clicking "All servers" in sidebar

### Task 3.2 — Search (Ctrl+K)

Search modal (#modal-search):
- Opens on: Ctrl+K keyboard shortcut, click on #btn-search
- Auto-focuses #search-input on open
- Closes on: ESC, click outside modal, click a result

#search-input oninput handler:
- Filter state.servers apps by name or ip or url
- Render results in #search-results as .search-result-item divs
- Each result: icon (16x16), app name, server name, address
- Click result: close modal, open app URL
- Up/Down arrows navigate results
- Enter opens first/highlighted result

Also update state.searchQuery for inline filtering in renderServerList()

### Task 3.3 — Tile interactions

Tile click handler (delegated on #server-list):
- If tile has data-url and is not disabled: window.open(url, '_blank', 'noopener')

Tile hover:
- CSS handles the border and background change
- No JS needed for hover

Edit button on tile (pencil icon — add this to tile-top):
- Show only on hover (CSS opacity 0 → 1 on .tile:hover .tile-edit-btn)
- Click: call openEditModal(serverName, app)
- .tile-edit-btn: 20x20, position absolute, top 8px right 8px,
  background rgba(10,16,32,0.8), border var(--border-mid), border-radius 4px,
  flex center, cursor pointer, opacity 0, transition opacity 0.15s
- .tile:hover .tile-edit-btn: opacity 1
- SVG pencil icon: 11x11

### Task 3.4 — Modal management

Implement:

```javascript
function openModal(id) {
  document.getElementById(id).classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal(id) {
  document.getElementById(id).classList.remove('open');
  document.body.style.overflow = '';
}

function closeAllModals() {
  document.querySelectorAll('.modal-overlay.open')
    .forEach(m => m.classList.remove('open'));
  document.body.style.overflow = '';
}
```

Wire all close buttons, cancel buttons, and overlay background clicks.
ESC key calls closeAllModals().
Clicking .modal-overlay (not .modal itself) calls closeAllModals().
Hash routing: on page load check window.location.hash:
- #settings → openSettingsModal()
- #add → openAddModal()
- #help → openHelpModal()
After opening, clear the hash.

### Task 3.5 — Add/Edit application modal

**openAddModal(serverName=null)**:
- Clear all form fields
- Set app-original-name and app-original-server to ""
- Populate #app-server dropdown from state.servers
- Pre-select serverName if provided
- Set modal title to "Add Application"
- openModal('modal-app')

**openEditModal(serverName, app)**:
- Prefill all form fields from app object
- Set hidden fields
- Set modal title to "Edit Application"
- openModal('modal-app')

**#modal-app-save click**:
- Validate:
  - name required
  - if url empty: ip required (valid format), port required (1-65535)
  - if url non-empty: must start http:// or https://
- If original-name set → POST /api/application/edit
- Else → POST /api/application/add
- On success: closeModal('modal-app'), showToast('Application saved'), fetchStatus()
- On error: show inline error below relevant field

### Task 3.6 — Settings modal

**openSettingsModal()**:
- fetchConfig() to get current config
- Render #settings-body with three sections:

Section 1 — Global settings:
```html
<div class="settings-section">
  <div class="settings-title">Global settings</div>
  <div class="settings-row">
    <span>Launch at Windows startup</span>
    <input type="checkbox" id="set-startup">
  </div>
  <div class="settings-row">
    <span>Health check interval (seconds)</span>
    <input type="number" class="form-input" id="set-interval"
           min="10" max="3600" style="width:80px;">
  </div>
  <div class="settings-row">
    <span>Health check timeout (seconds)</span>
    <input type="number" class="form-input" id="set-timeout"
           min="1" max="30" style="width:80px;">
  </div>
</div>
```

Section 2 — Servers:
- List each server with a Remove button
- "Add server" text input + Save button

Section 3 — Applications:
- Grouped list under each server
- Each row: icon, name, ip/url, protocol, toggle switch, edit button, remove button
- Toggle switch: custom CSS toggle, calls /api/application/toggle on change
- Remove: confirm dialog before POST /api/application/remove

#modal-settings-save:
- POST /api/settings/update with global settings values
- Handle server adds/removes
- closeModal, showToast('Settings saved'), fetchStatus()

### Task 3.7 — Help modal

**openHelpModal()**:
Render #help-body with formatted help content covering:
- Getting started
- The command bar and intel strip
- Using the sidebar
- Grid, compact, and list views
- Health monitoring
- Adding applications
- URL-based (reverse proxy) applications
- Settings
- Keyboard shortcuts:
  - Ctrl+K: quick search
  - R: refresh health checks
  - G/C/L: switch to grid/compact/list view
  - ESC: close modals

### Task 3.8 — Keyboard shortcuts

```javascript
document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    openSearchModal();
    return;
  }

  if (document.querySelector('.modal-overlay.open')) {
    if (e.key === 'Escape') closeAllModals();
    return;
  }

  switch(e.key.toLowerCase()) {
    case 'r': triggerRefresh(); break;
    case 'g': setView('grid'); break;
    case 'c': setView('compact'); break;
    case 'l': setView('list'); break;
  }
});
```

### Task 3.9 — Toast notifications

```javascript
function showToast(message, duration=3000) {
  const el = document.getElementById('toast');
  el.textContent = message;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), duration);
}
```

### Task 3.10 — Page visibility polling

```javascript
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    clearTimeout(state.pollTimer);
    clearInterval(state.countdownTimer);
  } else {
    fetchStatus();
  }
});
```

---

## PHASE 4 — INTEL STRIP DETAIL

### Task 4.1 — History tracking

The 24h uptime history is stored in state.history as an array of up to 24
summary objects, each containing: { green, amber, red, timestamp }.

Every time fetchStatus() completes, push the current summary to state.history.
If length > 24, shift the oldest off.

Persist state.history to localStorage under key 'shipyard_history' so it
survives page refreshes. On init, attempt to load from localStorage.

### Task 4.2 — Uptime bar rendering

Each bar in #uptime-bars represents one check interval.
Height is fixed at 22px, width 7px, border-radius 2px, gap 2px.

Color logic per snapshot:
- If red > 0: ub-r
- Else if amber > 0: ub-a
- Else if green > 0: ub-g
- Else: ub-e (no data / empty)

Tooltip on each bar: title attribute showing timestamp and counts.
Format: "Apr 9 14:32 — 19 online, 1 degraded, 0 offline"

### Task 4.3 — Per-server health bars

For each server in state.servers, render a .srv-row in #servers-intel.
Calculate enabled app counts by status.
Render proportional bar using flex with segments:
- Total bar container width: 80px
- Each segment width = (count / total_enabled) * 80px, minimum 3px if count > 0
- Order: green segment, amber segment, red segment
- Count label: "{online}/{total_enabled}"

---

## PHASE 5 — RESPONSE TIME DISPLAY

### Task 5.1 — Response time from API

The /api/status endpoint must return response_time_ms per application.
Add this to server.py:

In run_health_checks() in health.py, record the response time:
```python
import time
start = time.monotonic()
response = session.get(url, timeout=timeout, verify=False)
elapsed_ms = round((time.monotonic() - start) * 1000)
# Store in cache alongside status
cache[key] = {'status': classify(response), 'response_time_ms': elapsed_ms}
```

Update get_status() to return both status and response_time_ms.
Update /api/status in server.py to include response_time_ms in each app object.
Default to null if not yet checked.

### Task 5.2 — Response time color coding in tiles

In buildTileGrid():
```javascript
function formatResponseTime(ms) {
  if (ms === null || ms === undefined) return '—';
  if (ms < 100) return `<span style="color:var(--status-green)">${ms}ms</span>`;
  if (ms < 500) return `<span style="color:var(--status-amber)">${ms}ms</span>`;
  return `<span style="color:var(--status-red)">${ms}ms</span>`;
}
```

Display in .resp-time div in each tile.
In compact and list views, show response time in the address/info area.

---

## PHASE 6 — POLISH AND REFINEMENT

### Task 6.1 — Collapse state persistence

Persist state.collapsedServers to localStorage as an array under
'shipyard_collapsed'. Load on init. This means users' preferred
collapsed/expanded layout persists across page refreshes.

### Task 6.2 — View mode persistence

Persist state.currentView to localStorage as 'shipyard_view'.
Load on init.

### Task 6.3 — Last check time display

Update #pulse-time every second via setInterval:
```javascript
function updateLastCheckDisplay() {
  if (!state.lastCheck) return;
  const seconds = Math.round((Date.now() - state.lastCheck) / 1000);
  const el = document.getElementById('pulse-time');
  if (!el) return;
  if (seconds < 5) el.textContent = 'Just checked';
  else if (seconds < 60) el.textContent = `Last check ${seconds}s ago`;
  else el.textContent = `Last check ${Math.floor(seconds/60)}m ago`;
}
setInterval(updateLastCheckDisplay, 1000);
```

### Task 6.4 — Pulse ring animation

Add CSS keyframe animation for the pulse ring when system is healthy:
```css
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0,212,160,0.3); }
  50% { box-shadow: 0 0 0 6px rgba(0,212,160,0); }
}
.pulse-ring.healthy {
  animation: pulse-glow 2s ease-in-out infinite;
}
```

Add/remove .healthy class based on system status.
When degraded: border color amber, no animation.
When offline: border color red, no animation.

### Task 6.5 — Empty state

When a filter returns no results, render in #server-list:
```html
<div style="text-align:center;padding:60px 20px;color:var(--text-muted);">
  <div style="font-size:32px;margin-bottom:12px;">○</div>
  <div style="font-size:14px;font-weight:500;color:var(--text-secondary);margin-bottom:6px;">
    No applications found
  </div>
  <div style="font-size:12px;">
    Try a different filter or search query
  </div>
</div>
```

### Task 6.6 — Loading state

On initial page load before first API response, show in #server-list:
```html
<div style="text-align:center;padding:60px 20px;color:var(--text-muted);">
  <div style="font-size:12px;color:var(--text-dim);">Connecting to Shipyard...</div>
</div>
```

If API is unreachable after first fetch attempt, show:
```html
<div style="text-align:center;padding:60px 20px;">
  <div style="font-size:14px;font-weight:500;color:var(--status-amber);margin-bottom:8px;">
    Cannot reach Shipyard
  </div>
  <div style="font-size:11px;color:var(--text-muted);">
    Make sure Shipyard is running at 127.0.0.1:9999
  </div>
</div>
```

### Task 6.7 — Smooth tile status transitions

Add CSS transition to tile border-left-color:
```css
.tile { transition: border-color 0.3s ease, background 0.15s ease, border-left-color 0.3s ease; }
```

When status changes from one check to the next, the tile border color
transitions smoothly rather than snapping.

### Task 6.8 — Search results styling

.search-result-item:
- flex row, align center, gap 10px, padding 8px 10px
- border-radius 6px, cursor pointer, transition background 0.1s
- Hover: background var(--bg-raised)
- .sri-icon: 20x20, border-radius 4px, background var(--bg-raised), flex center
- .sri-name: 12px, color var(--text-secondary), font-weight 500
- .sri-server: 10px, color var(--text-dim), background var(--bg-input),
  padding 1px 5px, border-radius 4px
- .sri-addr: 10px, color var(--text-dim), font-family var(--font-mono),
  margin-left auto

When no results: show "No applications match your search" in muted text.

### Task 6.9 — Rebuild the exe

After all phase 1-6 changes are complete:

1. Scan all tracked files for real IPs (10.20.) — must return PASS:
```python
import os, subprocess
result = subprocess.run(
    ['git', 'ls-files', '--others', '--cached', '--exclude-standard'],
    cwd=r'D:\__Projects\Shipyard', capture_output=True, text=True
)
found = False
for rel in result.stdout.strip().split('\n'):
    fp = os.path.join(r'D:\__Projects\Shipyard', rel)
    if not os.path.isfile(fp): continue
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        for i, line in enumerate(f, 1):
            if '10.20.' in line:
                print(f'FAIL {rel} line {i}')
                found = True
if not found:
    print('PASS: No real IPs in tracked files')
```

2. Build:
```
cd D:\__Projects\Shipyard
pyinstaller shipyard.spec --clean
```

3. Verify dist\shipyard.exe produced successfully.

---

## PHASE 7 — END TO END TESTING

Do NOT begin this phase until all phases 1-6 are complete and the exe
has been rebuilt successfully. Run all tests in order. Fix failures
and re-run the entire suite before reporting completion.

### Task 7.1 — Server availability

Start Shipyard:
```
set SHIPYARD_CONFIG=D:\__Projects\Shipyard\config\servers.yaml
python D:\__Projects\Shipyard\main.py
```

Verify:
```
curl -s http://127.0.0.1:9999/ | findstr "Shipyard"
```
Must return non-empty result.
Print "T7.1 PASS" or fix and recheck.

### Task 7.2 — API status response structure

```python
import requests, json

r = requests.get('http://127.0.0.1:9999/api/status')
data = r.json()

assert r.status_code == 200, f'FAIL: status {r.status_code}'
assert 'servers' in data, 'FAIL: no servers key'
assert 'summary' in data, 'FAIL: no summary key'
assert len(data['servers']) >= 2, f'FAIL: only {len(data["servers"])} servers'

for server in data['servers']:
    assert 'name' in server, f'FAIL: server missing name'
    for app in server['applications']:
        required = ['name','ip','port','protocol','url','raw_url',
                    'enabled','status','clickable']
        for field in required:
            assert field in app, f'FAIL: app {app.get("name")} missing {field}'
        assert 'response_time_ms' in app, f'FAIL: app missing response_time_ms'

summary_fields = ['total','enabled','green','amber','red','unknown','last_check']
for f in summary_fields:
    assert f in data['summary'], f'FAIL: summary missing {f}'

print('T7.2 PASS: API status structure correct')
```

### Task 7.3 — HTML structure verification

```python
with open(r'D:\__Projects\Shipyard\pwa\index.html', 'r') as f:
    html = f.read()

checks = [
    ('#app', '<div id="app">'),
    ('cmdbar', 'class="cmdbar"'),
    ('intel-strip', 'id="intel-strip"'),
    ('sidebar', 'id="sidebar"'),
    ('content', 'id="content"'),
    ('server-list', 'id="server-list"'),
    ('statusbar', 'id="statusbar"'),
    ('modal-app', 'id="modal-app"'),
    ('modal-settings', 'id="modal-settings"'),
    ('modal-help', 'id="modal-help"'),
    ('modal-search', 'id="modal-search"'),
    ('toast', 'id="toast"'),
    ('view-toggle', 'class="view-toggle"'),
    ('uptime-bars', 'id="uptime-bars"'),
    ('servers-intel', 'id="servers-intel"'),
    ('pulse-ring', 'id="pulse-ring"'),
    ('sb-next-check', 'id="sb-next-check"'),
    ('intel-online', 'id="intel-online"'),
    ('intel-degraded', 'id="intel-degraded"'),
    ('intel-offline', 'id="intel-offline"'),
]

all_pass = True
for name, pattern in checks:
    if pattern not in html:
        print(f'FAIL: {name} not found ({pattern})')
        all_pass = False

if all_pass:
    print('T7.3 PASS: All required HTML elements present')
```

### Task 7.4 — CSS token verification

```python
with open(r'D:\__Projects\Shipyard\pwa\index.html', 'r') as f:
    css = f.read()

tokens = [
    '--bg-base', '--bg-surface', '--bg-raised', '--bg-hover',
    '--border-dim', '--border-mid', '--border-bright',
    '--text-primary', '--text-secondary', '--text-muted', '--text-dim',
    '--accent-blue', '--status-green', '--status-amber', '--status-red',
    '--font-ui', '--font-mono',
    'tile-online', 'tile-degraded', 'tile-offline',
    'tile-grid', 'tile-compact', 'tile-list-row',
    'pulse-glow', 'pulse-ring', 'pulse-inner',
    'sp-online', 'sp-degraded', 'sp-offline',
    'uptime-bars', 'ub-g', 'ub-a', 'ub-r',
    'srv-seg-g', 'srv-seg-a',
    'search-result-item',
    'view-toggle', 'vt-btn',
    'server-header', 'sh-name', 'sh-indicator',
    'sb-section', 'sb-item', 'sb-divider',
]

all_pass = True
for token in tokens:
    if token not in css:
        print(f'FAIL: CSS token/class missing: {token}')
        all_pass = False

if all_pass:
    print('T7.4 PASS: All CSS tokens and classes present')
```

### Task 7.5 — JavaScript function verification

```python
with open(r'D:\__Projects\Shipyard\pwa\app.js', 'r') as f:
    js = f.read()

functions = [
    'fetchStatus', 'triggerRefresh', 'apiPost', 'fetchConfig',
    'renderAll', 'renderIntelStrip', 'renderSidebarServers',
    'renderSidebarCounts', 'renderServerList', 'renderStatusBar',
    'buildTileGrid', 'buildTileCompact', 'buildTileList',
    'startCountdown', 'updateLastCheckDisplay',
    'openModal', 'closeModal', 'closeAllModals',
    'openAddModal', 'openEditModal', 'openSettingsModal',
    'openHelpModal', 'openSearchModal',
    'showToast', 'formatResponseTime',
    'ICON_MAP', 'ICON_BASE', 'API', 'POLL_INTERVAL',
    'state.history', 'state.collapsedServers', 'state.currentView',
    'localStorage', 'shipyard_history', 'shipyard_collapsed',
    'shipyard_view', 'visibilitychange',
    'keydown', 'Ctrl', 'Escape',
]

all_pass = True
for fn in functions:
    if fn not in js:
        print(f'FAIL: Missing in app.js: {fn}')
        all_pass = False

if all_pass:
    print('T7.5 PASS: All required JS functions and references present')
```

### Task 7.6 — No real IPs in tracked files

```python
import os, subprocess

result = subprocess.run(
    ['git', 'ls-files', '--others', '--cached', '--exclude-standard'],
    cwd=r'D:\__Projects\Shipyard', capture_output=True, text=True
)

found = False
for rel in result.stdout.strip().split('\n'):
    fp = os.path.join(r'D:\__Projects\Shipyard', rel)
    if not os.path.isfile(fp): continue
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                if '10.20.' in line or '10.20.239.' in line:
                    print(f'FAIL {rel} line {i}: {line.rstrip()}')
                    found = True
    except: pass

if not found:
    print('T7.6 PASS: No real IPs in any tracked file')
```

### Task 7.7 — Response time in API

```python
import requests

r = requests.post('http://127.0.0.1:9999/api/refresh')
assert r.json()['status'] == 'ok', 'FAIL: refresh endpoint'

import time; time.sleep(5)

r = requests.get('http://127.0.0.1:9999/api/status')
data = r.json()

found_rt = False
for server in data['servers']:
    for app in server['applications']:
        if app['enabled'] and app['clickable'] and app['response_time_ms'] is not None:
            found_rt = True
            assert isinstance(app['response_time_ms'], int), \
                f'FAIL: response_time_ms not int for {app["name"]}'

if found_rt:
    print('T7.7 PASS: Response times present and correct type')
else:
    print('T7.7 WARN: No response times found (all services may be offline)')
```

### Task 7.8 — JS syntax check

```
node --check D:\__Projects\Shipyard\pwa\app.js
```

If Node.js unavailable, run Python bracket balance check:
```python
with open(r'D:\__Projects\Shipyard\pwa\app.js', 'r') as f:
    js = f.read()

opens = js.count('{')
closes = js.count('}')
parens_o = js.count('(')
parens_c = js.count(')')
backticks = js.count('`')

ok = True
if opens != closes:
    print(f'FAIL: Unbalanced braces: {opens} open, {closes} close')
    ok = False
if parens_o != parens_c:
    print(f'FAIL: Unbalanced parens: {parens_o} open, {parens_c} close')
    ok = False
if backticks % 2 != 0:
    print(f'FAIL: Odd number of backticks: {backticks}')
    ok = False
if ok:
    print('T7.8 PASS: JS syntax appears balanced')
```

### Task 7.9 — Functional smoke tests

Verify the following by reading source code (not browser automation):

A. Search modal:
- #modal-search exists in HTML
- openSearchModal function exists in app.js
- Ctrl+K keydown handler exists in app.js
- search-result-item class exists in app.js or index.html
Print "T7.9A PASS" or fix.

B. Collapse functionality:
- state.collapsedServers exists
- localStorage.setItem with 'shipyard_collapsed' exists in app.js
- collapsed class handling exists in renderServerList
Print "T7.9B PASS" or fix.

C. Three view modes:
- buildTileGrid function exists
- buildTileCompact function exists
- buildTileList function exists
- data-view attribute handling exists in JS
Print "T7.9C PASS" or fix.

D. Sidebar filtering:
- data-filter attribute handling exists
- state.activeFilter is used in renderServerList
- state.activeServer is used in renderServerList
Print "T7.9D PASS" or fix.

E. History persistence:
- localStorage.getItem('shipyard_history') exists in app.js
- localStorage.setItem('shipyard_history') exists in app.js
- state.history is pushed to in fetchStatus
Print "T7.9E PASS" or fix.

### Task 7.10 — Exe smoke test

Test the compiled exe with the template config:
```
mkdir C:\ShipyardUITest
copy D:\__Projects\Shipyard\dist\shipyard.exe C:\ShipyardUITest\
C:\ShipyardUITest\shipyard.exe
```

Verify:
- Welcome dialog appears (first run)
- servers.yaml created from template at C:\ShipyardUITest\config\
- Tray icon appears
- PWA opens in browser at http://127.0.0.1:9999
- Dashboard renders with navy/slate dark theme (NOT purple)
- Intel strip visible with placeholders
- Sidebar visible
- Three view mode buttons visible in view controls

Kill Shipyard and delete C:\ShipyardUITest\ after test.
Print "T7.10 PASS" or document what failed.

---

## COMPLETION GATE

Only after ALL tasks T7.1 through T7.10 produce PASS results,
write D:\__Projects\Shipyard\UI_REDESIGN_TEST_RESULTS.md:

- Date and time
- Results for T7.1 through T7.10
- Any issues encountered and how they were fixed
- Final line:
  "SHIPYARD UI REDESIGN COMPLETE — all tests passed, exe rebuilt,
  mission control dashboard ready for use"

Do not report completion to the user until this file exists and
contains the final line above.

---

## CONSTRAINTS

- Do NOT modify server.py API endpoints or contracts (except adding
  response_time_ms to health cache and status response — this is the
  only backend change permitted)
- Do NOT modify config.py, main.py, health.py (except the
  response_time_ms addition)
- Do NOT modify shipyard.spec datas entries
- Do NOT use any external JS libraries — vanilla JS only
- Do NOT use Google Fonts — system fonts only
- All color values must use CSS variables defined under :root
- No hardcoded hex colors outside of :root variable definitions
- No real IP addresses in any tracked file
- The exe must be rebuilt before testing is considered complete
- The pre_redesign_hashes.txt file must be added to .gitignore

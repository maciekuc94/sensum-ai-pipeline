/* SENSUM Mission Control — vanilla JS, hash-routing. Read-only. */
'use strict';

const $app = document.getElementById('app');
let STATE = null;     // /api/state cache (odświeżany przy każdym wejściu na board)
let BACKLOG = null;   // /api/backlog cache (per sesja strony)

const esc = (s) => String(s).replace(/[&<>"]/g,
  (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

async function getJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url} -> HTTP ${r.status}`);
  return r.json();
}

function copyCmd(btn, cmd) {
  navigator.clipboard.writeText(cmd).then(() => {
    const old = btn.textContent;
    btn.textContent = 'skopiowano ✓';
    setTimeout(() => { btn.textContent = old; }, 1200);
  });
}

/* ---------- widok: tablica pipeline ---------- */

function stepperHTML(phases) {
  const dots = phases.map((p) =>
    `<span class="dot ${p.done ? '' : 'todo'}">${p.done ? '●' : '○'}</span>`);
  const bars = phases.slice(1).map((p) =>
    `<span class="bar ${p.done ? '' : 'todo'}"></span>`);
  let row = '';
  dots.forEach((d, i) => { row += d; if (bars[i]) row += bars[i]; });
  const labels = phases.map((p) => `<span>${esc(p.label)}</span>`).join('');
  return `<div class="stepper">${row}</div><div class="phase-labels">${labels}</div>`;
}

function nextHTML(slug, next) {
  if (!next.length) return '<span class="chip">✦ ukończony</span>';
  return next.map((a) => {
    if (a.command) {
      return `<span class="chip">→ ${esc(a.label)}</span>
        <button class="copy-btn" data-cmd="${esc(a.command)}">kopiuj komendę</button>`;
    }
    return `<span class="chip manual" title="${esc(a.manual_hint || '')}">→ ${esc(a.label)} (ręczne)</span>`;
  }).join(' ');
}

function cardHTML(s) {
  return `<div class="card" data-slug="${esc(s.slug)}">
    <div class="row">
      <div><div class="title">${esc(s.title)}</div>
        <div class="slug-name">${esc(s.slug)}</div></div>
      <div>${nextHTML(s.slug, s.next)}</div>
    </div>
    ${stepperHTML(s.phases)}
  </div>`;
}

async function renderPipeline() {
  STATE = await getJSON('/api/state');
  const active = STATE.slugs.filter((s) => !s.finished);
  const done = STATE.slugs.filter((s) => s.finished);
  $app.innerHTML = `
    <h2>Pipeline (${active.length} w toku)</h2>
    ${active.map(cardHTML).join('') || '<p class="muted">Wszystko ukończone.</p>'}
    <details class="finished" ${done.length ? '' : 'hidden'}>
      <summary>Ukończone (${done.length})</summary>
      ${done.map(cardHTML).join('')}
    </details>`;
  $app.querySelectorAll('.card').forEach((el) => {
    el.addEventListener('click', (ev) => {
      if (ev.target.closest('.copy-btn')) return;
      location.hash = `#/slug/${el.dataset.slug}/skrypt`;
    });
  });
  $app.querySelectorAll('.copy-btn').forEach((b) =>
    b.addEventListener('click', () => copyCmd(b, b.dataset.cmd)));
}

/* ---------- router ---------- */

function setNav(tab) {
  document.getElementById('nav-pipeline').classList.toggle('active', tab === 'pipeline');
  document.getElementById('nav-backlog').classList.toggle('active', tab === 'backlog');
}

async function router() {
  const h = location.hash || '#/';
  try {
    if (h.startsWith('#/slug/')) {
      const [, , slug, tab] = h.split('/');
      setNav('pipeline');
      await renderSlug(decodeURIComponent(slug), tab || 'skrypt');
    } else if (h === '#/backlog') {
      setNav('backlog');
      await renderBacklog();
    } else {
      setNav('pipeline');
      await renderPipeline();
    }
  } catch (e) {
    $app.innerHTML = `<p class="muted">Błąd: ${esc(e.message)} — czy serwer działa?</p>`;
  }
}

window.addEventListener('hashchange', router);
router();

async function renderSlug(slug) { $app.innerHTML = `<p class="muted">${esc(slug)} — widok w Task 7</p>`; }
async function renderBacklog() { $app.innerHTML = '<p class="muted">Backlog — widok w Task 7</p>'; }

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
  const flash = (msg) => {
    const old = btn.textContent;
    btn.textContent = msg;
    setTimeout(() => { btn.textContent = old; }, 1400);
  };
  const fallback = () => window.prompt('Skopiuj komendę (Ctrl+C):', cmd);
  if (!navigator.clipboard) { fallback(); return; }
  navigator.clipboard.writeText(cmd)
    .then(() => flash('skopiowano ✓'))
    .catch(() => { flash('skopiuj ręcznie ↓'); fallback(); });
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

/* ---------- widok: podstrona sluga ---------- */

const TABS = [['skrypt', 'Skrypt'], ['obrazy', 'Obrazy'],
              ['miniatury', 'Miniatury'], ['pliki', 'Pliki']];
const SCRIPT_VERSIONS = [
  ['md/script_corrected.md', 'po redakcji'],
  ['md/04_final.md', '04_final'],
  ['md/04_final_machine.md', 'machine'],
];

const rawURL = (slug, path) =>
  `/api/slug/${encodeURIComponent(slug)}/raw?path=${encodeURIComponent(path)}`;

async function fetchText(slug, path) {
  const r = await fetch(rawURL(slug, path));
  if (!r.ok) throw new Error(`${path} -> HTTP ${r.status}`);
  return r.text();
}

function galleryHTML(slug, paths) {
  if (!paths.length) return '<p class="muted">Brak obrazów.</p>';
  return `<div class="gallery">${paths.map((p, i) => `
    <figure data-path="${esc(p)}" data-n="${i + 1}">
      <img loading="lazy" src="${rawURL(slug, p)}" alt="${esc(p)}"
           onerror="this.replaceWith(document.createTextNode('⚠ brak pliku'))">
      <figcaption>#${i + 1} · ${esc(p.split('/').pop())}</figcaption>
    </figure>`).join('')}</div>`;
}

async function renderSlug(slug, tab) {
  // STATE reużyte (deep-link działa bez wejścia na board); świeży stan po powrocie na board (renderPipeline zawsze refetchuje).
  if (!STATE) STATE = await getJSON('/api/state');
  const info = STATE.slugs.find((s) => s.slug === slug);
  const files = (await getJSON(`/api/slug/${encodeURIComponent(slug)}/files`)).files;
  const have = new Set(files.map((f) => f.path));

  const tabsHTML = TABS.map(([id, label]) =>
    `<a href="#/slug/${encodeURIComponent(slug)}/${id}"
        class="${id === tab ? 'active' : ''}">${label}</a>`).join('');
  let body = '';

  if (tab === 'skrypt') {
    const versions = SCRIPT_VERSIONS.filter(([p]) => have.has(p));
    if (!versions.length) {
      body = '<p class="muted">Brak skryptu (przed /draft).</p>';
    } else {
      const current = versions[0][0];
      const sw = versions.map(([p, label]) =>
        `<a href="#" data-ver="${esc(p)}" class="${p === current ? 'active' : ''}">${label}</a>`).join('');
      body = `<div class="version-switch">${sw}</div><div class="prose" id="prose"></div>`;
      queueMicrotask(async () => {
        const load = async (p) => {
          const el = document.getElementById('prose');
          if (el) el.innerHTML = marked.parse(await fetchText(slug, p));
        };
        await load(current);
        $app.querySelectorAll('.version-switch a').forEach((a) =>
          a.addEventListener('click', async (ev) => {
            ev.preventDefault();
            $app.querySelectorAll('.version-switch a').forEach((x) => x.classList.remove('active'));
            a.classList.add('active');
            await load(a.dataset.ver);
          }));
      });
    }
  } else if (tab === 'obrazy') {
    const post = files.filter((f) => f.path.startsWith('images_post/') && f.path.endsWith('.png'));
    const base = files.filter((f) => f.path.startsWith('images/') && f.path.endsWith('.png'));
    body = galleryHTML(slug, (post.length ? post : base).map((f) => f.path));
  } else if (tab === 'miniatury') {
    const groups = ['thumbnails_no_grain/', 'thumbnails_grain/', 'thumbnails/'];
    body = groups.map((g) => {
      const paths = files.filter((f) => f.path.startsWith(g) && f.path.endsWith('.png'))
        .map((f) => f.path);
      return paths.length ? `<h2>${esc(g)}</h2>${galleryHTML(slug, paths)}` : '';
    }).join('') || '<p class="muted">Brak miniatur (przed /package).</p>';
  } else {
    body = `<ul class="filelist">${files.map((f) => `
      <li><a href="#" data-path="${esc(f.path)}">${esc(f.path)}</a>
          <span class="size">${(f.size / 1024).toFixed(0)} KB</span></li>`).join('')}</ul>
      <div class="prose" id="prose" hidden></div>`;
  }

  $app.innerHTML = `
    <a class="back" href="#/">← Pipeline</a>
    <h2>${esc(info ? info.title : slug)} <span class="slug-name">${esc(slug)}</span></h2>
    <div class="tabs">${tabsHTML}</div>${body}`;

  $app.querySelectorAll('.gallery figure').forEach((fig) =>
    fig.addEventListener('click', () => showLightbox(
      rawURL(slug, fig.dataset.path), `#${fig.dataset.n} · ${fig.dataset.path}`)));

  $app.querySelectorAll('.filelist a').forEach((a) =>
    a.addEventListener('click', async (ev) => {
      ev.preventDefault();
      const p = a.dataset.path;
      const prose = document.getElementById('prose');
      if (/\.(png|jpg|jpeg|gif)$/i.test(p)) {
        showLightbox(rawURL(slug, p), p);
      } else if (/\.(md|txt|srt|json|html|fcpxml)$/i.test(p)) {
        prose.hidden = false;
        const text = await fetchText(slug, p);
        prose.innerHTML = p.endsWith('.md')
          ? marked.parse(text)
          : `<pre>${esc(text.slice(0, 20000))}</pre>`;
        prose.scrollIntoView({behavior: 'smooth'});
      } else {
        prompt('Ścieżka pliku (Ctrl+C):', `outputs/videos_pl/${slug}/${p}`);
      }
    }));
}

/* ---------- lightbox ---------- */

const $lb = document.getElementById('lightbox');
function showLightbox(src, caption) {
  document.getElementById('lightbox-img').src = src;
  document.getElementById('lightbox-cap').textContent = caption;
  $lb.hidden = false;
}
$lb.addEventListener('click', () => { $lb.hidden = true; });

/* ---------- widok: backlog ---------- */

async function renderBacklog() {
  if (!BACKLOG) BACKLOG = await getJSON('/api/backlog');
  if (!BACKLOG.available) {
    $app.innerHTML = '<p class="muted">Brak docs/research/topic_backlog_PL.md.</p>';
    return;
  }
  const startCmd = (temat) =>
    `PYTHONIOENCODING=utf-8 python tools/pipeline/agent1_research.py "${temat}"`;
  const statusChip = (s) => s
    ? `<span class="status-chip${s === 'nakręcony' ? ' done' : ''}">${esc(s)}</span>` : '';

  const top = BACKLOG.top.map((t) => `
    <div class="topic">
      <span class="tier">${esc(t.tier)}</span> · idx ${t.idx} · suma ${t.suma}
      <div class="title">${esc(t.title)}</div>
      ${t.hook ? `<details><summary class="muted">zalążek hooka</summary>
        <p>„${esc(t.hook)}"</p></details>` : ''}
      <button class="copy-btn" data-cmd="${esc(startCmd(t.title))}">kopiuj start (agent1)</button>
    </div>`).join('');

  const rows = BACKLOG.ranking.map((r) => `
    <tr><td>${esc(r.pos)}</td>
      <td>${esc(r.temat)} ${statusChip(r.status)}</td>
      <td>${esc(r.tier)}</td><td>${esc(r.architektura)}</td>
      <td>${r.status ? '' :
        `<button class="copy-btn" data-cmd="${esc(startCmd(r.temat))}">start</button>`}</td>
    </tr>`).join('');

  $app.innerHTML = `
    <h2>Backlog — rekomendowane</h2>${top}
    <h2>Pełny ranking</h2>
    <table class="ranking">
      <tr><th>#</th><th>Temat</th><th>Tier</th><th>Architektura</th><th></th></tr>
      ${rows}
    </table>`;
  $app.querySelectorAll('.copy-btn').forEach((b) =>
    b.addEventListener('click', () => copyCmd(b, b.dataset.cmd)));
}

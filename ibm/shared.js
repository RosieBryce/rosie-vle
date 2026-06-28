/* ═══════════════════════════════════════════════════════════════
   VLE Shared JS
   - initNav(base)     → inject sticky nav + wire hamburger
   - startCountdown(id) → prize deadline ticker
   - initCollapsibles() → collapse-toggle behaviour
═══════════════════════════════════════════════════════════════ */

/* ── Course + viz data ─────────────────────────────────────── */
const VLE_COURSES = [
  { id: '01', name: 'Machine Learning with Python',                              hours: 20, genai: false },
  { id: '02', name: 'Intro to Deep Learning & Neural Networks with Keras',       hours: 10, genai: false },
  { id: '03', name: 'Deep Learning with Keras and TensorFlow',                   hours: 23, genai: false },
  { id: '04', name: 'Intro to Neural Networks and PyTorch',                      hours: 18, genai: false },
  { id: '05', name: 'Deep Learning with PyTorch',                                hours: 19, genai: false },
  { id: '06', name: 'AI Capstone Project with Deep Learning',                    hours: 15, genai: false },
  { id: '07', name: 'Generative AI and LLMs: Architecture & Data Prep',          hours: 6,  genai: true  },
  { id: '08', name: 'Gen AI Foundational Models for NLP & Language',             hours: 10, genai: true  },
  { id: '09', name: 'Generative AI Language Modeling with Transformers',         hours: 9,  genai: true  },
  { id: '10', name: 'Gen AI Engineering and Fine-Tuning Transformers',           hours: 8,  genai: true  },
  { id: '11', name: 'Gen AI Advanced Fine-Tuning for LLMs',                      hours: 9,  genai: true  },
  { id: '12', name: 'Fundamentals of AI Agents Using RAG and LangChain',         hours: 9,  genai: true  },
  { id: '13', name: 'Project: GenAI Applications with RAG and LangChain',        hours: 9,  genai: true  },
];

const VLE_VIZ = [
  { slug: 'gradient-descent',     name: 'Gradient Descent',            phase: 1 },
  { slug: 'activation-functions', name: 'Activation Functions',        phase: 1 },
  { slug: 'backprop',             name: 'Backpropagation',             phase: 1 },
  { slug: 'bias-variance',        name: 'Bias–Variance Tradeoff',      phase: 1 },
  { slug: 'temperature-sampling', name: 'Temperature & Sampling',      phase: 2 },
  { slug: 'attention',            name: 'Attention Mechanism',         phase: 2 },
  { slug: 'lora-decomposition',   name: 'LoRA Decomposition',          phase: 2 },
  { slug: 'tokenisation',         name: 'Tokenisation',                phase: 2 },
];

const VLE_GAMES = [
  { course: '03', type: 'quiz',        name: 'C3 Quiz — Keras & TF',          live: true  },
  { course: '03', type: 'flashcards', name: 'C3 Flashcards — Keras & TF',     live: true  },
  { course: '03', type: 'odd-one-out', name: 'C3 Odd One Out — Keras & TF',   live: true  },
  { course: '03', type: 'true-false',  name: 'C3 True/False Sprint — Keras',  live: true  },
  { course: '04', type: 'quiz',       name: 'C4 Quiz — PyTorch Fundamentals', live: true  },
  { course: '04', type: 'flashcards', name: 'C4 Flashcards — PyTorch',         live: true  },
];

/* ── Nav injection ─────────────────────────────────────────── */
/**
 * Inject the site nav as the first element in <body>.
 * @param {string} base  Path prefix — '' for vle/ root, '../' for sub-dirs.
 */
function initNav(base) {
  // Course dropdown links
  const courseLinks = VLE_COURSES.map(c => {
    const label = `${c.id}. ${c.name}`;
    return `<a href="${base}courses/c${c.id}.html">${label}</a>`;
  }).join('');

  // Games dropdown: live games linked, others dimmed
  const liveGames = VLE_GAMES.filter(g => g.live);
  const gameLinks = liveGames.length
    ? liveGames.map(g =>
        `<a href="${base}games/c${g.course}-${g.type}.html">${g.name}</a>`
      ).join('')
    : `<a style="opacity:.45;cursor:default">Coming soon…</a>`;

  // Viz dropdown: phase-1 live, phase-2 dimmed
  const vizLinks = VLE_VIZ.map(v => {
    if (v.phase === 1) {
      return `<a href="${base}viz/${v.slug}.html">${v.name}</a>`;
    }
    return `<a href="${base}viz/${v.slug}.html" style="opacity:.45">${v.name} <span style="font-size:.68rem;color:var(--muted)">(coming)</span></a>`;
  }).join('');

  const html = `
<nav class="site-nav" id="site-nav">
  <div class="nav-inner">
    <a class="nav-brand" href="${base}index.html">⚡ VLE</a>

    <ul class="nav-links" id="nav-links">
      <li class="nav-item">
        <a class="nav-link" href="${base}courses/c03.html">
          Courses <span class="nav-chevron">▾</span>
        </a>
        <div class="nav-dropdown">${courseLinks}</div>
      </li>

      <li class="nav-item">
        <a class="nav-link" href="${base}viz/index.html">
          Visualisations <span class="nav-chevron">▾</span>
        </a>
        <div class="nav-dropdown">${vizLinks}</div>
      </li>

      <li class="nav-item">
        <a class="nav-link" href="${base}games/index.html">
          Games <span class="nav-chevron">▾</span>
        </a>
        <div class="nav-dropdown">${gameLinks}</div>
      </li>

      <li class="nav-item">
        <a class="nav-link" href="${base}library/index.html">
          Library <span class="nav-chevron">▾</span>
        </a>
        <div class="nav-dropdown">
          <a href="${base}library/c03.html">C3 — Keras &amp; TF (10 models)</a>
          <a href="${base}library/" style="opacity:.55">More coming with each course…</a>
        </div>
      </li>

      <li class="nav-item nav-tracker">
        <a class="nav-link" href="${base}course-tracker.html" target="_blank">📊 Tracker</a>
      </li>
    </ul>

    <button class="nav-hamburger" id="nav-hamburger" aria-label="Menu">☰</button>
  </div>
</nav>`;

  document.body.insertAdjacentHTML('afterbegin', html);

  // Wire hamburger toggle
  document.getElementById('nav-hamburger').addEventListener('click', function () {
    document.getElementById('nav-links').classList.toggle('open');
  });

  // ── Active section highlight in nav ──────────────────────────
  const _path = window.location.pathname;
  const _navLinks = document.querySelectorAll('.nav-links .nav-link');
  ['/courses/', '/viz/', '/games/', '/library/'].forEach(function(seg, i) {
    if (_path.includes(seg)) _navLinks[i].classList.add('nav-active');
  });

  // ── Back-to-hub breadcrumb (injected on sub-pages only) ──────
  let _hubHref = null, _hubLabel = null;
  if (_path.includes('/games/') && !_path.includes('/games/index.html')) {
    _hubHref = 'index.html'; _hubLabel = '← Games Hub';
  } else if (_path.includes('/viz/') && !_path.includes('/viz/index.html')) {
    _hubHref = 'index.html'; _hubLabel = '← Visualisations';
  } else if (_path.includes('/library/') && !_path.includes('/library/index.html')) {
    _hubHref = 'index.html'; _hubLabel = '← Library';
  }
  if (_hubHref) {
    document.getElementById('site-nav').insertAdjacentHTML('afterend',
      '<div class="breadcrumb-bar"><div class="breadcrumb-inner"><a href="' + _hubHref + '" class="bc-link">' + _hubLabel + '</a></div></div>'
    );
  }
}

/* ── Prize countdown ───────────────────────────────────────── */
const PRIZE_DL = new Date('2026-09-01T23:59:59');

function _renderCountdown(el) {
  const diff = PRIZE_DL - Date.now();
  if (diff <= 0) {
    el.innerHTML = `<span style="color:var(--red);font-weight:700">Deadline passed</span>`;
    return;
  }
  const d = Math.floor(diff / 86400000);
  const h = Math.floor((diff % 86400000) / 3600000);
  const m = Math.floor((diff % 3600000)  / 60000);
  const s = Math.floor((diff % 60000)    / 1000);
  const p = n => String(n).padStart(2, '0');
  const unit = (v, l) =>
    `<div class="cd-unit"><div class="cd-val">${v}</div><div class="cd-lbl">${l}</div></div>`;
  el.innerHTML =
    unit(d, 'days')   + '<div class="cd-sep">:</div>' +
    unit(p(h), 'hrs') + '<div class="cd-sep">:</div>' +
    unit(p(m), 'min') + '<div class="cd-sep">:</div>' +
    unit(p(s), 'sec');
}

/**
 * Start live countdown in the element with the given id.
 * @param {string} elementId
 */
function startCountdown(elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;
  _renderCountdown(el);
  setInterval(() => _renderCountdown(el), 1000);
}

/* ── Collapsibles ──────────────────────────────────────────── */
function initCollapsibles() {
  document.querySelectorAll('.collapse-toggle').forEach(btn => {
    btn.addEventListener('click', function () {
      this.classList.toggle('open');
      const body = this.nextElementSibling;
      if (body && body.classList.contains('collapse-body')) {
        body.classList.toggle('open');
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', initCollapsibles);

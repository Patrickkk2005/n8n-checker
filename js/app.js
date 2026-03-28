// URL of your mini PC server — must be HTTPS if the site is on GitHub Pages
const API_BASE = 'https://checker.n8n-xpert.online';

// DOM elements
const textarea = document.getElementById('json-input');
const scanBtn = document.getElementById('btn-scan');
const deepScanBtn = document.getElementById('btn-deep-scan');
const pasteBtn = document.getElementById('btn-paste');
const loadFileBtn = document.getElementById('btn-load-file');
const fileInput = document.getElementById('file-input');
const loadExampleBtn = document.getElementById('btn-load-example');
const emptyState = document.getElementById('empty-state');
const resultsContent = document.getElementById('results-content');
const errorContainer = document.getElementById('error-container');
const themeBtn = document.getElementById('btn-theme');
const iconMoon = document.getElementById('icon-moon');
const iconSun = document.getElementById('icon-sun');

function init() {
  initTheme();
  attachEvents();
}

// ── Theme ──────────────────────────────────────────────────────────────────

function initTheme() {
  const saved = localStorage.getItem('n8n-debugger-theme');
  if (saved) applyTheme(saved, false);
}

function applyTheme(theme, save = true) {
  document.documentElement.setAttribute('data-theme', theme);
  const isDark = theme === 'dark';
  iconMoon.style.display = isDark ? 'none' : '';
  iconSun.style.display = isDark ? '' : 'none';
  if (save) localStorage.setItem('n8n-debugger-theme', theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const effectiveDark = current ? current === 'dark' : systemDark;
  applyTheme(effectiveDark ? 'light' : 'dark');
}

// ── Events ─────────────────────────────────────────────────────────────────

function attachEvents() {
  scanBtn.addEventListener('click', () => runScan(false));
  deepScanBtn.addEventListener('click', () => runScan(true));
  pasteBtn.addEventListener('click', pasteFromClipboard);
  loadFileBtn.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', loadFromFile);
  loadExampleBtn.addEventListener('click', loadExample);
  themeBtn.addEventListener('click', toggleTheme);
}

// ── Error / info display ───────────────────────────────────────────────────

function showError(msg) {
  errorContainer.innerHTML = `<div class="error-msg">${escapeHtml(msg)}</div>`;
}

function clearError() {
  errorContainer.innerHTML = '';
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ── JSON parsing ───────────────────────────────────────────────────────────

function parseWorkflow(raw) {
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch {
    throw new Error("Invalid JSON. Make sure you're pasting the raw workflow export, not a screenshot or partial copy.");
  }
  if (!parsed.nodes || !Array.isArray(parsed.nodes)) {
    throw new Error('This doesn\'t look like an n8n workflow. Expected a "nodes" array in the JSON.');
  }
  if (!parsed.connections || typeof parsed.connections !== 'object') {
    throw new Error('This doesn\'t look like an n8n workflow. Expected a "connections" object in the JSON.');
  }
  return parsed;
}

// ── Scanning ───────────────────────────────────────────────────────────────

async function runScan(useAI) {
  clearError();

  const raw = textarea.value.trim();
  if (!raw) {
    showError('Paste your n8n workflow JSON above.');
    return;
  }

  let workflow;
  try {
    workflow = parseWorkflow(raw);
  } catch (err) {
    showError(err.message);
    return;
  }

  // Static scan via Python backend
  scanBtn.disabled = true;
  let staticFindings = [];
  try {
    const resp = await fetch(`${API_BASE}/api/scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ workflow }),
    });
    const data = await resp.json();
    if (!resp.ok) {
      showError(data.error || 'Scan failed. Please try again.');
      return;
    }
    staticFindings = data.findings;
  } catch {
    showError('Could not reach the server. Make sure server.py is running.');
    return;
  } finally {
    scanBtn.disabled = false;
  }

  let allFindings = staticFindings;

  // AI deep scan via Python backend
  if (useAI) {
    deepScanBtn.disabled = true;
    const origText = deepScanBtn.innerHTML;
    deepScanBtn.innerHTML = '<span class="spinner"></span> Analyzing...';
    try {
      const resp = await fetch(`${API_BASE}/api/deep-scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow, staticFindings }),
      });
      const data = await resp.json();
      if (!resp.ok) {
        showError(data.error || 'AI scan failed. Please try again.');
      } else {
        allFindings = [...staticFindings, ...data.findings];
      }
    } catch {
      showError('Could not reach the server. Make sure server.py is running.');
    } finally {
      deepScanBtn.innerHTML = origText;
      deepScanBtn.disabled = false;
    }
  }

  renderResults(workflow, allFindings);
}

// ── Results rendering ──────────────────────────────────────────────────────

function calculateHealthScore(findings) {
  let score = 100;
  for (const f of findings) {
    if (f.severity === 'critical') score -= 15;
    else if (f.severity === 'warning') score -= 8;
    else if (f.severity === 'suggestion') score -= 2;
  }
  return Math.max(0, score);
}

function renderResults(workflow, findings) {
  emptyState.style.display = 'none';
  resultsContent.style.display = 'block';

  const nodeCount = workflow.nodes.filter(n => n.type !== 'n8n-nodes-base.stickyNote').length;
  const issueCount = findings.length;
  const healthScore = calculateHealthScore(findings);

  const scoreColor = healthScore >= 80 ? 'green' : healthScore >= 50 ? 'amber' : 'red';
  const issueColor = issueCount > 0 ? 'red' : 'green';

  document.getElementById('stat-nodes').textContent = nodeCount;
  const issuesEl = document.getElementById('stat-issues');
  issuesEl.textContent = issueCount;
  issuesEl.className = `stat-value ${issueColor}`;
  const scoreEl = document.getElementById('stat-score');
  scoreEl.textContent = `${healthScore}/100`;
  scoreEl.className = `stat-value ${scoreColor}`;

  const groups = { critical: [], warning: [], suggestion: [] };
  for (const f of findings) {
    if (groups[f.severity]) groups[f.severity].push(f);
  }

  for (const key of Object.keys(groups)) {
    groups[key].sort((a, b) => {
      const aName = (a.nodeNames && a.nodeNames[0]) || '';
      const bName = (b.nodeNames && b.nodeNames[0]) || '';
      return aName.localeCompare(bName);
    });
  }

  const findingsContainer = document.getElementById('findings-container');
  findingsContainer.innerHTML = '';

  if (findings.length === 0) {
    findingsContainer.innerHTML = `
      <div class="empty-state" style="border-style: solid; border-width: 1px;">
        <h3 style="color: var(--success-text);">All clear!</h3>
        <p>No issues detected. This workflow looks well-structured.</p>
      </div>`;
    return;
  }

  const severityLabels = { critical: 'Critical', warning: 'Warnings', suggestion: 'Suggestions' };

  for (const severity of ['critical', 'warning', 'suggestion']) {
    const items = groups[severity];
    if (items.length === 0) continue;

    const section = document.createElement('section');
    section.className = 'findings-group';
    section.setAttribute('aria-label', `${severityLabels[severity]} findings`);

    const header = document.createElement('h3');
    header.className = `findings-group-header ${severity}`;
    header.textContent = `${severityLabels[severity]} — ${items.length} issue${items.length === 1 ? '' : 's'}`;
    section.appendChild(header);

    for (const finding of items) {
      section.appendChild(createFindingCard(finding));
    }

    findingsContainer.appendChild(section);
  }
}

function createFindingCard(finding) {
  const card = document.createElement('article');
  card.className = `finding-card ${finding.severity}`;

  const aiBadge = finding.isAI ? '<span class="badge ai">AI</span>' : '';

  card.innerHTML = `
    <div class="finding-header">
      <div class="finding-title-row">
        <span class="badge ${finding.severity}">${finding.severity}</span>
        ${aiBadge}
        <span class="finding-title">${escapeHtml(finding.title)}</span>
      </div>
      <p class="finding-desc">${escapeHtml(finding.description)}</p>
      ${finding.nodeNames && finding.nodeNames.length > 0
        ? `<p class="finding-nodes">Nodes: ${finding.nodeNames.map(escapeHtml).join(', ')}</p>`
        : ''}
      <button class="finding-fix-toggle" aria-expanded="false">
        <span class="arrow">&#9654;</span> How to fix
      </button>
    </div>
    <div class="finding-fix-body">
      <div class="finding-fix-content">${escapeHtml(finding.fix)}</div>
    </div>`;

  const toggle = card.querySelector('.finding-fix-toggle');
  const body = card.querySelector('.finding-fix-body');
  toggle.addEventListener('click', () => {
    const isOpen = body.classList.contains('open');
    body.classList.toggle('open');
    toggle.classList.toggle('open');
    toggle.setAttribute('aria-expanded', !isOpen);
  });

  return card;
}

// ── Input helpers ──────────────────────────────────────────────────────────

async function pasteFromClipboard() {
  try {
    const text = await navigator.clipboard.readText();
    if (!text.trim()) {
      showError('Clipboard is empty.');
      return;
    }
    textarea.value = text;
    clearError();
  } catch {
    showError('Clipboard access denied. Use Ctrl+V / Cmd+V to paste directly into the text area.');
  }
}

function loadFromFile(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (ev) => {
    textarea.value = ev.target.result;
    clearError();
  };
  reader.onerror = () => showError('Could not read the file.');
  reader.readAsText(file);
  fileInput.value = '';
}

async function loadExample() {
  loadExampleBtn.disabled = true;
  try {
    const resp = await fetch('examples/messy-workflow.json');
    if (!resp.ok) throw new Error('Failed to load example');
    const text = await resp.text();
    textarea.value = text;
    clearError();
  } catch {
    showError('Could not load the example file.');
  } finally {
    loadExampleBtn.disabled = false;
  }
}

init();

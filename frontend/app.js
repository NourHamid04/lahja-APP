(() => {
  'use strict';

  const API_BASE_URL = window.LAHJA_API_BASE_URL || 'http://localhost:8000';
  const HISTORY_KEY = 'lahja-history-v1';

  const fallbackDialects = [
    { id: 'auto', name: 'Auto detect', name_ar: 'اكتشاف تلقائي', region: 'Automatic' },
    { id: 'msa', name: 'Modern Standard Arabic', name_ar: 'العربية الفصحى', region: 'Standard' },
    { id: 'lebanese', name: 'Lebanese Arabic', name_ar: 'لبناني', region: 'Levant' },
    { id: 'syrian', name: 'Syrian Arabic', name_ar: 'سوري', region: 'Levant' },
    { id: 'palestinian', name: 'Palestinian Arabic', name_ar: 'فلسطيني', region: 'Levant' },
    { id: 'jordanian', name: 'Jordanian Arabic', name_ar: 'أردني', region: 'Levant' },
    { id: 'egyptian', name: 'Egyptian Arabic', name_ar: 'مصري', region: 'Egypt' },
    { id: 'gulf', name: 'Gulf Arabic', name_ar: 'خليجي', region: 'Gulf' },
    { id: 'iraqi', name: 'Iraqi Arabic', name_ar: 'عراقي', region: 'Iraq' },
    { id: 'moroccan', name: 'Moroccan Arabic (Darija)', name_ar: 'مغربي / دارجة', region: 'North Africa' },
  ];

  const elements = {
    source: document.querySelector('#source-dialect'),
    target: document.querySelector('#target-dialect'),
    tone: document.querySelector('#tone'),
    inputScript: document.querySelector('#input-script'),
    outputScript: document.querySelector('#output-script'),
    sourceText: document.querySelector('#source-text'),
    resultArea: document.querySelector('#result-area'),
    transformButton: document.querySelector('#transform-button'),
    copyButton: document.querySelector('#copy-button'),
    clearButton: document.querySelector('#clear-button'),
    swapButton: document.querySelector('#swap-button'),
    characterCount: document.querySelector('#character-count'),
    outputTitle: document.querySelector('#output-title'),
    outputMeta: document.querySelector('#output-meta'),
    confidenceLabel: document.querySelector('#confidence-label'),
    alerts: document.querySelector('#alerts'),
    insightGrid: document.querySelector('#insight-grid'),
    historyToggle: document.querySelector('#history-toggle'),
    historyDrawer: document.querySelector('#history-drawer'),
    historyClose: document.querySelector('#history-close'),
    historyList: document.querySelector('#history-list'),
    clearHistory: document.querySelector('#clear-history'),
    backdrop: document.querySelector('#drawer-backdrop'),
  };

  let dialects = fallbackDialects;
  let currentResult = null;
  let activeController = null;
  let history = loadHistory();

  function escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function textDirection(text) {
    return /[\u0600-\u06ff]/.test(text) ? 'rtl' : 'ltr';
  }

  function dialectName(id) {
    return dialects.find((dialect) => dialect.id === id)?.name || id;
  }

  function renderDialectOptions() {
    const groups = new Map();
    dialects.forEach((dialect) => {
      if (!groups.has(dialect.region)) groups.set(dialect.region, []);
      groups.get(dialect.region).push(dialect);
    });

    const createOptions = (allowAuto) => {
      let html = '';
      groups.forEach((items, region) => {
        const filtered = allowAuto ? items : items.filter((item) => item.id !== 'auto');
        if (!filtered.length) return;
        html += `<optgroup label="${escapeHtml(region)}">`;
        filtered.forEach((dialect) => {
          html += `<option value="${escapeHtml(dialect.id)}">${escapeHtml(dialect.name)} — ${escapeHtml(dialect.name_ar)}</option>`;
        });
        html += '</optgroup>';
      });
      return html;
    };

    elements.source.innerHTML = createOptions(true);
    elements.target.innerHTML = createOptions(false);
    elements.source.value = dialects.some((item) => item.id === 'lebanese') ? 'lebanese' : 'auto';
    elements.target.value = dialects.some((item) => item.id === 'syrian') ? 'syrian' : dialects.find((item) => item.id !== 'auto')?.id || 'msa';
    updateOutputTitle();
  }

  async function loadDialects() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/dialects`);
      if (!response.ok) throw new Error('Could not load dialects.');
      const body = await response.json();
      if (Array.isArray(body.dialects) && body.dialects.length) dialects = body.dialects;
    } catch {
      // The fallback list lets the UI remain usable while the backend starts.
    }
    renderDialectOptions();
  }

  function updateOutputTitle() {
    elements.outputTitle.textContent = `Natural ${dialectName(elements.target.value)}`;
  }

  function updateCharacterCount() {
    elements.characterCount.textContent = `${elements.sourceText.value.length} / 2000`;
    elements.sourceText.dir = textDirection(elements.sourceText.value);
  }

  function clearAlerts() {
    elements.alerts.innerHTML = '';
  }

  function addAlert(message, type) {
    const alert = document.createElement('div');
    alert.className = `alert ${type}`;
    alert.textContent = message;
    elements.alerts.appendChild(alert);
  }

  function setLoading(isLoading) {
    elements.transformButton.disabled = isLoading;
    elements.transformButton.innerHTML = isLoading ? 'Transforming…' : 'Transform dialect <span aria-hidden="true">✦</span>';
    if (isLoading) {
      elements.resultArea.className = 'result-area';
      elements.resultArea.dir = 'ltr';
      elements.resultArea.innerHTML = '<div class="loading-state"><span class="spinner"></span> Lahja is understanding the context…</div>';
      elements.outputMeta.textContent = 'Calling the backend securely…';
      elements.confidenceLabel.textContent = 'Working';
      elements.copyButton.disabled = true;
    }
  }

  function renderEmptyResult() {
    currentResult = null;
    elements.resultArea.className = 'result-area empty';
    elements.resultArea.dir = 'rtl';
    elements.resultArea.innerHTML = '<div class="empty-state"><span>لهجة</span><p>Meaning preserved. Dialect transformed.</p></div>';
    elements.outputMeta.textContent = 'Your transformed message appears here';
    elements.confidenceLabel.textContent = 'Ready';
    elements.copyButton.disabled = true;
    elements.insightGrid.hidden = true;
    elements.insightGrid.innerHTML = '';
  }

  function renderResult(result) {
    currentResult = result;
    elements.resultArea.className = 'result-area';
    elements.resultArea.dir = textDirection(result.transformed_text);
    const paragraph = document.createElement('p');
    paragraph.textContent = result.transformed_text;
    elements.resultArea.replaceChildren(paragraph);
    elements.outputMeta.textContent = `${result.latency_ms} ms · ${result.model}`;
    elements.confidenceLabel.textContent = `${Math.round(result.confidence * 100)}% confidence`;
    elements.copyButton.disabled = false;
    elements.copyButton.textContent = 'Copy';

    clearAlerts();
    if (result.mock_mode) addAlert('Mock mode is active. Add your API key to test real AI results.', 'warning');

    const cards = [];
    cards.push(`
      <div class="insight-card">
        <span class="insight-label">Detected</span>
        <strong>${escapeHtml(result.detected_source_dialect)}</strong>
        <p>${escapeHtml(result.detected_input_script)} input</p>
      </div>
    `);

    const notes = [...(result.notes || []), ...(result.warnings || [])].slice(0, 3);
    if (notes.length) {
      cards.push(`
        <div class="insight-card wide">
          <span class="insight-label">Lahja notes</span>
          ${notes.map((note) => `<p>• ${escapeHtml(note)}</p>`).join('')}
        </div>
      `);
    }

    const alternatives = result.alternatives || [];
    if (alternatives.length) {
      cards.push(`
        <div class="insight-card wide">
          <span class="insight-label">Alternatives</span>
          ${alternatives.map((alternative, index) => `<button type="button" data-alternative-index="${index}">${escapeHtml(alternative)}</button>`).join('')}
        </div>
      `);
    }

    elements.insightGrid.innerHTML = cards.join('');
    elements.insightGrid.hidden = cards.length === 0;
    elements.insightGrid.querySelectorAll('[data-alternative-index]').forEach((button) => {
      button.addEventListener('click', () => {
        elements.sourceText.value = alternatives[Number(button.dataset.alternativeIndex)];
        updateCharacterCount();
      });
    });
  }

  async function parseError(response) {
    try {
      const body = await response.json();
      if (typeof body.detail === 'string') return body.detail;
      if (Array.isArray(body.detail)) return body.detail.map((item) => item.msg).filter(Boolean).join(', ');
    } catch {
      // Use the status fallback below.
    }
    return `Request failed with status ${response.status}`;
  }

  async function transform() {
    const text = elements.sourceText.value.trim();
    if (!text) {
      clearAlerts();
      addAlert('Write a message first.', 'error');
      return;
    }

    activeController?.abort();
    activeController = new AbortController();
    clearAlerts();
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/transform`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: activeController.signal,
        body: JSON.stringify({
          text,
          source_dialect: elements.source.value,
          target_dialect: elements.target.value,
          input_script: elements.inputScript.value,
          output_script: elements.outputScript.value,
          tone: elements.tone.value,
          preserve_names: true,
        }),
      });

      if (!response.ok) throw new Error(await parseError(response));
      const result = await response.json();
      renderResult(result);
      saveHistory({
        id: result.request_id,
        createdAt: new Date().toISOString(),
        sourceName: dialectName(elements.source.value),
        targetName: dialectName(elements.target.value),
        input: text,
        output: result.transformed_text,
      });
    } catch (error) {
      if (error.name === 'AbortError') return;
      renderEmptyResult();
      clearAlerts();
      addAlert(error instanceof Error ? error.message : 'Something went wrong.', 'error');
    } finally {
      elements.transformButton.disabled = false;
      elements.transformButton.innerHTML = 'Transform dialect <span aria-hidden="true">✦</span>';
    }
  }

  function swapDialects() {
    const source = elements.source.value;
    const target = elements.target.value;
    elements.source.value = target;
    elements.target.value = source === 'auto' ? 'msa' : source;
    if (currentResult) elements.sourceText.value = currentResult.transformed_text;
    renderEmptyResult();
    updateCharacterCount();
    updateOutputTitle();
  }

  async function copyResult() {
    if (!currentResult) return;
    try {
      await navigator.clipboard.writeText(currentResult.transformed_text);
      elements.copyButton.textContent = 'Copied ✓';
      setTimeout(() => { elements.copyButton.textContent = 'Copy'; }, 1500);
    } catch {
      addAlert('Copy failed. Select the result and copy it manually.', 'error');
    }
  }

  function loadHistory() {
    try {
      const parsed = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }

  function saveHistory(item) {
    history = [item, ...history.filter((entry) => entry.id !== item.id)].slice(0, 12);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    renderHistory();
  }

  function renderHistory() {
    if (!history.length) {
      elements.historyList.innerHTML = '<p class="drawer-empty">Your recent transformations will appear here.</p>';
      elements.clearHistory.hidden = true;
      return;
    }

    elements.historyList.innerHTML = history.map((item, index) => `
      <button class="history-item" type="button" data-history-index="${index}">
        <span>${escapeHtml(item.sourceName)} → ${escapeHtml(item.targetName)}</span>
        <strong dir="${textDirection(item.output)}">${escapeHtml(item.output)}</strong>
        <small>${escapeHtml(new Date(item.createdAt).toLocaleString())}</small>
      </button>
    `).join('');
    elements.clearHistory.hidden = false;

    elements.historyList.querySelectorAll('[data-history-index]').forEach((button) => {
      button.addEventListener('click', () => {
        const item = history[Number(button.dataset.historyIndex)];
        elements.sourceText.value = item.input;
        updateCharacterCount();
        renderEmptyResult();
        closeHistory();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    });
  }

  function openHistory() {
    elements.historyDrawer.classList.add('open');
    elements.historyDrawer.setAttribute('aria-hidden', 'false');
    elements.backdrop.hidden = false;
  }

  function closeHistory() {
    elements.historyDrawer.classList.remove('open');
    elements.historyDrawer.setAttribute('aria-hidden', 'true');
    elements.backdrop.hidden = true;
  }

  function clearHistory() {
    history = [];
    localStorage.removeItem(HISTORY_KEY);
    renderHistory();
  }

  elements.sourceText.addEventListener('input', updateCharacterCount);
  elements.target.addEventListener('change', updateOutputTitle);
  elements.transformButton.addEventListener('click', transform);
  elements.copyButton.addEventListener('click', copyResult);
  elements.swapButton.addEventListener('click', swapDialects);
  elements.clearButton.addEventListener('click', () => {
    elements.sourceText.value = '';
    updateCharacterCount();
    clearAlerts();
    renderEmptyResult();
    elements.sourceText.focus();
  });
  elements.historyToggle.addEventListener('click', openHistory);
  elements.historyClose.addEventListener('click', closeHistory);
  elements.backdrop.addEventListener('click', closeHistory);
  elements.clearHistory.addEventListener('click', clearHistory);

  document.querySelectorAll('.example-card').forEach((card) => {
    card.addEventListener('click', () => {
      elements.source.value = card.dataset.source;
      elements.target.value = card.dataset.target;
      elements.sourceText.value = card.dataset.text;
      updateCharacterCount();
      updateOutputTitle();
      renderEmptyResult();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  document.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') transform();
    if (event.key === 'Escape') closeHistory();
  });

  loadDialects();
  updateCharacterCount();
  renderHistory();
})();

/**
 * PaperMind AI — Modern Client Application Logic
 * Integrates with FastAPI RAG backend, Supabase pgvector, and Google Gemini
 */

document.addEventListener("DOMContentLoaded", () => {
  // Global State
  const state = {
    papers: [],
    searchResults: [],
    activeScope: "",
    isQuerying: false,
    ingestingPapers: new Set(),
  };

  // DOM Elements
  const elements = {
    // Header & Telemetry
    statusSupabase: document.getElementById("status-supabase"),
    statusGemini: document.getElementById("status-gemini"),
    headerPapersCount: document.getElementById("header-papers-count"),
    headerChunksCount: document.getElementById("header-chunks-count"),
    btnRefreshStatus: document.getElementById("btn-refresh-status"),

    // Tabs
    tabBtnSearch: document.getElementById("tab-btn-search"),
    tabBtnLibrary: document.getElementById("tab-btn-library"),
    tabPaneSearch: document.getElementById("tab-pane-search"),
    tabPaneLibrary: document.getElementById("tab-pane-library"),
    tabLibraryBadge: document.getElementById("tab-library-badge"),

    // arXiv Search
    searchForm: document.getElementById("search-form"),
    arxivSearchInput: document.getElementById("arxiv-search-input"),
    btnSearchArxiv: document.getElementById("btn-search-arxiv"),
    searchResultsList: document.getElementById("search-results-list"),
    searchEmptyState: document.getElementById("search-empty-state"),
    topicChips: document.querySelectorAll(".topic-chip"),

    // Paper Library
    libraryCardsList: document.getElementById("library-cards-list"),
    libraryEmptyState: document.getElementById("library-empty-state"),
    libraryFilterInput: document.getElementById("library-filter-input"),

    // Chat Area
    paperScopeSelect: document.getElementById("paper-scope-select"),
    btnClearChat: document.getElementById("btn-clear-chat"),
    chatMessagesContainer: document.getElementById("chat-messages-container"),
    chatWelcomeCard: document.getElementById("chat-welcome-card"),
    chatForm: document.getElementById("chat-form"),
    chatTextarea: document.getElementById("chat-textarea"),
    btnSendQuery: document.getElementById("btn-send-query"),
    suggestionCards: document.querySelectorAll(".suggestion-card"),
    toastContainer: document.getElementById("toast-container"),
  };

  // ==========================================
  // Toast Notifications
  // ==========================================
  function showToast(message, type = "info", duration = 4000) {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    
    let icon = "ℹ️";
    if (type === "success") icon = "✓";
    if (type === "error") icon = "⚠️";

    toast.innerHTML = `<span>${icon}</span> <span>${escapeHtml(message)}</span>`;
    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(-10px)";
      toast.style.transition = "all 0.25s ease";
      setTimeout(() => toast.remove(), 250);
    }, duration);
  }

  function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.innerText = text;
    return div.innerHTML;
  }

  // ==========================================
  // API Calls & System Status
  // ==========================================
  async function fetchStatus() {
    try {
      const res = await fetch("/api/status");
      const data = await res.json();
      
      if (data.status === "online") {
        elements.statusSupabase.classList.toggle("error", !data.supabase_connected);
        elements.statusGemini.classList.toggle("error", !data.gemini_connected);
        
        elements.headerPapersCount.textContent = `${data.papers_count} paper${data.papers_count === 1 ? '' : 's'}`;
        elements.headerChunksCount.textContent = `${data.total_chunks} chunks`;
        elements.tabLibraryBadge.textContent = data.papers_count;
      }
    } catch (err) {
      console.warn("Failed to fetch system status:", err);
      elements.statusSupabase.classList.add("error");
      elements.statusGemini.classList.add("error");
    }
  }

  async function fetchPapers() {
    try {
      const res = await fetch("/api/papers");
      const data = await res.json();
      state.papers = data.papers || [];
      renderLibrary(state.papers);
      updateScopeDropdown();
      fetchStatus();
    } catch (err) {
      console.error("Failed to load papers:", err);
      showToast("Could not load indexed papers.", "error");
    }
  }

  // ==========================================
  // Scope Dropdown & Library Rendering
  // ==========================================
  function updateScopeDropdown() {
    const currentVal = elements.paperScopeSelect.value;
    elements.paperScopeSelect.innerHTML = `<option value="">🌐 All Indexed Papers (Cross-Paper Synthesis)</option>`;

    state.papers.forEach((paper) => {
      const opt = document.createElement("option");
      opt.value = paper.filename;
      opt.textContent = `📄 ${paper.title} (${paper.chunk_count} chunks)`;
      elements.paperScopeSelect.appendChild(opt);
    });

    if (currentVal && state.papers.some(p => p.filename === currentVal)) {
      elements.paperScopeSelect.value = currentVal;
    }
  }

  function renderLibrary(papersList) {
    elements.libraryCardsList.innerHTML = "";

    if (!papersList || papersList.length === 0) {
      elements.libraryEmptyState.hidden = false;
      return;
    }

    elements.libraryEmptyState.hidden = true;

    papersList.forEach((paper) => {
      const card = document.createElement("div");
      card.className = "paper-card";
      card.innerHTML = `
        <div class="paper-card-header">
          <h3 class="paper-card-title">${escapeHtml(paper.title)}</h3>
        </div>
        <div class="paper-card-meta">
          <span class="paper-meta-badge">📊 ${paper.chunk_count} Chunks</span>
          <span class="paper-meta-badge">🔍 384-d Vectorized</span>
        </div>
        <div class="paper-card-footer">
          <button class="btn btn-secondary btn-sm btn-focus-paper" data-filename="${escapeHtml(paper.filename)}">
            💬 Focus Chat
          </button>
          <button class="btn btn-danger btn-sm btn-delete-paper" data-filename="${escapeHtml(paper.filename)}">
            🗑 Delete
          </button>
        </div>
      `;

      card.querySelector(".btn-focus-paper").addEventListener("click", () => {
        elements.paperScopeSelect.value = paper.filename;
        state.activeScope = paper.filename;
        showToast(`Chat scope focused on: "${paper.title}"`, "info");
      });

      card.querySelector(".btn-delete-paper").addEventListener("click", () => {
        handleDeletePaper(paper.filename, paper.title);
      });

      elements.libraryCardsList.appendChild(card);
    });
  }

  async function handleDeletePaper(filename, title) {
    if (!confirm(`Are you sure you want to delete "${title}"? This will delete chunks from pgvector and storage.`)) {
      return;
    }

    try {
      showToast(`Deleting "${title}"...`, "info");
      const res = await fetch(`/api/papers/${encodeURIComponent(filename)}`, { method: "DELETE" });
      const data = await res.json();

      if (data.success) {
        showToast(`Deleted "${title}" successfully.`, "success");
        if (state.activeScope === filename) {
          state.activeScope = "";
          elements.paperScopeSelect.value = "";
        }
        await fetchPapers();
      } else {
        showToast(data.message || "Failed to delete paper.", "error");
      }
    } catch (err) {
      showToast("Error deleting paper: " + err.message, "error");
    }
  }

  // ==========================================
  // arXiv Search & Ingestion Flow
  // ==========================================
  async function handleArxivSearch(query) {
    if (!query || !query.trim()) return;

    elements.btnSearchArxiv.disabled = true;
    elements.btnSearchArxiv.innerHTML = `<span class="spinner"></span> Searching...`;
    elements.searchEmptyState.style.display = "none";
    elements.searchResultsList.innerHTML = `
      <div style="text-align: center; padding: 30px; color: var(--text-muted);">
        <span class="spinner" style="width: 24px; height: 24px; border-width: 3px;"></span>
        <p style="margin-top: 10px; font-size: 0.85rem;">Querying arXiv API for "${escapeHtml(query)}"...</p>
      </div>
    `;

    try {
      const res = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query.trim(), max_results: 6 })
      });
      const data = await res.json();
      state.searchResults = data.results || [];
      renderSearchResults(state.searchResults);
    } catch (err) {
      elements.searchResultsList.innerHTML = `
        <div style="padding: 20px; color: var(--accent-rose); text-align: center;">
          Failed to search arXiv: ${escapeHtml(err.message)}
        </div>
      `;
      showToast("Search failed. Check your internet connection.", "error");
    } finally {
      elements.btnSearchArxiv.disabled = false;
      elements.btnSearchArxiv.innerHTML = `Search`;
    }
  }

  function renderSearchResults(results) {
    elements.searchResultsList.innerHTML = "";

    if (!results || results.length === 0) {
      elements.searchResultsList.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">🔍</div>
          <p class="empty-title">No matching papers found</p>
          <p class="empty-desc">Try different keywords, author names, or arXiv identifiers.</p>
        </div>
      `;
      return;
    }

    const indexedSet = new Set(state.papers.map(p => p.filename));

    results.forEach((paper) => {
      const isAlreadyIndexed = indexedSet.has(paper.filename) || paper.is_indexed;
      const isIngesting = state.ingestingPapers.has(paper.filename);

      const card = document.createElement("div");
      card.className = "paper-card";
      card.id = `paper-${paper.filename.replace(/[^a-zA-Z0-9]/g, '_')}`;

      card.innerHTML = `
        <div class="paper-card-header">
          <h3 class="paper-card-title">${escapeHtml(paper.title)}</h3>
        </div>

        <div class="paper-card-meta">
          <span class="paper-meta-badge">📅 ${escapeHtml(paper.published || 'Recent')}</span>
          <span class="paper-meta-badge">👥 ${escapeHtml(paper.authors.slice(0, 3).join(', '))}${paper.authors.length > 3 ? ' et al.' : ''}</span>
        </div>

        <p class="paper-card-summary" id="summary-${card.id}">${escapeHtml(paper.summary)}</p>
        <button type="button" class="toggle-summary-btn" data-target="summary-${card.id}">Show full abstract</button>

        <div class="paper-card-footer">
          <a href="${escapeHtml(paper.pdf_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-ghost btn-sm" title="Open PDF from arXiv">
            🔗 arXiv PDF
          </a>

          <div class="card-action-box">
            ${isAlreadyIndexed ? `
              <span class="status-tag-indexed">✓ In Knowledge Base</span>
            ` : isIngesting ? `
              <div class="ingest-progress-box">
                <span class="spinner"></span>
                <span>Vectorizing...</span>
              </div>
            ` : `
              <button class="btn btn-primary btn-sm btn-ingest" data-url="${escapeHtml(paper.pdf_url)}" data-title="${escapeHtml(paper.title)}">
                ⚡ Ingest & Analyze
              </button>
            `}
          </div>
        </div>
      `;

      // Abstract toggle
      const toggleBtn = card.querySelector(".toggle-summary-btn");
      const summaryP = card.querySelector(".paper-card-summary");
      toggleBtn.addEventListener("click", () => {
        const isExp = summaryP.classList.toggle("expanded");
        if (isExp) {
          summaryP.textContent = paper.full_summary;
          toggleBtn.textContent = "Show less";
        } else {
          summaryP.textContent = paper.summary;
          toggleBtn.textContent = "Show full abstract";
        }
      });

      // Ingest action
      const ingestBtn = card.querySelector(".btn-ingest");
      if (ingestBtn) {
        ingestBtn.addEventListener("click", () => {
          handleIngest(paper.pdf_url, paper.title, paper.filename, card);
        });
      }

      elements.searchResultsList.appendChild(card);
    });
  }

  async function handleIngest(pdfUrl, title, filename, cardElement) {
    if (state.ingestingPapers.has(filename)) return;

    state.ingestingPapers.add(filename);
    const actionBox = cardElement.querySelector(".card-action-box");
    actionBox.innerHTML = `
      <div class="ingest-progress-box">
        <span class="spinner"></span>
        <span id="ingest-step-text">Downloading PDF...</span>
      </div>
    `;

    const stepText = actionBox.querySelector("#ingest-step-text");
    const stepTimer = setTimeout(() => {
      if (stepText) stepText.textContent = "Extracting & Chunking...";
    }, 3500);
    const stepTimer2 = setTimeout(() => {
      if (stepText) stepText.textContent = "Generating 384-d Embeddings...";
    }, 7000);

    try {
      const res = await fetch("/api/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pdf_url: pdfUrl, title: title })
      });
      const data = await res.json();

      clearTimeout(stepTimer);
      clearTimeout(stepTimer2);

      if (data.success) {
        actionBox.innerHTML = `<span class="status-tag-indexed">✓ Ingested (${data.chunks_count} chunks)</span>`;
        showToast(`Successfully indexed "${title}" (${data.chunks_count} chunks)`, "success");
        await fetchPapers();
      } else {
        actionBox.innerHTML = `
          <button class="btn btn-primary btn-sm btn-ingest" data-url="${escapeHtml(pdfUrl)}" data-title="${escapeHtml(title)}">
            Retry Ingest
          </button>
        `;
        showToast(data.message || "Failed to ingest paper.", "error");
      }
    } catch (err) {
      clearTimeout(stepTimer);
      clearTimeout(stepTimer2);
      actionBox.innerHTML = `<span style="color: var(--accent-rose); font-size: 0.75rem;">Failed</span>`;
      showToast("Ingestion failed: " + err.message, "error");
    } finally {
      state.ingestingPapers.delete(filename);
    }
  }

  // ==========================================
  // Chat & Q&A Flow
  // ==========================================
  function appendMessage(role, text, sources = []) {
    // Hide welcome card once conversation begins
    if (elements.chatWelcomeCard) {
      elements.chatWelcomeCard.style.display = "none";
    }

    const row = document.createElement("div");
    row.className = `message-row ${role}`;

    if (role === "user") {
      row.innerHTML = `
        <div class="message-content-wrapper">
          <div class="user-bubble">${escapeHtml(text)}</div>
        </div>
      `;
    } else {
      let formattedText = formatMarkdown(text);
      let sourcesHtml = "";

      if (sources && sources.length > 0) {
        const sourcesListItems = sources.map((src) => `
          <div class="source-item">
            <div class="source-item-header">
              <span class="source-title">📄 ${escapeHtml(src.paper_title)}</span>
              ${src.similarity_pct ? `<span class="source-relevance">${src.similarity_pct}% relevance</span>` : ''}
            </div>
            <div class="source-excerpt">${escapeHtml(src.chunk_text)}</div>
          </div>
        `).join("");

        sourcesHtml = `
          <div class="sources-card">
            <button class="sources-toggle" type="button">
              <div class="sources-toggle-left">
                <span>📚 Grounded in ${sources.length} paper excerpt${sources.length > 1 ? 's' : ''}</span>
              </div>
              <svg class="sources-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </button>
            <div class="sources-list">${sourcesListItems}</div>
          </div>
        `;
      }

      row.innerHTML = `
        <div class="avatar avatar-ai" title="AI Research Assistant">✦</div>
        <div class="message-content-wrapper">
          <div class="assistant-bubble">${formattedText}</div>
          ${sourcesHtml}
        </div>
      `;

      // Accordion listener for sources
      const sourcesToggle = row.querySelector(".sources-toggle");
      if (sourcesToggle) {
        sourcesToggle.addEventListener("click", () => {
          row.querySelector(".sources-card").classList.toggle("open");
        });
      }
    }

    elements.chatMessagesContainer.appendChild(row);
    elements.chatMessagesContainer.scrollTop = elements.chatMessagesContainer.scrollHeight;
    return row;
  }

  function appendThinkingMessage() {
    if (elements.chatWelcomeCard) {
      elements.chatWelcomeCard.style.display = "none";
    }

    const row = document.createElement("div");
    row.className = "message-row assistant thinking-message";
    row.innerHTML = `
      <div class="avatar avatar-ai">✦</div>
      <div class="message-content-wrapper">
        <div class="assistant-bubble" style="display: flex; align-items: center; gap: 8px; color: var(--text-muted);">
          <span class="spinner"></span>
          <span>Searching vector database and synthesizing answer with Gemini...</span>
        </div>
      </div>
    `;
    elements.chatMessagesContainer.appendChild(row);
    elements.chatMessagesContainer.scrollTop = elements.chatMessagesContainer.scrollHeight;
    return row;
  }

  async function handleSendQuery(question) {
    if (!question || !question.trim() || state.isQuerying) return;

    const trimmedQuestion = question.trim();
    appendMessage("user", trimmedQuestion);

    elements.chatTextarea.value = "";
    elements.chatTextarea.style.height = "auto";
    state.isQuerying = true;
    elements.btnSendQuery.disabled = true;

    const thinkingRow = appendThinkingMessage();

    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: trimmedQuestion,
          paper_filter: state.activeScope || null,
          top_k: 5
        })
      });

      const data = await res.json();
      thinkingRow.remove();

      if (data.answer) {
        appendMessage("assistant", data.answer, data.sources || []);
      } else {
        appendMessage("assistant", "Sorry, an unexpected response occurred while querying the papers.");
      }
    } catch (err) {
      thinkingRow.remove();
      appendMessage("assistant", `⚠️ An error occurred while generating the response: ${err.message}`);
      showToast("Query error: " + err.message, "error");
    } finally {
      state.isQuerying = false;
      elements.btnSendQuery.disabled = false;
      elements.chatTextarea.focus();
    }
  }

  // Light-weight Markdown Formatter for Assistant Responses
  function formatMarkdown(text) {
    if (!text) return "";
    let clean = escapeHtml(text);

    // Headers (### Header)
    clean = clean.replace(/^### (.*$)/gim, '<h4 style="font-size:0.95rem; font-weight:700; margin:10px 0 4px 0; color:#fff;">$1</h4>');
    clean = clean.replace(/^## (.*$)/gim, '<h3 style="font-size:1.05rem; font-weight:700; margin:12px 0 6px 0; color:#fff;">$1</h3>');
    clean = clean.replace(/^# (.*$)/gim, '<h2 style="font-size:1.15rem; font-weight:800; margin:14px 0 8px 0; color:#fff;">$1</h2>');

    // Bold (**text**)
    clean = clean.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Inline code (`code`)
    clean = clean.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Bullet lists (* or -)
    clean = clean.replace(/^\s*[\*\-]\s+(.*)$/gim, '<li>$1</li>');
    clean = clean.replace(/(<li>.*<\/li>)/gms, '<ul>$1</ul>');

    // Numbered lists (1. text)
    clean = clean.replace(/^\s*\d+\.\s+(.*)$/gim, '<li>$1</li>');

    // Paragraph line breaks
    clean = clean.replace(/\n\n+/g, '</p><p>');
    clean = '<p>' + clean + '</p>';
    clean = clean.replace(/<p><\/p>/g, '');
    clean = clean.replace(/<p>(<h[2-4]>.*?<\/h[2-4]>)<\/p>/g, '$1');
    clean = clean.replace(/<p>(<ul>.*?<\/ul>)<\/p>/gs, '$1');

    return clean;
  }

  // ==========================================
  // Event Listeners & Interaction Wiring
  // ==========================================
  
  // Tab Switching
  elements.tabBtnSearch.addEventListener("click", () => {
    elements.tabBtnSearch.classList.add("active");
    elements.tabBtnLibrary.classList.remove("active");
    elements.tabPaneSearch.hidden = false;
    elements.tabPaneLibrary.hidden = true;
  });

  elements.tabBtnLibrary.addEventListener("click", () => {
    elements.tabBtnLibrary.classList.add("active");
    elements.tabBtnSearch.classList.remove("active");
    elements.tabPaneLibrary.hidden = false;
    elements.tabPaneSearch.hidden = true;
  });

  // arXiv Search Submit
  elements.searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    handleArxivSearch(elements.arxivSearchInput.value);
  });

  // Topic Chips
  elements.topicChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-query");
      elements.arxivSearchInput.value = q;
      handleArxivSearch(q);
    });
  });

  // Library Filter Search
  elements.libraryFilterInput.addEventListener("input", (e) => {
    const term = e.target.value.toLowerCase();
    const filtered = state.papers.filter(p => p.title.toLowerCase().includes(term));
    renderLibrary(filtered);
  });

  // Scope Selection
  elements.paperScopeSelect.addEventListener("change", (e) => {
    state.activeScope = e.target.value;
    if (state.activeScope) {
      showToast(`Active chat scope set to: ${elements.paperScopeSelect.selectedOptions[0].text}`, "info");
    } else {
      showToast("Active chat scope set to: All Indexed Papers", "info");
    }
  });

  // Clear Chat
  elements.btnClearChat.addEventListener("click", () => {
    elements.chatMessagesContainer.innerHTML = "";
    if (elements.chatWelcomeCard) {
      elements.chatMessagesContainer.appendChild(elements.chatWelcomeCard);
      elements.chatWelcomeCard.style.display = "block";
    }
    showToast("Chat conversation cleared.", "info");
  });

  // Chat Form Submit
  elements.chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    handleSendQuery(elements.chatTextarea.value);
  });

  // Chat Textarea Enter / Auto-resize
  elements.chatTextarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      elements.chatForm.dispatchEvent(new Event("submit"));
    }
  });

  elements.chatTextarea.addEventListener("input", () => {
    elements.chatTextarea.style.height = "auto";
    elements.chatTextarea.style.height = `${Math.min(elements.chatTextarea.scrollHeight, 140)}px`;
  });

  // Starter Query Suggestions
  elements.suggestionCards.forEach((card) => {
    card.addEventListener("click", () => {
      const prompt = card.getAttribute("data-prompt");
      handleSendQuery(prompt);
    });
  });

  // Refresh Telemetry
  elements.btnRefreshStatus.addEventListener("click", () => {
    fetchPapers();
    fetchStatus();
    showToast("Refreshed system status and paper library.", "info");
  });

  // Initial Load
  fetchStatus();
  fetchPapers();
});

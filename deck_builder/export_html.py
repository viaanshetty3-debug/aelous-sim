#!/usr/bin/env python3
"""Generates a standalone, touch-optimized interactive HTML presentation for Android tablets.

Features:
- Offline-ready (zero external dependencies).
- Touch swipe gestures for tablet navigation.
- Slide jump dropdown categorized across all 6 parts.
- Collapsible Professor Lecture Notes drawer on every slide.
- Keyboard navigation (arrows, space, full-screen, notes toggle).
- Modern Deep Slate (#0B1120) UI with electric neon accents.
"""

import os
import sys
import json
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from deck_builder.part0_intro import get_part0_slides
from deck_builder.part1_governing import get_part1_slides
from deck_builder.part2_microphysics import get_part2_slides
from deck_builder.part3_kinematics import get_part3_slides
from deck_builder.part4_cfd_verification import get_part4_slides
from deck_builder.part5_code_ledger import get_part5_slides
from deck_builder.part6_hardware_prototype import get_part6_slides

def compile_all_slides():
    slides = []
    slides.extend(get_part0_slides())
    slides.extend(get_part1_slides())
    slides.extend(get_part2_slides())
    slides.extend(get_part3_slides())
    slides.extend(get_part4_slides())
    slides.extend(get_part5_slides())
    slides.extend(get_part6_slides())
    return slides

def generate_interactive_html(output_path):
    slides = compile_all_slides()
    slides_json = json.dumps(slides, ensure_ascii=False)

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Project AEOLUS: Master Technical Briefing (82 Slides)</title>
  <style>
    :root {
      --bg-dark: #0B1120;
      --card-bg: #162032;
      --card-border: #334155;
      --code-bg: #070B14;
      --accent-cyan: #38BDF8;
      --accent-green: #34D399;
      --accent-amber: #F59E0B;
      --accent-coral: #F87171;
      --text-white: #FFFFFF;
      --text-body: #E2E8F0;
      --text-muted: #94A3B8;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-tap-highlight-color: transparent;
    }

    body {
      background-color: var(--bg-dark);
      color: var(--text-body);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
      user-select: text;
    }

    /* Top Control Bar */
    header {
      background: #0F172A;
      border-bottom: 1px solid var(--card-border);
      padding: 8px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      z-index: 100;
      position: sticky;
      top: 0;
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .project-logo {
      font-size: 15px;
      font-weight: 800;
      color: var(--accent-cyan);
      letter-spacing: 1px;
      white-space: nowrap;
    }

    .slide-badge {
      background: #1E293B;
      color: var(--accent-cyan);
      border: 1px solid var(--card-border);
      font-size: 11px;
      font-weight: 700;
      padding: 4px 8px;
      border-radius: 6px;
      white-space: nowrap;
    }

    .slide-select {
      background: #1E293B;
      color: #F1F5F9;
      border: 1px solid var(--card-border);
      border-radius: 6px;
      padding: 6px 10px;
      font-size: 13px;
      max-width: 320px;
      outline: none;
      cursor: pointer;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .btn {
      background: #1E293B;
      color: #F8FAFC;
      border: 1px solid var(--card-border);
      padding: 7px 12px;
      font-size: 13px;
      font-weight: 600;
      border-radius: 6px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }

    .btn:hover {
      background: #334155;
      border-color: var(--accent-cyan);
    }

    .btn-primary {
      background: #0284C7;
      border-color: #38BDF8;
      color: #FFFFFF;
    }

    .btn-primary:hover {
      background: #0369A1;
    }

    /* Progress bar */
    .progress-bar-container {
      width: 100%;
      height: 3px;
      background: #1E293B;
    }

    .progress-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, #38BDF8, #34D399);
      width: 0%;
      transition: width 0.2s ease;
    }

    /* Main Slide Presentation Stage */
    main {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 16px;
      position: relative;
    }

    .slide-wrapper {
      width: 100%;
      max-width: 1200px;
      background: #0F172A;
      border: 1px solid var(--card-border);
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      min-height: 580px;
      animation: fadeIn 0.2s ease-in-out;
    }

    @keyframes fadeIn {
      from { opacity: 0.85; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .slide-header {
      padding: 20px 24px 14px 24px;
      border-bottom: 1px solid rgba(51, 65, 85, 0.5);
      position: relative;
    }

    .slide-header::before {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: var(--accent-cyan);
    }

    .slide-part {
      font-size: 11px;
      font-weight: 700;
      color: var(--accent-cyan);
      text-transform: uppercase;
      letter-spacing: 0.8px;
      margin-bottom: 4px;
    }

    .slide-title {
      font-size: 22px;
      font-weight: 800;
      color: var(--text-white);
      line-height: 1.3;
      margin-bottom: 6px;
    }

    .slide-subtitle {
      font-size: 13px;
      color: var(--text-muted);
      font-style: italic;
    }

    .slide-content {
      padding: 20px 24px;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    /* Layout Containers */
    .two-column {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      flex: 1;
    }

    .three-column {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 16px;
      flex: 1;
    }

    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 16px 18px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .card-title {
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
      padding-bottom: 6px;
      border-bottom: 1px solid rgba(51, 65, 85, 0.4);
    }

    .card-bullets {
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-size: 12.5px;
      line-height: 1.45;
    }

    .bullet-header {
      font-weight: 700;
      color: #FFFFFF;
      margin-top: 6px;
    }

    .bullet-item {
      color: var(--text-body);
      padding-left: 10px;
      position: relative;
    }

    .bullet-item::before {
      content: "▪";
      position: absolute;
      left: 0;
      color: var(--accent-cyan);
      font-size: 10px;
      top: 1px;
    }

    /* Code Boxes */
    .code-container {
      background: var(--code-bg);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      flex: 1;
    }

    .code-header-bar {
      background: #0E1626;
      border-bottom: 1px solid var(--card-border);
      padding: 8px 14px;
      font-size: 11px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .code-content {
      padding: 14px;
      font-family: "JetBrains Mono", "Courier New", Consolas, monospace;
      font-size: 11px;
      line-height: 1.5;
      color: #CBD5E1;
      white-space: pre-wrap;
      overflow-x: auto;
      flex: 1;
    }

    /* Stats Grid */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 16px;
    }

    .stat-box {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 14px 10px;
      text-align: center;
    }

    .stat-val {
      font-size: 22px;
      font-weight: 800;
    }

    .stat-lbl {
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 4px;
    }

    /* Table Styles */
    .table-container {
      overflow-x: auto;
      border-radius: 8px;
      border: 1px solid var(--card-border);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }

    th {
      background: #1E293B;
      color: var(--accent-cyan);
      font-weight: 700;
      padding: 10px 12px;
      text-align: left;
      border-bottom: 1px solid var(--card-border);
    }

    td {
      padding: 9px 12px;
      border-bottom: 1px solid rgba(51, 65, 85, 0.4);
    }

    tr:nth-child(even) td {
      background: rgba(15, 23, 42, 0.6);
    }

    tr.highlight-row td {
      background: #064E3B;
      color: #34D399;
      font-weight: 700;
    }

    /* Speaker Notes Drawer */
    .notes-drawer {
      background: #090E17;
      border-top: 1px solid var(--card-border);
      padding: 16px 24px;
      display: none;
      animation: slideUp 0.2s ease-out;
    }

    .notes-drawer.open {
      display: block;
    }

    @keyframes slideUp {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .notes-header {
      font-size: 11px;
      font-weight: 800;
      color: var(--accent-amber);
      letter-spacing: 0.8px;
      margin-bottom: 6px;
    }

    .notes-text {
      font-size: 12px;
      line-height: 1.55;
      color: #CBD5E1;
      white-space: pre-wrap;
    }

    /* Bottom Control Dock */
    footer {
      background: #0F172A;
      border-top: 1px solid var(--card-border);
      padding: 10px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .footer-left {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .nav-btn {
      background: #1E293B;
      border: 1px solid var(--card-border);
      color: #FFFFFF;
      font-size: 14px;
      font-weight: 700;
      padding: 8px 18px;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .nav-btn:hover {
      background: #0284C7;
      border-color: #38BDF8;
    }

    .nav-btn:disabled {
      opacity: 0.35;
      cursor: not-allowed;
      background: #1E293B;
      border-color: var(--card-border);
    }

    /* Responsive adjustments */
    @media (max-width: 860px) {
      .two-column, .three-column {
        grid-template-columns: 1fr;
      }
      .stats-grid {
        grid-template-columns: 1fr 1fr;
      }
      .slide-select {
        max-width: 180px;
      }
    }
  </style>
</head>
<body>

  <!-- Top Header Control Bar -->
  <header>
    <div class="header-left">
      <div class="project-logo">PROJECT AEOLUS</div>
      <div class="slide-badge" id="slideBadge">Slide 1 of 82</div>
      <select class="slide-select" id="slideSelect" onchange="jumpToSlide(parseInt(this.value))">
        <!-- Options injected via JS -->
      </select>
    </div>
    <div class="header-actions">
      <button class="btn" onclick="toggleNotes()">📝 Notes (<span id="notesStatus">Show</span>)</button>
      <button class="btn" onclick="toggleFullscreen()">⛶ Fullscreen</button>
    </div>
  </header>

  <div class="progress-bar-container">
    <div class="progress-bar-fill" id="progressBar"></div>
  </div>

  <!-- Main Slide Presentation Area -->
  <main id="mainContainer">
    <div class="slide-wrapper" id="slideCard">
      <!-- Injected dynamically -->
    </div>
  </main>

  <!-- Bottom Navigation Dock -->
  <footer>
    <div class="footer-left">
      <button class="nav-btn" id="prevBtn" onclick="prevSlide()">◀ Previous</button>
      <button class="nav-btn" id="nextBtn" onclick="nextSlide()">Next ▶</button>
    </div>
    <div style="font-size: 12px; color: var(--text-muted);">
      Swipe or use ⬅ ➡ arrow keys
    </div>
  </footer>

  <script>
    const SLIDES_DATA = """ + slides_json + """;
    let currentIndex = 0;
    let notesOpen = false;

    // Initialize Dropdown
    function initSelect() {
      const select = document.getElementById("slideSelect");
      select.innerHTML = "";
      SLIDES_DATA.forEach((s, idx) => {
        const opt = document.createElement("option");
        opt.value = idx;
        opt.textContent = `${idx + 1}. ${s.title}`;
        select.appendChild(opt);
      });
    }

    function renderSlide(index) {
      if (index < 0) index = 0;
      if (index >= SLIDES_DATA.length) index = SLIDES_DATA.length - 1;
      currentIndex = index;

      const s = SLIDES_DATA[index];
      const card = document.getElementById("slideCard");
      const badge = document.getElementById("slideBadge");
      const select = document.getElementById("slideSelect");
      const progress = document.getElementById("progressBar");

      badge.textContent = `Slide ${index + 1} of ${SLIDES_DATA.length}`;
      select.value = index;
      progress.style.width = `${((index + 1) / SLIDES_DATA.length) * 100}%`;

      document.getElementById("prevBtn").disabled = (index === 0);
      document.getElementById("nextBtn").disabled = (index === SLIDES_DATA.length - 1);

      let contentHtml = "";

      if (s.type === "title") {
        let statsHtml = "";
        if (s.stats) {
          statsHtml = `<div class="stats-grid">` + s.stats.map(st => `
            <div class="stat-box" style="border-color: ${st.col};">
              <div class="stat-val" style="color: ${st.col};">${escapeHtml(st.val)}</div>
              <div class="stat-lbl">${escapeHtml(st.lbl)}</div>
            </div>
          `).join("") + `</div>`;
        }
        contentHtml = `
          ${statsHtml}
          <div class="card" style="border-color: var(--accent-cyan);">
            <div class="card-title" style="color: var(--accent-cyan);">EXECUTIVE TECHNICAL BRIEFING STATEMENT</div>
            <div style="font-size: 13px; line-height: 1.6; color: var(--text-body);">${escapeHtml(s.summary || "")}</div>
          </div>
        `;
      } else if (s.type === "three_cards") {
        contentHtml = `<div class="three-column">` + (s.cards || []).map(c => `
          <div class="card" style="border-color: ${c.col || 'var(--card-border)'};">
            <div class="card-title" style="color: ${c.col || 'var(--accent-cyan)'};">${escapeHtml(c.title)}</div>
            <div class="card-bullets">${formatBullets(c.bullets)}</div>
          </div>
        `).join("") + `</div>`;
      } else if (s.type === "split_cards") {
        contentHtml = `<div class="two-column">
          <div class="card" style="border-color: ${s.card1.col || 'var(--card-border)'};">
            <div class="card-title" style="color: ${s.card1.col || 'var(--accent-cyan)'};">${escapeHtml(s.card1.title)}</div>
            <div class="card-bullets">${formatBullets(s.card1.bullets)}</div>
          </div>
          <div class="card" style="border-color: ${s.card2.col || 'var(--card-border)'};">
            <div class="card-title" style="color: ${s.card2.col || 'var(--accent-cyan)'};">${escapeHtml(s.card2.title)}</div>
            <div class="card-bullets">${formatBullets(s.card2.bullets)}</div>
          </div>
        </div>`;
      } else if (s.type === "split_code") {
        contentHtml = `<div class="two-column">
          <div class="code-container" style="border-color: ${s.accent || 'var(--card-border)'};">
            <div class="code-header-bar" style="color: ${s.accent || 'var(--accent-cyan)'};">
              <span>${escapeHtml(s.codeHeader || "SOURCE CODE / FORMULATION")}</span>
              <button class="btn" style="padding: 2px 6px; font-size: 10px;" onclick="copyCode(this)">Copy</button>
            </div>
            <div class="code-content">${escapeHtml(s.codeText || "")}</div>
          </div>
          <div class="card" style="border-color: ${s.card.col || s.accent || 'var(--card-border)'};">
            <div class="card-title" style="color: ${s.card.col || s.accent || 'var(--accent-cyan)'};">${escapeHtml(s.card.title)}</div>
            <div class="card-bullets">${formatBullets(s.card.bullets)}</div>
          </div>
        </div>`;
      } else if (s.type === "full_code") {
        contentHtml = `
          <div class="code-container" style="border-color: ${s.accent || 'var(--card-border)'}; margin-bottom: 14px;">
            <div class="code-header-bar" style="color: ${s.accent || 'var(--accent-cyan)'};">
              <span>${escapeHtml(s.codeHeader || "SOURCE CODE")}</span>
              <button class="btn" style="padding: 2px 6px; font-size: 10px;" onclick="copyCode(this)">Copy</button>
            </div>
            <div class="code-content" style="max-height: 280px;">${escapeHtml(s.codeText || "")}</div>
          </div>
          <div class="card" style="border-color: ${s.bottomCard.col || s.accent || 'var(--card-border)'};">
            <div class="card-title" style="color: ${s.bottomCard.col || s.accent || 'var(--accent-cyan)'};">${escapeHtml(s.bottomCard.title)}</div>
            <div class="card-bullets">${formatBullets(s.bottomCard.bullets)}</div>
          </div>
        `;
      } else if (s.type === "table") {
        let thead = "<tr>" + (s.headers || []).map(h => `<th>${escapeHtml(h)}</th>`).join("") + "</tr>";
        let tbody = (s.rows || []).map((r, rIdx) => {
          const isHighlight = (rIdx === s.rows.length - 1);
          return `<tr class="${isHighlight ? 'highlight-row' : ''}">` + r.map(cell => `<td>${escapeHtml(cell)}</td>`).join("") + `</tr>`;
        }).join("");
        contentHtml = `
          <div class="table-container">
            <table>
              <thead>${thead}</thead>
              <tbody>${tbody}</tbody>
            </table>
          </div>
        `;
      }

      card.innerHTML = `
        <div class="slide-header">
          <div class="slide-part">${escapeHtml(s.part || "")}</div>
          <div class="slide-title">${escapeHtml(s.title || "")}</div>
          ${s.subtitle ? `<div class="slide-subtitle">${escapeHtml(s.subtitle)}</div>` : ""}
        </div>
        <div class="slide-content">
          ${contentHtml}
        </div>
        <div class="notes-drawer ${notesOpen ? 'open' : ''}" id="notesDrawer">
          <div class="notes-header">PROFESSOR'S LECTURE NOTES & DEFENSE DEFICIENCIES:</div>
          <div class="notes-text">${escapeHtml(s.notes || "No additional notes for this slide.")}</div>
        </div>
      `;
    }

    function formatBullets(bullets) {
      if (!bullets || !Array.isArray(bullets)) return "";
      let html = "";
      bullets.forEach(b => {
        const raw = b.trim();
        if (!raw) return;
        if (raw.startsWith("•")) {
          html += `<div class="bullet-header">${escapeHtml(raw.replace(/^•\\s*/, ""))}</div>`;
        } else if (raw.startsWith("-")) {
          html += `<div class="bullet-item">${escapeHtml(raw.replace(/^-\\s*/, ""))}</div>`;
        } else {
          html += `<div class="bullet-item">${escapeHtml(raw)}</div>`;
        }
      });
      return html;
    }

    function escapeHtml(text) {
      return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    function nextSlide() {
      if (currentIndex < SLIDES_DATA.length - 1) {
        renderSlide(currentIndex + 1);
      }
    }

    function prevSlide() {
      if (currentIndex > 0) {
        renderSlide(currentIndex - 1);
      }
    }

    function jumpToSlide(idx) {
      renderSlide(idx);
    }

    function toggleNotes() {
      notesOpen = !notesOpen;
      const drawer = document.getElementById("notesDrawer");
      const status = document.getElementById("notesStatus");
      if (drawer) {
        drawer.classList.toggle("open", notesOpen);
      }
      if (status) {
        status.textContent = notesOpen ? "Hide" : "Show";
      }
    }

    function toggleFullscreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => alert("Fullscreen not supported"));
      } else {
        document.exitFullscreen();
      }
    }

    function copyCode(btn) {
      const code = btn.closest(".code-container").querySelector(".code-content").textContent;
      navigator.clipboard.writeText(code).then(() => {
        const orig = btn.textContent;
        btn.textContent = "Copied!";
        setTimeout(() => btn.textContent = orig, 1500);
      });
    }

    // Keyboard Shortcuts
    window.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight" || e.key === " " || e.key === "PageDown") {
        nextSlide();
      } else if (e.key === "ArrowLeft" || e.key === "PageUp") {
        prevSlide();
      } else if (e.key === "n" || e.key === "N") {
        toggleNotes();
      } else if (e.key === "f" || e.key === "F") {
        toggleFullscreen();
      }
    });

    // Touch Swipe Detection for Android Tablet
    let touchStartX = 0;
    let touchStartY = 0;
    const container = document.getElementById("mainContainer");

    container.addEventListener("touchstart", (e) => {
      touchStartX = e.changedTouches[0].screenX;
      touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });

    container.addEventListener("touchend", (e) => {
      const diffX = e.changedTouches[0].screenX - touchStartX;
      const diffY = e.changedTouches[0].screenY - touchStartY;
      if (Math.abs(diffX) > 60 && Math.abs(diffY) < 100) {
        if (diffX < 0) {
          nextSlide();
        } else {
          prevSlide();
        }
      }
    }, { passive: true });

    // Initial boot
    initSelect();
    renderSlide(0);
  </script>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"Generated standalone interactive HTML presentation at: {output_path} ({os.path.getsize(output_path)/1024:.1f} KB)")

    # Copy to tablet Downloads folder
    download_dir = "/storage/emulated/0/Download"
    if os.path.isdir(download_dir):
        dest = os.path.join(download_dir, os.path.basename(output_path))
        shutil.copy2(output_path, dest)
        print(f"Copied HTML presentation directly to tablet storage: {dest}")

if __name__ == "__main__":
    out = os.path.join(BASE_DIR, "aeolus_presentation.html")
    generate_interactive_html(out)

#!/usr/bin/env python3
"""Compiles all 82 slides of Project AEOLUS and generates:
1. Google Apps Script file (build_aeolus_deck.js) for Google Slides
2. Native PowerPoint file (Project_AEOLUS_Master_Technical_Briefing.pptx)
3. Standalone touch-optimized tablet viewer (aeolus_presentation.html)
4. One-click copy and deployment hub (copy_deck.html)

All artifacts are copied directly to /storage/emulated/0/Download for seamless access on Android tablets.
"""

import os
import sys
import json
import subprocess
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
from deck_builder.export_pptx import export_to_pptx
from deck_builder.export_html import generate_interactive_html

def compile_deck():
    slides = []
    
    p0 = get_part0_slides()
    p1 = get_part1_slides()
    p2 = get_part2_slides()
    p3 = get_part3_slides()
    p4 = get_part4_slides()
    p5 = get_part5_slides()
    p6 = get_part6_slides()

    slides.extend(p0)
    slides.extend(p1)
    slides.extend(p2)
    slides.extend(p3)
    slides.extend(p4)
    slides.extend(p5)
    slides.extend(p6)

    print(f"Total slides compiled: {len(slides)}")
    print(f"  Part 0 (Intro & Agenda):      {len(p0)} slides")
    print(f"  Part 1 (Governing Equations): {len(p1)} slides")
    print(f"  Part 2 (Micro-Physics):       {len(p2)} slides")
    print(f"  Part 3 (Kinematics):          {len(p3)} slides")
    print(f"  Part 4 (CFD Verification):    {len(p4)} slides")
    print(f"  Part 5 (Code Ledger):         {len(p5)} slides")
    print(f"  Part 6 (Tabletop Prototype):  {len(p6)} slides")

    assert len(slides) >= 80, f"Error: Slide count {len(slides)} is below required 80 slides!"
    return slides

def generate_javascript(slides):
    slides_json = json.dumps(slides, indent=2, ensure_ascii=False)

    js_code = """/**
 * Project AEOLUS: Master Technical Briefing Compendium (82 Slides)
 * Automated Google Apps Script for Google Slides (SlidesApp)
 *
 * FULL 6-PART SCIENTIFIC & ENGINEERING COMPENDIUM:
 *   - Part 0: Master Title, Syllabus, and Executive Disruption Milestones (Slides 1 - 3)
 *   - Part 1: Governing Fluid Equations & Cylindrical Coordinates (Slides 4 - 17)
 *   - Part 2: Micro-Physics Realism & Non-Hydrostatic Thermodynamics (Slides 18 - 30)
 *   - Part 3: Asymmetric Disruption Kinematics & Dual-Mode Interventions (Slides 31 - 44)
 *   - Part 4: High-Fidelity Computational Verification (96³ Grid) (Slides 45 - 57)
 *   - Part 5: Complete Verbatim Code Ledger & Mathematical Algorithms (Slides 58 - 69)
 *   - Part 6: Laboratory Tabletop Prototype & Froude Scaling (Slides 70 - 82)
 *
 * HOW TO EXECUTE IN GOOGLE APPS SCRIPT:
 * 1. Open https://script.google.com and create a new project.
 * 2. Paste this entire file into Code.gs (replacing any existing text).
 * 3. Choose your execution mode:
 *    - To build the entire 82-slide deck: Select 'buildAeolusDeck' and click 'Run'.
 *    - To build or append modularly: Set PRESENTATION_ID below, select 'buildAeolusDeckPart', and pass part 0-6.
 * 4. Grant required Google Slides permissions on first execution.
 * 5. Check the Execution Log for the direct edit URL of the generated master deck.
 */

// OPTIONAL: Paste an existing presentation ID to append, or leave empty to create a new deck.
var PRESENTATION_ID = "";

// MASTER DATA REPOSITORY (82 SLIDES)
var AEOLUS_SLIDES = """ + slides_json + """;

// Master Design Palette (Deep Slate & High-Contrast Accents)
var PALETTE = {
  BG_DARK: "#0B1120",      // Deep Obsidian Slate
  CARD_BG: "#162032",      // Elevated Card Background
  CARD_BORDER: "#334155",  // Slate Border
  CODE_BG: "#070B14",      // Monospace Box Background
  ACCENT_CYAN: "#38BDF8",  // Primary Flow / Kinematics
  ACCENT_GREEN: "#34D399", // Divergence / Success Metrics
  ACCENT_AMBER: "#F59E0B", // Thermal / Warning Accents
  ACCENT_CORAL: "#F87171", // Negative Drag / Vorticity
  TEXT_WHITE: "#FFFFFF",
  TEXT_BODY: "#E2E8F0",
  TEXT_MUTED: "#94A3B8"
};

function getOrCreateDeck(deckTitle) {
  if (PRESENTATION_ID && PRESENTATION_ID.trim() !== "") {
    Logger.log("Opening existing presentation: " + PRESENTATION_ID);
    return SlidesApp.openById(PRESENTATION_ID.trim());
  } else {
    Logger.log("Creating new presentation: " + deckTitle);
    var deck = SlidesApp.create(deckTitle);
    var existing = deck.getSlides();
    if (existing.length > 0) {
      existing[0].remove();
    }
    return deck;
  }
}

function createBaseSlide(deck) {
  var slide = deck.appendSlide(SlidesApp.PredefinedLayout.BLANK);
  slide.getBackground().setSolidFill(PALETTE.BG_DARK);
  return slide;
}

function applyHeader(slide, pageWidth, slideNum, totalSlides, partLabel, titleText, subtitleText) {
  var topRule = slide.insertShape(SlidesApp.ShapeType.RECTANGLE, 0, 0, pageWidth, 4);
  topRule.getFill().setSolidFill(PALETTE.ACCENT_CYAN);
  topRule.getBorder().setTransparent();

  var tagText = "SLIDE " + slideNum + " OF " + totalSlides + "  •  " + partLabel.toUpperCase();
  var pBox = slide.insertTextBox(tagText, 35, 12, 650, 16);
  var pt = pBox.getText();
  pt.getTextStyle().setFontFamily("Arial").setFontSize(9.5).setBold(true).setForegroundColor(PALETTE.ACCENT_CYAN);

  var tBox = slide.insertTextBox(titleText, 35, 28, 650, 28);
  var tt = tBox.getText();
  tt.getTextStyle().setFontFamily("Arial").setFontSize(17.5).setBold(true).setForegroundColor(PALETTE.TEXT_WHITE);

  if (subtitleText) {
    var sBox = slide.insertTextBox(subtitleText, 35, 56, 650, 16);
    var st = sBox.getText();
    st.getTextStyle().setFontFamily("Arial").setFontSize(9.5).setItalic(true).setForegroundColor(PALETTE.TEXT_MUTED);
  }
}

function insertCard(slide, x, y, w, h, bgHex, borderHex) {
  var card = slide.insertShape(SlidesApp.ShapeType.ROUNDED_RECTANGLE, x, y, w, h);
  card.getFill().setSolidFill(bgHex || PALETTE.CARD_BG);
  if (borderHex) {
    card.getBorder().getLineFill().setSolidFill(borderHex);
    card.getBorder().setWeight(1);
  } else {
    card.getBorder().getLineFill().setSolidFill(PALETTE.CARD_BORDER);
    card.getBorder().setWeight(1);
  }
  return card;
}

function insertCardWithBullets(slide, x, y, w, h, cardData) {
  insertCard(slide, x, y, w, h, PALETTE.CARD_BG, cardData.col || PALETTE.CARD_BORDER);
  var tb = slide.insertTextBox("", x + 10, y + 8, w - 20, h - 16);
  var t = tb.getText();
  t.setText(cardData.title + "\\n");
  t.getRange(0, cardData.title.length).getTextStyle()
    .setFontFamily("Arial")
    .setFontSize(12)
    .setBold(true)
    .setForegroundColor(cardData.col || PALETTE.ACCENT_CYAN);

  var curPos = cardData.title.length + 1;
  var bullets = cardData.bullets || [];
  for (var i = 0; i < bullets.length; i++) {
    var raw = bullets[i].trim();
    if (!raw) continue;
    var isHeader = (raw.indexOf("•") === 0);
    var isSub = (raw.indexOf("-") === 0);
    var cleanText = raw.replace(/^[•\\-]\\s*/, "");
    var prefix = isSub ? "    ▪  " : "•  ";
    var line = prefix + cleanText + "\\n";
    t.appendText(line);
    var r = t.getRange(curPos, curPos + line.length);
    r.getTextStyle()
      .setFontFamily("Arial")
      .setFontSize(isHeader ? 10.5 : (isSub ? 9.5 : 10.0))
      .setBold(isHeader)
      .setForegroundColor(isHeader ? PALETTE.TEXT_WHITE : PALETTE.TEXT_BODY);
    curPos += line.length;
  }
  return tb;
}

function insertCodeBox(slide, x, y, w, h, headerTitle, codeString, accentColor) {
  var box = insertCard(slide, x, y, w, h, PALETTE.CODE_BG, accentColor || PALETTE.ACCENT_CYAN);
  var tb = slide.insertTextBox("", x + 8, y + 6, w - 16, h - 12);
  var t = tb.getText();
  var fullContent = (headerTitle ? headerTitle + "\\n" : "") + codeString;
  t.setText(fullContent);

  if (headerTitle) {
    t.getRange(0, headerTitle.length).getTextStyle()
      .setFontFamily("Arial")
      .setFontSize(10)
      .setBold(true)
      .setForegroundColor(accentColor || PALETTE.ACCENT_CYAN);

    t.getRange(headerTitle.length + 1, t.getLength()).getTextStyle()
      .setFontFamily("Courier New")
      .setFontSize(8.2)
      .setForegroundColor(PALETTE.TEXT_BODY);
  } else {
    t.getTextStyle()
      .setFontFamily("Courier New")
      .setFontSize(8.2)
      .setForegroundColor(PALETTE.TEXT_BODY);
  }
  return box;
}

function setSpeakerNotes(slide, notesContent) {
  if (notesContent) {
    var notesPage = slide.getNotesPage();
    var speakerNotesShape = notesPage.getSpeakerNotesShape();
    speakerNotesShape.getText().setText(notesContent);
  }
}

function renderTitleSlide(slide, s, pageWidth, slideNum, total) {
  var bar = slide.insertShape(SlidesApp.ShapeType.RECTANGLE, 0, 0, pageWidth, 5);
  bar.getFill().setSolidFill(PALETTE.ACCENT_CYAN);
  bar.getBorder().setTransparent();

  var badge = slide.insertShape(SlidesApp.ShapeType.ROUNDED_RECTANGLE, 35, 20, 320, 22);
  badge.getFill().setSolidFill(PALETTE.CARD_BG);
  badge.getBorder().getLineFill().setSolidFill(PALETTE.ACCENT_CYAN);
  var bt = badge.getText();
  bt.setText("COMPUTATIONAL FLUID DYNAMICS & HARDWARE DEFENSE");
  bt.getTextStyle().setFontFamily("Arial").setFontSize(7.5).setBold(true).setForegroundColor(PALETTE.ACCENT_CYAN);
  bt.getParagraphStyle().setAlignment(SlidesApp.ParagraphAlignment.CENTER);

  var titleBox = slide.insertTextBox(s.title, 35, 46, 650, 42);
  titleBox.getText().getTextStyle().setFontFamily("Arial").setFontSize(28).setBold(true).setForegroundColor(PALETTE.TEXT_WHITE);

  var subBox = slide.insertTextBox(s.subtitle, 35, 90, 650, 24);
  subBox.getText().getTextStyle().setFontFamily("Arial").setFontSize(10.5).setItalic(true).setForegroundColor(PALETTE.TEXT_MUTED);

  var cardW = 152;
  var gap = 14;
  for (var i = 0; i < s.stats.length; i++) {
    var stat = s.stats[i];
    var cx = 35 + i * (cardW + gap);
    insertCard(slide, cx, 120, cardW, 80, PALETTE.CARD_BG, stat.col || PALETTE.CARD_BORDER);

    var tb = slide.insertTextBox("", cx + 6, 126, cardW - 12, 68);
    var t = tb.getText();
    t.setText(stat.val + "\\n" + stat.lbl);
    t.getRange(0, stat.val.length).getTextStyle().setFontFamily("Arial").setFontSize(19).setBold(true).setForegroundColor(stat.col);
    t.getRange(stat.val.length + 1, t.getLength()).getTextStyle().setFontFamily("Arial").setFontSize(8.2).setForegroundColor(PALETTE.TEXT_MUTED);
  }

  insertCard(slide, 35, 212, 650, 168, PALETTE.CARD_BG, PALETTE.ACCENT_CYAN);
  var descBox = slide.insertTextBox("", 46, 220, 628, 152);
  var dt = descBox.getText();
  dt.setText("EXECUTIVE TECHNICAL BRIEFING STATEMENT:\\n" + s.summary);
  dt.getRange(0, 42).getTextStyle().setFontFamily("Arial").setFontSize(10.5).setBold(true).setForegroundColor(PALETTE.ACCENT_CYAN);
  dt.getRange(43, dt.getLength()).getTextStyle().setFontFamily("Arial").setFontSize(9.5).setForegroundColor(PALETTE.TEXT_BODY);

  setSpeakerNotes(slide, s.notes);
}

function renderSplitCards(slide, s, pageWidth, slideNum, total) {
  applyHeader(slide, pageWidth, slideNum, total, s.part, s.title, s.subtitle);
  insertCardWithBullets(slide, 35, 78, 315, 305, s.card1);
  insertCardWithBullets(slide, 370, 78, 315, 305, s.card2);
  setSpeakerNotes(slide, s.notes);
}

function renderSplitCode(slide, s, pageWidth, slideNum, total) {
  applyHeader(slide, pageWidth, slideNum, total, s.part, s.title, s.subtitle);
  insertCodeBox(slide, 35, 78, 325, 305, s.codeHeader, s.codeText, s.accent || PALETTE.ACCENT_CYAN);
  insertCardWithBullets(slide, 375, 78, 310, 305, s.card);
  setSpeakerNotes(slide, s.notes);
}

function renderThreeCards(slide, s, pageWidth, slideNum, total) {
  applyHeader(slide, pageWidth, slideNum, total, s.part, s.title, s.subtitle);
  var cardW = 206;
  var gap = 16;
  for (var i = 0; i < s.cards.length; i++) {
    var cx = 35 + i * (cardW + gap);
    insertCardWithBullets(slide, cx, 78, cardW, 305, s.cards[i]);
  }
  setSpeakerNotes(slide, s.notes);
}

function renderFullCode(slide, s, pageWidth, slideNum, total) {
  applyHeader(slide, pageWidth, slideNum, total, s.part, s.title, s.subtitle);
  insertCodeBox(slide, 35, 78, 650, 205, s.codeHeader, s.codeText, s.accent || PALETTE.ACCENT_CYAN);
  insertCardWithBullets(slide, 35, 292, 650, 92, s.bottomCard);
  setSpeakerNotes(slide, s.notes);
}

function renderTableSlide(slide, s, pageWidth, slideNum, total) {
  applyHeader(slide, pageWidth, slideNum, total, s.part, s.title, s.subtitle);
  var table = slide.insertTable(s.rows.length + 1, s.headers.length, 35, 80, 650, 300);

  for (var c = 0; c < s.headers.length; c++) {
    var hCell = table.getCell(0, c);
    hCell.getText().setText(s.headers[c]);
    hCell.getText().getTextStyle().setFontFamily("Arial").setFontSize(9).setBold(true).setForegroundColor(PALETTE.ACCENT_CYAN);
    hCell.getFill().setSolidFill(PALETTE.CARD_BG);
    if (s.colWidths && s.colWidths.length === s.headers.length) {
      table.getColumn(c).setWidth(s.colWidths[c]);
    }
  }

  for (var r = 0; r < s.rows.length; r++) {
    var isHighlight = (r === s.rows.length - 1);
    for (var col = 0; col < s.headers.length; col++) {
      var cell = table.getCell(r + 1, col);
      cell.getText().setText(s.rows[r][col]);
      var fg = isHighlight ? PALETTE.ACCENT_GREEN : PALETTE.TEXT_BODY;
      cell.getText().getTextStyle().setFontFamily("Arial").setFontSize(8.5).setBold(isHighlight).setForegroundColor(fg);
      cell.getFill().setSolidFill(isHighlight ? "#064E3B" : (r % 2 === 0 ? "#0F172A" : "#162032"));
    }
  }
  setSpeakerNotes(slide, s.notes);
}

function buildAeolusDeck() {
  Logger.log("Beginning full Project AEOLUS Master Deck Generation (82 Slides)...");
  var deckTitle = "Project AEOLUS: Master Technical Briefing (82 Slides)";
  var deck = getOrCreateDeck(deckTitle);
  var pageWidth = deck.getPageWidth();
  var total = AEOLUS_SLIDES.length;

  for (var i = 0; i < total; i++) {
    var s = AEOLUS_SLIDES[i];
    var slide = createBaseSlide(deck);
    var num = i + 1;

    if (s.type === "title") {
      renderTitleSlide(slide, s, pageWidth, num, total);
    } else if (s.type === "split_cards") {
      renderSplitCards(slide, s, pageWidth, num, total);
    } else if (s.type === "split_code") {
      renderSplitCode(slide, s, pageWidth, num, total);
    } else if (s.type === "three_cards") {
      renderThreeCards(slide, s, pageWidth, num, total);
    } else if (s.type === "full_code") {
      renderFullCode(slide, s, pageWidth, num, total);
    } else if (s.type === "table") {
      renderTableSlide(slide, s, pageWidth, num, total);
    }

    if (num % 10 === 0 || num === total) {
      Logger.log("Progress: Rendered Slide " + num + " / " + total + ": " + s.title);
    }
  }

  Logger.log("==================================================================");
  Logger.log("SUCCESS: Project AEOLUS Presentation Successfully Generated!");
  Logger.log("Total Slides Created: " + total);
  Logger.log("Presentation URL: " + deck.getUrl());
  Logger.log("Presentation ID: " + deck.getId());
  Logger.log("==================================================================");

  return deck.getUrl();
}
"""
    return js_code

def update_copy_html(js_code):
    html_path = os.path.join(BASE_DIR, "copy_deck.html")
    escaped_js = js_code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Project AEOLUS: Master Technical Presentation Hub</title>
  <style>
    :root {{
      --bg: #0B1120;
      --card: #162032;
      --border: #334155;
      --cyan: #38BDF8;
      --green: #34D399;
      --amber: #F59E0B;
      --text: #E2E8F0;
      --muted: #94A3B8;
    }}
    body {{
      background-color: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      padding: 24px;
      margin: 0;
      line-height: 1.5;
    }}
    .container {{
      max-width: 960px;
      margin: 0 auto;
    }}
    h1 {{
      color: var(--cyan);
      margin-bottom: 6px;
    }}
    .subtitle {{
      color: var(--muted);
      margin-bottom: 20px;
      font-size: 15px;
    }}
    .options-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-bottom: 24px;
    }}
    .option-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .option-badge {{
      font-size: 11px;
      font-weight: 800;
      color: var(--cyan);
      letter-spacing: 0.8px;
      text-transform: uppercase;
      margin-bottom: 6px;
    }}
    .option-title {{
      font-size: 17px;
      font-weight: 700;
      color: #FFFFFF;
      margin-bottom: 8px;
    }}
    .option-desc {{
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 14px;
      line-height: 1.4;
    }}
    .btn {{
      background: #0284C7;
      color: #FFFFFF;
      font-size: 14px;
      font-weight: 700;
      padding: 10px 16px;
      border: 1px solid var(--cyan);
      border-radius: 6px;
      cursor: pointer;
      text-align: center;
      text-decoration: none;
      transition: all 0.15s ease;
    }}
    .btn:hover {{
      background: #0369A1;
    }}
    .btn-green {{
      background: #059669;
      border-color: var(--green);
    }}
    .btn-green:hover {{
      background: #047857;
    }}
    .code-container {{
      background: #070B14;
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow: hidden;
      margin-top: 20px;
    }}
    .code-header {{
      background: #0F172A;
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 13px;
      font-weight: 700;
      color: var(--cyan);
    }}
    .code-box {{
      padding: 16px;
      max-height: 380px;
      overflow-y: auto;
      font-family: "JetBrains Mono", Consolas, "Courier New", monospace;
      font-size: 11px;
      color: #94A3B8;
      white-space: pre-wrap;
    }}
    @media (max-width: 800px) {{
      .options-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Project AEOLUS: Master Technical Briefing</h1>
    <div class="subtitle">82-Slide Master Defense Deck across 6 Exhaustive Navier-Stokes & Tabletop Modules</div>

    <div class="options-grid">
      <!-- Option 1: PPTX to Google Drive -->
      <div class="option-card" style="border-color: var(--green);">
        <div>
          <div class="option-badge" style="color: var(--green);">Recommended for Tablet</div>
          <div class="option-title">1. PowerPoint (.pptx)</div>
          <div class="option-desc">
            Directly openable in Google Slides! Saved in your tablet's Downloads as <code>Project_AEOLUS_Master_Technical_Briefing.pptx</code>. Upload to Google Drive to edit or present in native Google Slides.
          </div>
        </div>
        <div style="font-size: 12px; color: var(--green); font-weight: bold;">✓ Ready in Downloads folder</div>
      </div>

      <!-- Option 2: Standalone Interactive HTML -->
      <div class="option-card" style="border-color: var(--cyan);">
        <div>
          <div class="option-badge">Instant Offline View</div>
          <div class="option-title">2. Tablet HTML Viewer</div>
          <div class="option-desc">
            Touch-optimized presentation with swipe navigation, slide jump dropdown, and embedded professor lecture notes. Opens right in your browser offline.
          </div>
        </div>
        <a href="aeolus_presentation.html" class="btn">Open Interactive Deck</a>
      </div>

      <!-- Option 3: Google Apps Script -->
      <div class="option-card" style="border-color: var(--amber);">
        <div>
          <div class="option-badge" style="color: var(--amber);">Cloud Automation</div>
          <div class="option-title">3. Google Apps Script</div>
          <div class="option-desc">
            Automate slide generation via Google Cloud. Copy the script below, paste into <a href="https://script.google.com" target="_blank" style="color: var(--cyan);">script.google.com</a>, and run <code>buildAeolusDeck()</code>.
          </div>
        </div>
        <button class="btn" style="background: #D97706; border-color: var(--amber);" onclick="copyToClipboard()">📋 Copy Apps Script</button>
      </div>
    </div>

    <div id="copyAlert" style="display: none; background: #064E3B; border: 1px solid var(--green); color: #FFFFFF; padding: 12px; border-radius: 8px; margin-bottom: 16px; font-weight: bold; text-align: center;">
      ✓ Copied 82-slide Google Apps Script to clipboard! Paste into script.google.com.
    </div>

    <div class="code-container">
      <div class="code-header">
        <span>build_aeolus_deck.js (Google Apps Script)</span>
        <button class="btn" style="padding: 4px 10px; font-size: 11px;" onclick="copyToClipboard()">Copy Code</button>
      </div>
      <div class="code-box" id="codeContent">{escaped_js}</div>
    </div>
  </div>

  <script>
    function copyToClipboard() {{
      const code = document.getElementById("codeContent").textContent;
      navigator.clipboard.writeText(code).then(() => {{
        const alertBox = document.getElementById("copyAlert");
        alertBox.style.display = "block";
        setTimeout(() => {{ alertBox.style.display = "none"; }}, 3500);
      }});
    }}
  </script>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Updated {html_path} ({os.path.getsize(html_path)/1024:.1f} KB)")

    download_dir = "/storage/emulated/0/Download"
    if os.path.isdir(download_dir):
        dest = os.path.join(download_dir, "copy_deck.html")
        shutil.copy2(html_path, dest)
        print(f"Copied copy_deck.html to {dest}")

def main():
    print("Beginning master compilation of Project AEOLUS 82-slide deck...")
    slides = compile_deck()
    js_code = generate_javascript(slides)

    output_path = os.path.join(BASE_DIR, "build_aeolus_deck.js")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(js_code)
    print(f"Wrote {len(js_code)} bytes to {output_path}")

    # Validate JS syntax with node -c
    print("Validating JavaScript syntax with node -c...")
    res = subprocess.run(["node", "-c", output_path], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error in JS syntax: {res.stderr}")
        sys.exit(1)
    print("JavaScript syntax validated successfully!")

    # Copy JS to Android Download directory
    download_dir = "/storage/emulated/0/Download"
    if os.path.isdir(download_dir):
        dest = os.path.join(download_dir, "build_aeolus_deck.js")
        shutil.copy2(output_path, dest)
        print(f"Copied build_aeolus_deck.js to {dest}")

    # Update copy_deck.html
    update_copy_html(js_code)

    # Generate PPTX
    pptx_path = os.path.join(BASE_DIR, "Project_AEOLUS_Master_Technical_Briefing.pptx")
    export_to_pptx(pptx_path)

    # Generate Interactive HTML
    html_path = os.path.join(BASE_DIR, "aeolus_presentation.html")
    generate_interactive_html(html_path)

    print("\n==================================================================")
    print("ALL PROJECT AEOLUS PRESENTATION ARTIFACTS GENERATED SUCCESSFULLY!")
    print(f"1. PowerPoint (.pptx):     {pptx_path}")
    print(f"2. Google Apps Script:     {output_path}")
    print(f"3. Interactive HTML:       {html_path}")
    print(f"4. Quick Copy Portal:      {os.path.join(BASE_DIR, 'copy_deck.html')}")
    print(f"All files mirrored to:     {download_dir}")
    print("==================================================================")

if __name__ == "__main__":
    main()

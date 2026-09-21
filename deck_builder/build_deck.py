#!/usr/bin/env python3
"""Compiles all 82 slides and emits the complete Google Apps Script file build_aeolus_deck.js."""

import os
import json
import subprocess
import shutil

from deck_builder.part0_intro import get_part0_slides
from deck_builder.part1_governing import get_part1_slides
from deck_builder.part2_microphysics import get_part2_slides
from deck_builder.part3_kinematics import get_part3_slides
from deck_builder.part4_cfd_verification import get_part4_slides
from deck_builder.part5_code_ledger import get_part5_slides
from deck_builder.part6_hardware_prototype import get_part6_slides

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

    assert len(slides) >= 80, f"Error: Slide count {len(slides)} is below the required 80 slides!"

    return slides

def generate_javascript(slides):
    slides_json = json.dumps(slides, indent=2)

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
 * DESIGN & LAYOUT SPECIFICATIONS:
 *   - Clean Dark Palette: Background #0F172A (Deep Slate), Cards #1E293B, Border #334155.
 *   - Typography: Bold White (#FFFFFF) Titles, High-Contrast Off-White (#E2E8F0) Bullets, Cyan (#38BDF8) Accents.
 *   - Rectangular Monospace Code Boxes: Background #090E17, Font Courier New (7.5pt).
 *   - Professor Lecture Notes: Exhaustive, graduate-level narrative explanations on every single slide.
 *
 * HOW TO EXECUTE:
 * 1. Open https://script.google.com and create a new project.
 * 2. Paste this entire file into Code.gs (replacing any existing text).
 * 3. Select 'buildAeolusDeck' in the function dropdown and click 'Run'.
 * 4. Grant required Google Slides permissions on first execution.
 * 5. Check the Execution Log for the direct edit URL of the generated master deck.
 */

// MASTER DATA REPOSITORY (82 SLIDES)
var AEOLUS_SLIDES = """ + slides_json + """;

function buildAeolusDeck() {
  Logger.log("Initializing Project AEOLUS Master Presentation Deck Generation (82 Slides)...");

  // 1. Initialize Presentation
  var deckTitle = "Project AEOLUS: Master Technical Briefing";
  var deck = SlidesApp.create(deckTitle);
  var pageWidth = deck.getPageWidth();   // 720 pt
  var pageHeight = deck.getPageHeight(); // 405 pt

  // Clean initial default blank slide
  var existingSlides = deck.getSlides();
  if (existingSlides.length > 0) {
    existingSlides[0].remove();
  }

  // Master Design Palette
  var PALETTE = {
    BG_DARK: "#0F172A",
    CODE_BG: "#090E17",
    CARD_BG: "#1E293B",
    CARD_BORDER: "#334155",
    ACCENT_CYAN: "#38BDF8",
    ACCENT_GREEN: "#34D399",
    ACCENT_AMBER: "#F59E0B",
    ACCENT_CORAL: "#F87171",
    TEXT_WHITE: "#FFFFFF",
    TEXT_BODY: "#E2E8F0",
    TEXT_MUTED: "#94A3B8"
  };

  // Helper: Create Base Dark Slide
  function createBaseSlide() {
    var slide = deck.appendSlide(SlidesApp.PredefinedLayout.BLANK);
    slide.getBackground().setSolidFill(PALETTE.BG_DARK);
    return slide;
  }

  // Helper: Apply Slide Header Banner
  function applyHeader(slide, partLabel, titleText, subtitleText) {
    var topRule = slide.insertShape(SlidesApp.ShapeType.RECTANGLE, 0, 0, pageWidth, 4);
    topRule.getFill().setSolidFill(PALETTE.ACCENT_CYAN);
    topRule.getBorder().setTransparent();

    var pBox = slide.insertTextBox(partLabel.toUpperCase(), 35, 12, 650, 15);
    var pt = pBox.getText();
    pt.getTextStyle().setFontFamily("Arial").setFontSize(9).setBold(true).setForegroundColor(PALETTE.ACCENT_CYAN);

    var tBox = slide.insertTextBox(titleText, 35, 26, 650, 30);
    var tt = tBox.getText();
    tt.getTextStyle().setFontFamily("Arial").setFontSize(16.5).setBold(true).setForegroundColor(PALETTE.TEXT_WHITE);

    if (subtitleText) {
      var sBox = slide.insertTextBox(subtitleText, 35, 56, 650, 16);
      var st = sBox.getText();
      st.getTextStyle().setFontFamily("Arial").setFontSize(8.5).setForegroundColor(PALETTE.TEXT_MUTED);
    }
  }

  // Helper: Insert Card Container Shape
  function insertCard(slide, x, y, w, h, bgHex, borderHex) {
    var card = slide.insertShape(SlidesApp.ShapeType.ROUNDED_RECTANGLE, x, y, w, h);
    card.getFill().setSolidFill(bgHex || PALETTE.CARD_BG);
    if (borderHex) {
      card.getBorder().getLineFill().setSolidFill(borderHex);
      card.getBorder().setWeight(1);
    } else {
      card.getBorder().setTransparent();
    }
    return card;
  }

  // Helper: Insert Monospace Code / Equation Box
  function insertCodeBox(slide, x, y, w, h, headerTitle, codeString, accentColor) {
    var box = slide.insertShape(SlidesApp.ShapeType.ROUNDED_RECTANGLE, x, y, w, h);
    box.getFill().setSolidFill(PALETTE.CODE_BG);
    box.getBorder().getLineFill().setSolidFill(accentColor || PALETTE.CARD_BORDER);
    box.getBorder().setWeight(1);

    var tb = slide.insertTextBox("", x + 8, y + 6, w - 16, h - 12);
    var t = tb.getText();
    var fullContent = (headerTitle ? headerTitle + "\\n" : "") + codeString;
    t.setText(fullContent);

    if (headerTitle) {
      t.getRange(0, headerTitle.length).getTextStyle()
        .setFontFamily("Arial")
        .setFontSize(9)
        .setBold(true)
        .setForegroundColor(accentColor || PALETTE.ACCENT_CYAN);

      t.getRange(headerTitle.length + 1, t.getLength()).getTextStyle()
        .setFontFamily("Courier New")
        .setFontSize(7.5)
        .setForegroundColor(PALETTE.TEXT_BODY);
    } else {
      t.getTextStyle()
        .setFontFamily("Courier New")
        .setFontSize(7.5)
        .setForegroundColor(PALETTE.TEXT_BODY);
    }
    return box;
  }

  // Helper: Insert Card with Bullet List
  function insertCardWithBullets(slide, x, y, w, h, cardData) {
    insertCard(slide, x, y, w, h, PALETTE.CARD_BG, cardData.col || PALETTE.CARD_BORDER);
    var tb = slide.insertTextBox("", x + 10, y + 8, w - 20, h - 16);
    var t = tb.getText();
    t.setText(cardData.title + "\\n");
    t.getRange(0, cardData.title.length).getTextStyle()
      .setFontFamily("Arial")
      .setFontSize(10.5)
      .setBold(true)
      .setForegroundColor(cardData.col || PALETTE.ACCENT_CYAN);

    var curPos = cardData.title.length + 1;
    for (var i = 0; i < cardData.bullets.length; i++) {
      var item = cardData.bullets[i] + "\\n";
      t.appendText(item);
      var r = t.getRange(curPos, curPos + item.length);
      var isHeaderBullet = item.indexOf("•") !== -1 && item.indexOf(":") !== -1;
      r.getTextStyle()
        .setFontFamily("Arial")
        .setFontSize(8.2)
        .setBold(isHeaderBullet)
        .setForegroundColor(isHeaderBullet ? PALETTE.TEXT_WHITE : PALETTE.TEXT_BODY);
      curPos += item.length;
    }
    return tb;
  }

  // Helper: Set Speaker Notes
  function setSpeakerNotes(slide, notesContent) {
    var notesPage = slide.getNotesPage();
    var speakerNotesShape = notesPage.getSpeakerNotesShape();
    speakerNotesShape.getText().setText(notesContent);
  }

  // SLIDE RENDERERS
  function renderTitleSlide(slide, s) {
    var bar = slide.insertShape(SlidesApp.ShapeType.RECTANGLE, 0, 0, pageWidth, 5);
    bar.getFill().setSolidFill(PALETTE.ACCENT_CYAN);
    bar.getBorder().setTransparent();

    var badge = slide.insertShape(SlidesApp.ShapeType.ROUNDED_RECTANGLE, 35, 25, 280, 22);
    badge.getFill().setSolidFill(PALETTE.CARD_BG);
    badge.getBorder().getLineFill().setSolidFill(PALETTE.ACCENT_CYAN);
    var bt = badge.getText();
    bt.setText("COMPUTATIONAL FLUID DYNAMICS & HARDWARE DEFENSE");
    bt.getTextStyle().setFontFamily("Arial").setFontSize(7.5).setBold(true).setForegroundColor(PALETTE.ACCENT_CYAN);
    bt.getParagraphStyle().setAlignment(SlidesApp.ParagraphAlignment.CENTER);

    var titleBox = slide.insertTextBox(s.title, 35, 52, 650, 42);
    titleBox.getText().getTextStyle().setFontFamily("Arial").setFontSize(28).setBold(true).setForegroundColor(PALETTE.TEXT_WHITE);

    var subBox = slide.insertTextBox(s.subtitle, 35, 96, 650, 24);
    subBox.getText().getTextStyle().setFontFamily("Arial").setFontSize(10.5).setForegroundColor(PALETTE.TEXT_MUTED);

    var cardW = 152;
    var gap = 14;
    for (var i = 0; i < s.stats.length; i++) {
      var stat = s.stats[i];
      var cx = 35 + i * (cardW + gap);
      insertCard(slide, cx, 126, cardW, 78, PALETTE.CARD_BG, PALETTE.CARD_BORDER);

      var tb = slide.insertTextBox("", cx + 8, 134, cardW - 16, 62);
      var t = tb.getText();
      t.setText(stat.val + "\\n" + stat.lbl);
      t.getRange(0, stat.val.length).getTextStyle().setFontFamily("Arial").setFontSize(17).setBold(true).setForegroundColor(stat.col);
      t.getRange(stat.val.length + 1, t.getLength()).getTextStyle().setFontFamily("Arial").setFontSize(7.5).setForegroundColor(PALETTE.TEXT_MUTED);
    }

    insertCard(slide, 35, 218, 650, 160, PALETTE.CARD_BG, PALETTE.CARD_BORDER);
    var descBox = slide.insertTextBox("", 48, 228, 624, 140);
    var dt = descBox.getText();
    dt.setText("EXECUTIVE TECHNICAL BRIEFING STATEMENT:\\n" + s.summary);
    dt.getRange(0, 42).getTextStyle().setFontFamily("Arial").setFontSize(10).setBold(true).setForegroundColor(PALETTE.ACCENT_CYAN);
    dt.getRange(43, dt.getLength()).getTextStyle().setFontFamily("Arial").setFontSize(9).setForegroundColor(PALETTE.TEXT_BODY);

    setSpeakerNotes(slide, s.notes);
  }

  function renderSplitCards(slide, s) {
    applyHeader(slide, s.part, s.title, s.subtitle);
    insertCardWithBullets(slide, 35, 78, 315, 305, s.card1);
    insertCardWithBullets(slide, 370, 78, 315, 305, s.card2);
    setSpeakerNotes(slide, s.notes);
  }

  function renderSplitCode(slide, s) {
    applyHeader(slide, s.part, s.title, s.subtitle);
    insertCodeBox(slide, 35, 78, 325, 305, s.codeHeader, s.codeText, s.accent || PALETTE.ACCENT_CYAN);
    insertCardWithBullets(slide, 375, 78, 310, 305, s.card);
    setSpeakerNotes(slide, s.notes);
  }

  function renderThreeCards(slide, s) {
    applyHeader(slide, s.part, s.title, s.subtitle);
    var cardW = 206;
    var gap = 16;
    for (var i = 0; i < s.cards.length; i++) {
      var cx = 35 + i * (cardW + gap);
      insertCardWithBullets(slide, cx, 78, cardW, 305, s.cards[i]);
    }
    setSpeakerNotes(slide, s.notes);
  }

  function renderFullCode(slide, s) {
    applyHeader(slide, s.part, s.title, s.subtitle);
    insertCodeBox(slide, 35, 78, 650, 210, s.codeHeader, s.codeText, s.accent || PALETTE.ACCENT_CYAN);
    insertCardWithBullets(slide, 35, 298, 650, 85, s.bottomCard);
    setSpeakerNotes(slide, s.notes);
  }

  function renderTableSlide(slide, s) {
    applyHeader(slide, s.part, s.title, s.subtitle);
    var table = slide.insertTable(s.rows.length + 1, s.headers.length, 35, 80, 650, 300);

    for (var c = 0; c < s.headers.length; c++) {
      var hCell = table.getCell(0, c);
      hCell.getText().setText(s.headers[c]);
      hCell.getText().getTextStyle().setFontFamily("Arial").setFontSize(8.2).setBold(true).setForegroundColor(PALETTE.ACCENT_CYAN);
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
        cell.getText().getTextStyle().setFontFamily("Arial").setFontSize(7.8).setBold(isHighlight).setForegroundColor(fg);
        cell.getFill().setSolidFill(isHighlight ? "#064E3B" : (r % 2 === 0 ? "#0F172A" : "#1E293B"));
      }
    }
    setSpeakerNotes(slide, s.notes);
  }

  // 2. Iterate and Build All 82 Slides
  for (var i = 0; i < AEOLUS_SLIDES.length; i++) {
    var s = AEOLUS_SLIDES[i];
    var slide = createBaseSlide();

    if (s.type === "title") {
      renderTitleSlide(slide, s);
    } else if (s.type === "split_cards") {
      renderSplitCards(slide, s);
    } else if (s.type === "split_code") {
      renderSplitCode(slide, s);
    } else if (s.type === "three_cards") {
      renderThreeCards(slide, s);
    } else if (s.type === "full_code") {
      renderFullCode(slide, s);
    } else if (s.type === "table") {
      renderTableSlide(slide, s);
    }

    if ((i + 1) % 10 === 0 || i === AEOLUS_SLIDES.length - 1) {
      Logger.log("Progress: Rendered Slide " + (i + 1) + " / " + AEOLUS_SLIDES.length + ": " + s.title);
    }
  }

  Logger.log("==================================================================");
  Logger.log("SUCCESS: Project AEOLUS Presentation Successfully Generated!");
  Logger.log("Total Slides Created: " + AEOLUS_SLIDES.length);
  Logger.log("Presentation URL: " + deck.getUrl());
  Logger.log("==================================================================");

  return deck.getUrl();
}
"""
    return js_code

def main():
    print("Beginning compilation of 82-slide Project AEOLUS deck...")
    slides = compile_deck()
    js_code = generate_javascript(slides)

    output_path = "/home/aeolus_sim/build_aeolus_deck.js"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(js_code)
    print(f"Wrote {len(js_code)} bytes to {output_path}")

    # Validate with node
    print("Validating JavaScript syntax with node -c...")
    res = subprocess.run(["node", "-c", output_path], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error in JS syntax: {res.stderr}")
        exit(1)
    print("JavaScript syntax validated successfully!")

    # Update downloads and web server files
    download_dir = "/storage/emulated/0/Download"
    if os.path.isdir(download_dir):
        shutil.copy2(output_path, os.path.join(download_dir, "build_aeolus_deck.js"))
        print(f"Copied build_aeolus_deck.js to {download_dir}")

    home_symlink = "/home/build_aeolus_deck.js"
    if os.path.islink(home_symlink) or os.path.isfile(home_symlink):
        try:
            shutil.copy2(output_path, home_symlink)
        except Exception:
            pass

    # Update copy_deck.html
    update_copy_html(js_code)

def update_copy_html(js_code):
    html_path = "/home/aeolus_sim/copy_deck.html"
    escaped_js = js_code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Project AEOLUS - 82-Slide Master Google Apps Script Deck</title>
  <style>
    body {{
      background-color: #0F172A;
      color: #E2E8F0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
      padding: 24px;
      margin: 0;
    }}
    .container {{
      max-width: 900px;
      margin: 0 auto;
    }}
    h1 {{
      color: #38BDF8;
      margin-bottom: 8px;
    }}
    .stats-bar {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin: 20px 0;
    }}
    .stat-card {{
      background: #1E293B;
      padding: 12px;
      border-radius: 8px;
      border: 1px solid #334155;
      text-align: center;
    }}
    .stat-val {{
      font-size: 20px;
      font-weight: bold;
      color: #34D399;
    }}
    .stat-lbl {{
      font-size: 11px;
      color: #94A3B8;
      margin-top: 4px;
    }}
    .btn-copy {{
      background: #38BDF8;
      color: #0F172A;
      font-size: 18px;
      font-weight: bold;
      padding: 14px 28px;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      width: 100%;
      margin: 16px 0;
      transition: background 0.2s;
    }}
    .btn-copy:hover {{
      background: #0284C7;
      color: #FFFFFF;
    }}
    .code-box {{
      background: #090E17;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 16px;
      max-height: 400px;
      overflow-y: auto;
      font-family: "Courier New", monospace;
      font-size: 11px;
      white-space: pre-wrap;
      color: #94A3B8;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Project AEOLUS: Master Technical Briefing</h1>
    <p>Automated Google Apps Script Generator (<strong>82 Slides</strong> across 6 Exhaustive Modules)</p>

    <div class="stats-bar">
      <div class="stat-card">
        <div class="stat-val">82 Slides</div>
        <div class="stat-lbl">Full Curriculum</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">117.30%</div>
        <div class="stat-lbl">Vorticity Reduction</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">-47.80 Pa</div>
        <div class="stat-lbl">Auto-Tuned Suction</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">0.735</div>
        <div class="stat-lbl">Div. RMS (&lt;1.0)</div>
      </div>
    </div>

    <button id="copyBtn" class="btn-copy" onclick="copyToClipboard()">📋 COPY 82-SLIDE APPS SCRIPT TO CLIPBOARD</button>
    <div id="statusMsg" style="text-align: center; color: #34D399; font-weight: bold; margin-bottom: 12px; display: none;">✓ Copied to clipboard! Ready to paste into script.google.com</div>

    <h3>Google Apps Script Code (build_aeolus_deck.js)</h3>
    <div class="code-box" id="codeContent">{escaped_js}</div>
  </div>

  <script>
    function copyToClipboard() {{
      const text = document.getElementById("codeContent").innerText;
      navigator.clipboard.writeText(text).then(function() {{
        const msg = document.getElementById("statusMsg");
        msg.style.display = "block";
        const btn = document.getElementById("copyBtn");
        btn.innerText = "✓ COPIED TO CLIPBOARD!";
        btn.style.background = "#34D399";
        setTimeout(() => {{
          btn.innerText = "📋 COPY 82-SLIDE APPS SCRIPT TO CLIPBOARD";
          btn.style.background = "#38BDF8";
        }}, 3000);
      }}).catch(function(err) {{
        alert("Clipboard copy failed: " + err);
      }});
    }}
  </script>
</body>
</html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Updated {html_path}")

    download_dir = "/storage/emulated/0/Download"
    if os.path.isdir(download_dir):
        shutil.copy2(html_path, os.path.join(download_dir, "copy_deck.html"))
        print(f"Copied copy_deck.html to {download_dir}")

if __name__ == "__main__":
    main()

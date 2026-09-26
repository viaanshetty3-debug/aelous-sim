/**
 * PROJECT AEOLUS — Enhanced 82-Slide Master Technical Deck Builder
 * Google Apps Script that assembles the full presentation directly into
 * your Google Drive as a native Google Slides file.
 *
 * DATA FILES (already uploaded to your Drive by the assistant):
 *   AEOLUS_Data_Part1.txt   — slides 1–24
 *   AEOLUS_Data_Part2.txt   — slides 25–47
 *   AEOLUS_Data_Part3.txt   — slides 48–68
 *   AEOLUS_Data_Part4.txt   — slides 69–82
 *
 * HOW TO RUN (Android- or desktop-friendly):
 *   1. Open  https://script.google.com  in a browser (Chrome on Android works).
 *   2. Click  "New project"  and delete any default code.
 *   3. Paste this entire file into the editor and save (Ctrl/Cmd+S). Give
 *      the project any name (e.g. "AEOLUS Deck Builder").
 *   4. In the toolbar function selector, choose  buildAeolusDeck  and press
 *      the "Run" button.
 *   5. Grant the requested permissions on the first execution.
 *   6. Watch the Execution Log for a status line ending with:
 *          Presentation ready:  https://docs.google.com/presentation/d/<ID>/edit
 *      That URL is your finished Google Slides deck (also saved in Drive).
 *
 * OUTPUT:  A new Google Slides file titled
 *          "Project AEOLUS — Master Technical Briefing (82 Slides)"
 *          appears in the root of your Drive.
 */

// ----- Design palette --------------------------------------------------------
var BG        = "#0B121E";  // deep navy background
var PANEL     = "#141F35";  // card / panel fill
var PANEL2    = "#1A2740";  // alternating table row
var TEXT      = "#E5E7EB";  // primary text
var MUTED     = "#94A3B8";  // secondary text
var CYAN      = "#38BDF8";
var EMERALD   = "#34D399";
var AMBER     = "#F59E0B";
var ROSE      = "#F43F5E";
var VIOLET    = "#A78BFA";
var CODE_BG   = "#05101F";
var CODE_TXT  = "#86EF9A";

function accentFor(part) {
  if (!part) return CYAN;
  if (part.indexOf("Part 1") === 0 || part.indexOf("Master") === 0) return CYAN;
  if (part.indexOf("Part 2") === 0) return AMBER;
  if (part.indexOf("Part 3") === 0) return ROSE;
  if (part.indexOf("Part 4") === 0) return EMERALD;
  if (part.indexOf("Part 5") === 0) return VIOLET;
  if (part.indexOf("Part 6") === 0) return AMBER;
  if (part.indexOf("Executive") === 0) return EMERALD;
  if (part.indexOf("Technical Curriculum") === 0) return VIOLET;
  return CYAN;
}

// ----- Small helpers ---------------------------------------------------------
function addRect(slide, x, y, w, h, color, lineColor) {
  var shape = slide.insertShape(SlidesApp.ShapeType.RECTANGLE, x, y, w, h);
  shape.getFill().setSolidFill(color);
  if (lineColor) shape.getBorder().getLineFill().setSolidFill(lineColor);
  else shape.getBorder().setTransparent();
  return shape;
}
function addRoundRect(slide, x, y, w, h, color) {
  var shape = slide.insertShape(SlidesApp.ShapeType.ROUND_RECTANGLE, x, y, w, h);
  shape.getFill().setSolidFill(color);
  shape.getBorder().setTransparent();
  return shape;
}
function addText(slide, x, y, w, h, txt, opts) {
  opts = opts || {};
  var box = slide.insertTextBox(String(txt == null ? "" : txt), x, y, w, h);
  var tr = box.getText();
  var style = tr.getTextStyle();
  style.setFontSize(opts.size || 12)
       .setForegroundColor(opts.color || TEXT)
       .setBold(!!opts.bold)
       .setItalic(!!opts.italic)
       .setFontFamily(opts.font || "Roboto");
  if (opts.align) tr.getParagraphStyle().setParagraphAlignment(opts.align);
  return box;
}
function paintBackground(slide, color) {
  slide.getBackground().setSolidFill(color || BG);
}
function addHeader(slide, part, idx, total, accent) {
  addRect(slide, 0, 0, 720, 6, accent);
  addText(slide, 20, 12, 500, 16,
          "PROJECT AEOLUS  •  " + part,
          { size: 9, color: MUTED, bold: true, font: "Roboto Mono" });
  addText(slide, 560, 12, 145, 16,
          "SLIDE " + pad2(idx) + " / " + pad2(total),
          { size: 9, color: accent, bold: true,
            align: SlidesApp.ParagraphAlignment.END,
            font: "Roboto Mono" });
}
function addFooter(slide, accent) {
  addRect(slide, 0, 402, 720, 3, accent);
  addText(slide, 20, 386, 680, 12,
          "AEOLUS • Master Technical Briefing Compendium  —  3D Navier–Stokes • EF4 Vortex Disruption • CFD + Hardware Prototype",
          { size: 7.5, color: MUTED, italic: true });
}
function addTitleBlock(slide, title, subtitle, accent, yStart) {
  var y = (yStart == null) ? 40 : yStart;
  addText(slide, 24, y, 675, 32, title,
          { size: 22, color: TEXT, bold: true });
  addRect(slide, 24, y + 34, 42, 3, accent);
  if (subtitle) {
    addText(slide, 24, y + 40, 675, 22, subtitle,
            { size: 10, color: MUTED, italic: true });
  }
}
function pad2(n) { return (n < 10 ? "0" : "") + n; }

function joinBullets(bullets) {
  if (!bullets || !bullets.length) return "";
  return bullets.join("\n");
}

// ----- Slide renderers -------------------------------------------------------
function renderTitle(slide, s, idx, total) {
  var accent = accentFor(s.part);
  paintBackground(slide);
  addHeader(slide, s.part || "", idx, total, accent);
  addFooter(slide, accent);

  addText(slide, 28, 55, 664, 56, s.title || "",
          { size: 36, color: accent, bold: true });
  addText(slide, 28, 115, 664, 28, s.subtitle || "",
          { size: 13, color: TEXT, italic: true });

  var stats = s.stats || [];
  if (stats.length > 0) {
    var totalW = 664, gap = 8;
    var n = stats.length;
    var w = (totalW - gap * (n - 1)) / n;
    for (var i = 0; i < n; i++) {
      var x = 28 + (w + gap) * i;
      var y = 155;
      var h = 75;
      addRoundRect(slide, x, y, w, h, PANEL);
      addRect(slide, x, y, 5, h, stats[i].col || accent);
      addText(slide, x + 10, y + 8, w - 15, 28,
              stats[i].val || "",
              { size: 18, color: stats[i].col || accent, bold: true });
      addText(slide, x + 10, y + 40, w - 15, h - 45,
              stats[i].lbl || "",
              { size: 7.5, color: MUTED });
    }
  }
  if (s.summary) {
    addRoundRect(slide, 28, 245, 664, 128, PANEL);
    addText(slide, 40, 254, 640, 16, "EXECUTIVE ABSTRACT",
            { size: 9, color: accent, bold: true, font: "Roboto Mono" });
    addText(slide, 40, 272, 640, 96, s.summary,
            { size: 9.5, color: TEXT });
  }
}

function renderThreeCards(slide, s, idx, total) {
  var accent = accentFor(s.part);
  paintBackground(slide);
  addHeader(slide, s.part || "", idx, total, accent);
  addFooter(slide, accent);
  addTitleBlock(slide, s.title, s.subtitle, accent);

  var cards = (s.cards || []).slice(0, 3);
  var n = cards.length;
  if (!n) return;
  var totalW = 675, gap = 10;
  var w = (totalW - gap * (n - 1)) / n;
  for (var i = 0; i < n; i++) {
    var x = 24 + (w + gap) * i;
    var y = 122;
    var h = 250;
    var col = cards[i].col || accent;
    addRoundRect(slide, x, y, w, h, PANEL);
    addRect(slide, x, y, w, 4, col);
    addText(slide, x + 10, y + 10, w - 15, 26,
            cards[i].title || "",
            { size: 12, color: col, bold: true });
    addText(slide, x + 10, y + 40, w - 15, h - 46,
            joinBullets(cards[i].bullets),
            { size: 8, color: TEXT });
  }
}

function renderSplitCards(slide, s, idx, total) {
  var accent = accentFor(s.part);
  paintBackground(slide);
  addHeader(slide, s.part || "", idx, total, accent);
  addFooter(slide, accent);
  addTitleBlock(slide, s.title, s.subtitle, accent);

  var totalW = 675, gap = 12;
  var w = (totalW - gap) / 2;
  var cards = [s.card1, s.card2];
  var cols  = [accent, EMERALD];
  for (var i = 0; i < 2; i++) {
    var c = cards[i]; if (!c) continue;
    var x = 24 + (w + gap) * i;
    var y = 122;
    var h = 252;
    addRoundRect(slide, x, y, w, h, PANEL);
    addRect(slide, x, y, w, 4, cols[i]);
    addText(slide, x + 12, y + 10, w - 20, 26,
            c.title || "",
            { size: 13, color: cols[i], bold: true });
    addText(slide, x + 12, y + 42, w - 20, h - 50,
            joinBullets(c.bullets),
            { size: 8.5, color: TEXT });
  }
}

function renderSplitCode(slide, s, idx, total) {
  var accent = s.accent || accentFor(s.part);
  paintBackground(slide);
  addHeader(slide, s.part || "", idx, total, accent);
  addFooter(slide, accent);
  addTitleBlock(slide, s.title, s.subtitle, accent);

  // Left: code
  var lx = 24, ly = 122, lw = 385, lh = 250;
  addRoundRect(slide, lx, ly, lw, lh, CODE_BG);
  addRect(slide, lx, ly, lw, 4, accent);
  addText(slide, lx + 12, ly + 10, lw - 20, 18,
          s.codeHeader || "",
          { size: 9, color: accent, bold: true, font: "Roboto Mono" });
  addText(slide, lx + 12, ly + 32, lw - 20, lh - 42,
          s.codeText || "",
          { size: 7, color: CODE_TXT, font: "Roboto Mono" });

  // Right: card
  var rx = 417, ry = 122, rw = 282, rh = 250;
  var c = s.card || {};
  addRoundRect(slide, rx, ry, rw, rh, PANEL);
  addRect(slide, rx, ry, rw, 4, EMERALD);
  addText(slide, rx + 12, ry + 10, rw - 20, 22,
          c.title || "DYNAMICS",
          { size: 12, color: EMERALD, bold: true });
  addText(slide, rx + 12, ry + 40, rw - 20, rh - 48,
          joinBullets(c.bullets),
          { size: 8, color: TEXT });
}

function renderFullCode(slide, s, idx, total) {
  var accent = s.accent || accentFor(s.part);
  paintBackground(slide);
  addHeader(slide, s.part || "", idx, total, accent);
  addFooter(slide, accent);
  addTitleBlock(slide, s.title, s.subtitle, accent);

  addRoundRect(slide, 24, 122, 675, 190, CODE_BG);
  addRect(slide, 24, 122, 675, 4, accent);
  addText(slide, 36, 132, 660, 18,
          s.codeHeader || "",
          { size: 9, color: accent, bold: true, font: "Roboto Mono" });
  addText(slide, 36, 152, 660, 152,
          s.codeText || "",
          { size: 6.5, color: CODE_TXT, font: "Roboto Mono" });

  var b = s.bottomCard || {};
  addRoundRect(slide, 24, 318, 675, 55, PANEL);
  addRect(slide, 24, 318, 675, 3, EMERALD);
  addText(slide, 36, 324, 660, 16,
          b.title || "KEY POINTS",
          { size: 10, color: EMERALD, bold: true });
  var bl = (b.bullets || []).slice(0, 4).join("   ");
  addText(slide, 36, 342, 660, 30, bl,
          { size: 7.5, color: TEXT });
}

function renderTable(slide, s, idx, total) {
  var accent = accentFor(s.part);
  paintBackground(slide);
  addHeader(slide, s.part || "", idx, total, accent);
  addFooter(slide, accent);
  addTitleBlock(slide, s.title, s.subtitle, accent);

  var headers = s.headers || [];
  var rows = s.rows || [];
  if (!headers.length) return;
  var nCols = headers.length;
  var nRows = rows.length + 1;
  var tbl = slide.insertTable(nRows, nCols, 24, 122, 675, 250);
  // Header row
  for (var c = 0; c < nCols; c++) {
    var cell = tbl.getCell(0, c);
    cell.getFill().setSolidFill(accent);
    var t = cell.getText().setText(String(headers[c] == null ? "" : headers[c]));
    t.getTextStyle().setFontSize(8).setBold(true).setForegroundColor(BG)
     .setFontFamily("Roboto");
  }
  // Body rows
  for (var r = 0; r < rows.length; r++) {
    var row = rows[r];
    for (var c2 = 0; c2 < nCols; c2++) {
      var cell2 = tbl.getCell(r + 1, c2);
      cell2.getFill().setSolidFill((r % 2 === 0) ? PANEL : PANEL2);
      var val = (c2 < row.length && row[c2] != null) ? row[c2] : "";
      var t2 = cell2.getText().setText(String(val));
      t2.getTextStyle().setFontSize(7.5).setForegroundColor(TEXT)
        .setFontFamily("Roboto");
    }
  }
}

// ----- Speaker note enhancer -------------------------------------------------
function enhanceNotes(notes, part, title) {
  var lead = "[ENHANCED LECTURE NOTES  —  " + (part || "") + "]\n" +
             "Slide focus: " + (title || "") + "\n\n";
  var tail = "\n\nPEDAGOGICAL EXTENSIONS:\n" +
    " • Framing question: how does this slide connect the equations to " +
    "the physical mechanism defended?\n" +
    " • Cross-reference: this material anchors the defense in the " +
    "grid.py → solver.py → interventions architecture.\n" +
    " • Extension exercise: sketch a dimensional-analysis check on each " +
    "surviving term.\n" +
    " • Failure mode: describe one boundary condition that, if violated, " +
    "would invalidate the result here.\n" +
    " • Verification hook: which test in the 17/17 pytest suite guards " +
    "the invariant introduced on this slide?";
  return lead + (notes || "") + tail;
}

// ----- Data loader -----------------------------------------------------------
function loadAllSlideData_() {
  var names = ["AEOLUS_Data_Part1.txt","AEOLUS_Data_Part2.txt",
               "AEOLUS_Data_Part3.txt","AEOLUS_Data_Part4.txt"];
  var out = [];
  for (var i = 0; i < names.length; i++) {
    var files = DriveApp.getFilesByName(names[i]);
    if (!files.hasNext()) {
      throw new Error("Missing data file in Drive: " + names[i]);
    }
    var raw = files.next().getBlob().getDataAsString("UTF-8");
    var arr = JSON.parse(raw);
    for (var j = 0; j < arr.length; j++) out.push(arr[j]);
  }
  return out;
}

// ----- Main entry point ------------------------------------------------------
function buildAeolusDeck() {
  var slidesData = loadAllSlideData_();
  Logger.log("Loaded " + slidesData.length + " slides from Drive data files.");

  var deck = SlidesApp.create(
    "Project AEOLUS — Master Technical Briefing (82 Slides)");
  // Remove default placeholder slide
  var initial = deck.getSlides();
  if (initial.length > 0) initial[0].remove();

  var total = slidesData.length;
  for (var i = 0; i < total; i++) {
    var s = slidesData[i];
    var slide = deck.appendSlide(SlidesApp.PredefinedLayout.BLANK);
    try {
      switch (s.type) {
        case "title":       renderTitle(slide, s, i + 1, total); break;
        case "three_cards": renderThreeCards(slide, s, i + 1, total); break;
        case "split_cards": renderSplitCards(slide, s, i + 1, total); break;
        case "split_code":  renderSplitCode(slide, s, i + 1, total); break;
        case "full_code":   renderFullCode(slide, s, i + 1, total); break;
        case "table":       renderTable(slide, s, i + 1, total); break;
        default:
          paintBackground(slide);
          addText(slide, 40, 180, 640, 40,
                  "Unhandled slide type: " + s.type,
                  { size: 16, color: ROSE });
      }
      var notes = enhanceNotes(s.notes, s.part, s.title);
      slide.getNotesPage().getSpeakerNotesShape().getText().setText(notes);
    } catch (err) {
      Logger.log("Slide " + (i + 1) + " (" + s.type + ") failed: " + err);
    }
    if ((i + 1) % 10 === 0) Logger.log("  rendered " + (i + 1) + " slides");
  }

  var url = deck.getUrl();
  Logger.log("=====================================================");
  Logger.log("Presentation ready:  " + url);
  Logger.log("=====================================================");
  return url;
}

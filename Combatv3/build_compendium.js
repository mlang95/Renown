// build_compendium.js — render the Compendium .docx from renown_data JSON,
// matching the AUTHORED doc's formatting: landscape, 0.5" margins, EB Garamond,
// tight tables, minimal page breaks. Goal: compact, ~13pp not 21pp.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, WidthType, BorderStyle, ShadingType, PageOrientation,
} = require("docx");

const data = JSON.parse(fs.readFileSync(process.argv[2] || "compendium_data.json", "utf8"));
const OUT = process.argv[3] || "Compendium.docx";

const FONT = "EB Garamond";
const BODY = 17;          // 8.5pt, matches authored doc
const HEAD_FILL = "EFEFEF";
const thin = { style: BorderStyle.SINGLE, size: 4, color: "auto" };
const borders = { top: thin, bottom: thin, left: thin, right: thin,
                  insideHorizontal: thin, insideVertical: thin };
const cellMargins = { top: 14, bottom: 14, left: 40, right: 40 };

function run(text, opts = {}) {
  return new TextRun({ text: String(text), bold: !!opts.bold, italics: !!opts.i,
    size: opts.size || BODY, font: FONT });
}
// split **bold** markup into alternating regular/bold runs
function richRuns(text, opts = {}) {
  const parts = String(text).split(/(\*\*[^*]+\*\*)/g).filter((p) => p !== "");
  if (parts.length === 0) return [run("", opts)];
  if (parts.length === 1 && !/^\*\*[^*]+\*\*$/.test(parts[0])) return [run(parts[0], opts)];
  return parts.map((p) => {
    const m = /^\*\*([^*]+)\*\*$/.exec(p);
    return new TextRun({ text: m ? m[1] : p, bold: m ? true : !!opts.bold,
      italics: !!opts.i, size: opts.size || BODY, font: FONT });
  });
}
function cell(text, opts = {}) {
  return new TableCell({ borders, margins: cellMargins,
    children: [new Paragraph({ spacing: { before: 0, after: 0, line: 200, lineRule: "auto" },
      children: opts.head ? [run(text, { bold: true })] : richRuns(text) })] });
}
function table(headers, rows) {
  const head = new TableRow({ tableHeader: true,
    children: headers.map((h) => cell(h, { head: true })) });
  const body = rows.map((r) => new TableRow({ children: r.map((c) => cell(c)) }));
  return new Table({ width: { size: 100, type: WidthType.PERCENTAGE },
    alignment: "center", rows: [head, ...body] });
}
function h1(t) { return new Paragraph({ heading: HeadingLevel.HEADING_1,
  spacing: { before: 180, after: 60 }, children: [new TextRun({ text: t, font: FONT, bold: true, size: 32 })] }); }
function h2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2,
  spacing: { before: 120, after: 40 }, children: [new TextRun({ text: t, font: FONT, bold: true, size: 26 })] }); }
function para(t, opts = {}) { return new Paragraph({ spacing: { before: 0, after: 40 },
  children: [run(t, opts)] }); }
function tight() { return new Paragraph({ spacing: { before: 0, after: 20 }, children: [] }); }

const kids = [];
kids.push(new Paragraph({ heading: HeadingLevel.TITLE, spacing: { after: 80 },
  children: [new TextRun({ text: "Renown — Compendium", font: FONT, bold: true, size: 44 })] }));
kids.push(para("Generated from renown_data.py — the single source of truth.", { i: true }));

// Pursuits (no page breaks between sections; let it flow)
kids.push(h1("Pursuits"));
for (const sec of data.pursuit_sections) {
  kids.push(h2(sec.title));
  kids.push(table(["Pursuit", "Mastery Unlock", "Innate Effect", "Mastery Effect"], sec.rows));
}

kids.push(h1("Equipment"));
kids.push(h2("Retinues"));
kids.push(table(["Retinue", "Cost", "To Hit", "Endurance", "Morale", "Keyword"], data.equipment.Retinues));
kids.push(h2("Melee Weapons"));
kids.push(table(["Weapon", "Tier", "AP", "Init", "Keywords"], data.equipment.Weapons));
kids.push(h2("Ranged Weapons"));
kids.push(table(["Ranged", "Tier", "AP", "Init", "Keywords"], data.equipment.Ranged));
kids.push(h2("Shields"));
kids.push(table(["Shield", "Tier", "Save", "Init", "Keywords"], data.equipment.Shields));
kids.push(h2("Armor"));
kids.push(table(["Armor", "Tier", "Save", "Keywords"], data.equipment.Armor));

kids.push(h1("Infrastructure & Wonders"));
kids.push(table(["Infrastructure", "Upkeep", "Freq", "Empire Bonus", "Tier", "Build", "Requirement"], data.infrastructure));
kids.push(h2("Wonders"));
kids.push(table(["Wonder", "Empire Bonus", "Build", "Requirement"], data.wonders));

kids.push(h1("Empire"));
kids.push(h2("Settlements"));
kids.push(table(["Settlement", "Tier", "Sea Variant", "Tax", "Muster", "Build", "Wards", "Reach", "Notes"], data.settlements));
kids.push(h2("Eras"));
kids.push(table(["Era", "Renown", "Armies", "Cities", "Infl/Turn", "Diplo Infl", "Envoys", "Unlocks"], data.eras));
kids.push(h2("Domain Standings (empire)"));
kids.push(table(["Domain", "Rising (3)", "Established (6)", "Sovereign (10)"], data.domain_board));
kids.push(h2("Domain Standing Effects (combat)"));
kids.push(table(["Domain", "Rising", "Established", "Sovereign"], data.standing_effects));
kids.push(h2("Tactic Matrix"));
kids.push(table(data.tactic_matrix_header, data.tactic_matrix_rows));
kids.push(h2("Public Order"));
kids.push(table(["PO", "State", "Effect"], data.public_order));
kids.push(h2("Faith & Doubt Sources"));
kids.push(table(["Type", "Source", "Condition"], data.po_modifiers));
kids.push(h2("Seasons"));
kids.push(table(["Season", "Name", "Effect"], data.seasons));
kids.push(h2("Trade & Income"));
kids.push(table(["Rule", "Value"], data.trade_rules));

kids.push(h1("Factions"));
kids.push(table(["Faction", "Mechanic"], data.factions));

kids.push(h1("Glossary"));
for (const cat of data.glossary_categorized) {
  kids.push(h2(cat.title));
  // glossary as a compact 2-col table instead of paragraphs (denser)
  kids.push(table(["Term", "Definition"], cat.rows));
}

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: BODY } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", next: "Normal",
        run: { size: 44, bold: true, font: FONT }, paragraph: { spacing: { after: 80 } } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: FONT }, paragraph: { spacing: { before: 180, after: 60 }, outlineLevel: 0, keepNext: true } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: FONT }, paragraph: { spacing: { before: 120, after: 40 }, outlineLevel: 1, keepNext: true } },
    ] },
  sections: [{
    properties: { page: {
      size: { orientation: PageOrientation.LANDSCAPE, width: 16838, height: 11906 },
      margin: { top: 720, right: 720, bottom: 720, left: 720 } } },
    children: kids,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log("wrote " + OUT); });

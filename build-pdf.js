// Сборка ИНСТРУКЦИЯ.pdf из ИНСТРУКЦИЯ.md.
// 1) markdown -> self-contained HTML (картинки вшиваются в base64);
// 2) печать HTML в PDF через headless Chrome/Edge (без скачиваний).
//
// Запуск:  npm install markdown-it   (один раз)
//          node build-pdf.js
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const MarkdownIt = require("markdown-it");

const ROOT = __dirname;
const SRC = path.join(ROOT, "ИНСТРУКЦИЯ.md");
const OUT_HTML = path.join(ROOT, "instruction.html");
const OUT_PDF = path.join(ROOT, "ИНСТРУКЦИЯ.pdf");

const md = new MarkdownIt({ html: true, linkify: true, typographer: false });

let raw = fs.readFileSync(SRC, "utf8");
let body = md.render(raw);

// Встроить локальные картинки как data-URI, чтобы PDF был самодостаточным.
body = body.replace(/<img([^>]*?)src="([^"]+)"([^>]*?)>/g, (m, pre, src, post) => {
  if (/^(https?:|data:)/.test(src)) return m;
  const file = path.join(ROOT, decodeURIComponent(src));
  try {
    const buf = fs.readFileSync(file);
    const ext = path.extname(file).slice(1).toLowerCase();
    const mime = ext === "svg" ? "image/svg+xml" : `image/${ext === "jpg" ? "jpeg" : ext}`;
    const data = `data:${mime};base64,${buf.toString("base64")}`;
    return `<img${pre}src="${data}"${post}>`;
  } catch (e) {
    return m;
  }
});

const css = `
  @page { size: A4; margin: 16mm 14mm; }
  * { box-sizing: border-box; }
  body { font-family: "Segoe UI", Arial, sans-serif; font-size: 11pt; line-height: 1.5;
         color: #1f2430; max-width: 100%; }
  h1 { font-size: 22pt; border-bottom: 3px solid #4b6bfb; padding-bottom: 6px; }
  h2 { font-size: 17pt; margin-top: 26px; border-bottom: 1px solid #d0d7e2; padding-bottom: 4px;
       page-break-before: auto; }
  h3 { font-size: 13pt; margin-top: 18px; color: #2b3550; }
  code { background: #f0f2f7; padding: 1px 5px; border-radius: 4px;
         font-family: "Cascadia Code", Consolas, monospace; font-size: 9.5pt; }
  pre { background: #0f1525; color: #e6e9f0; padding: 12px 14px; border-radius: 8px;
        overflow-x: auto; font-size: 9pt; line-height: 1.45; }
  pre code { background: transparent; color: inherit; padding: 0; }
  table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 10pt; }
  th, td { border: 1px solid #c8d0de; padding: 6px 9px; text-align: left; vertical-align: top; }
  th { background: #eef1f8; }
  tr:nth-child(even) td { background: #fafbfe; }
  blockquote { border-left: 4px solid #f0a020; background: #fff8ec; margin: 12px 0;
               padding: 8px 14px; border-radius: 0 6px 6px 0; }
  img { max-width: 100%; height: auto; display: block; margin: 10px auto;
        border: 1px solid #e2e6ef; border-radius: 6px; }
  a { color: #2b53d8; text-decoration: none; }
  hr { border: none; border-top: 1px solid #d0d7e2; margin: 22px 0; }
  h2, h3 { page-break-after: avoid; }
  table, pre, img, blockquote { page-break-inside: avoid; }
`;

const html = `<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<title>Voron 2.4 Gr1mSkull — Инструкция</title>
<style>${css}</style></head>
<body>${body}</body></html>`;

fs.writeFileSync(OUT_HTML, html, "utf8");
console.log("HTML:", `${Math.round(html.length / 1024)} KB`);

// --- Найти браузер на базе Chromium ---
function findBrowser() {
  const pf = process.env["ProgramFiles"] || "C:\\Program Files";
  const pf86 = process.env["ProgramFiles(x86)"] || "C:\\Program Files (x86)";
  const candidates = [
    path.join(pf, "Google\\Chrome\\Application\\chrome.exe"),
    path.join(pf86, "Google\\Chrome\\Application\\chrome.exe"),
    path.join(pf86, "Microsoft\\Edge\\Application\\msedge.exe"),
    path.join(pf, "Microsoft\\Edge\\Application\\msedge.exe"),
  ];
  return candidates.find((p) => fs.existsSync(p));
}

const browser = findBrowser();
if (!browser) {
  console.log("HTML готов. Браузер Chrome/Edge не найден — откройте instruction.html и Печать -> Сохранить как PDF.");
  process.exit(0);
}

const fileUrl = "file:///" + OUT_HTML.replace(/\\/g, "/").replace(/ /g, "%20");
execFileSync(browser, [
  "--headless=new",
  "--disable-gpu",
  "--no-pdf-header-footer",
  "--run-all-compositor-stages-before-draw",
  "--virtual-time-budget=10000",
  `--print-to-pdf=${OUT_PDF}`,
  fileUrl,
], { stdio: "ignore" });

fs.rmSync(OUT_HTML, { force: true });
const kb = Math.round(fs.statSync(OUT_PDF).size / 1024);
console.log("PDF готов:", OUT_PDF, `(${kb} KB)`);

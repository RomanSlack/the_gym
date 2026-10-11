// Export every sheet of the drawing set as one A1 PDF.
// node tools/export/export_pdf.js [out.pdf]   (needs the blueprint dev server on :5280)
const { chromium } = require('/tmp/figt/node_modules/playwright-core');
const { execFileSync } = require('child_process');
const fs = require('fs'); const path = require('path');
const SHEETS = ['A-100', 'A-101', 'A-102', 'A-103', 'A-104', 'A-105', 'A-106', 'A-201', 'A-202', 'A-203', 'A-204', 'A-301', 'A-302', 'A-303', 'A-601'];
(async () => {
  const out = path.resolve(process.argv[2] || 'docs/drawings/THE_GYM_drawing_set.pdf');
  fs.mkdirSync(path.dirname(out), { recursive: true });
  const tmp = fs.mkdtempSync('/tmp/gympdf-');
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', headless: true });
  const c = await b.newContext({ viewport: { width: 3179, height: 2245 } });
  await c.addInitScript(() => localStorage.setItem('gym-theme', 'light'));
  const p = await c.newPage(); const files = [];
  for (const s of SHEETS) {
    await p.goto('about:blank'); await p.goto(`http://localhost:5280/?print&export#${s}`); await p.waitForTimeout(3000);
    const f = path.join(tmp, `${s}.pdf`);
    await p.pdf({ path: f, width: '841mm', height: '594mm', printBackground: true, pageRanges: '1' });
    files.push(f); console.log('sheet', s);
  }
  await b.close();
  execFileSync('pdfunite', [...files, out]);
  console.log('wrote', out, (fs.statSync(out).size / 1e6).toFixed(1), 'MB');
})();

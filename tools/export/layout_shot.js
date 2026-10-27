// Screenshot a 2D layout page (blueprint/layout.html?name=...) to a PNG, never overwriting: <out>_vNNN.png.
// node tools/export/layout_shot.js <name> <out_prefix> [x0,y0,x1,y1] [width] [height]   (needs the blueprint dev server on :5280)
const path = require('path'); const fs = require('fs');
const pw = ['/home/roman/pichon_tools/node_modules/playwright-core', '/tmp/figt/node_modules/playwright-core'].find((p) => fs.existsSync(p));
const { chromium } = require(pw);
(async () => {
  const [name, prefix, view, W = '2600', H = '1500'] = process.argv.slice(2);
  let n = 1; while (fs.existsSync(`${prefix}_v${String(n).padStart(3, '0')}.png`)) n++;
  const out = `${prefix}_v${String(n).padStart(3, '0')}.png`;
  fs.mkdirSync(path.dirname(out), { recursive: true });
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', headless: true });
  const p = await (await b.newContext({ viewport: { width: +W, height: +H }, deviceScaleFactor: 1 })).newPage();
  await p.goto(`http://localhost:5280/layout.html?name=${name}${view ? `&view=${view}` : ''}`); await p.waitForTimeout(2500);
  await p.screenshot({ path: out });
  await b.close(); console.log(out);
})();

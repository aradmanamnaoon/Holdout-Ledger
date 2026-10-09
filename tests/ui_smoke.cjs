/* DOM integration check. Run the local API on port 8765 before invoking. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { JSDOM, VirtualConsole } = require('jsdom');

const root = path.join(__dirname, '../src/holdout_ledger/static');
const base = process.env.HOLDOUT_LEDGER_TEST_URL || 'http://127.0.0.1:8765';
const errors = [];
const virtualConsole = new VirtualConsole();
virtualConsole.on('jsdomError', error => errors.push(error.message));
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

async function waitFor(check, context) {
  for (let attempt = 0; attempt < 200; attempt += 1) {
    if (await check()) return;
    await delay(25);
  }
  throw new Error(`UI condition timed out: ${context()}`);
}

async function main() {
  await waitFor(async () => {
    try { return (await fetch(`${base}/health`)).ok; }
    catch { return false; }
  }, () => `API not ready at ${base}`);

  const dashboard = new JSDOM(fs.readFileSync(path.join(root, 'index.html'), 'utf8'), {
    url: base,
    runScripts: 'dangerously',
    virtualConsole,
    beforeParse(window) {
      window.fetch = (url, options) => fetch(base + url, options);
      window.TextEncoder = TextEncoder;
      window.TextDecoder = TextDecoder;
    },
  });
  let explorer;
  try {
    const document = dashboard.window.document;
    const status = () => document.getElementById('status').textContent;
    document.getElementById('demo').click();
    await waitFor(() => document.getElementById('records').value.includes('train-exact'), status);
    document.getElementById('include').checked = true;
    document.getElementById('audit').click();
    await waitFor(() => status().startsWith('Snapshot saved:'), status);
    assert.equal(document.querySelectorAll('#stats .stat').length, 3);
    assert.equal(document.querySelector('#stats strong').textContent, '14');
    const id = document.getElementById('current').value;
    const response = await fetch(`${base}/api/reports/${id}/html`);
    assert.equal(response.status, 200);
    explorer = new JSDOM(await response.text(), {
      runScripts: 'dangerously',
      virtualConsole,
      beforeParse(window) {
        window.Element.prototype.scrollIntoView = () => {};
      },
    });
    const evidence = explorer.window.document;
    assert.equal(evidence.querySelectorAll('#clusters tr').length, 4);
    evidence.querySelector('#clusters button').click();
    assert.equal(evidence.getElementById('detail').hidden, false);
    assert.ok(evidence.querySelectorAll('#graph circle').length >= 2);
    assert.ok(evidence.querySelectorAll('#members tr').length >= 2);
    assert.equal(errors.length, 0, errors.join('\n'));
    fs.writeFileSync(process.env.HOLDOUT_LEDGER_UI_RESULT || 'smoke-result.json', JSON.stringify({
      passed: true,
      checks: ['synthetic demo load', 'audit submission', 'snapshot persistence',
        'result statistics', '4 cross-split components', 'witness graph',
        'record inspection', 'no JavaScript errors'],
      visual_browser_check: false,
    }, null, 2));
    process.stdout.write('Dashboard DOM workflow passed. No browser screenshot was produced.\n');
  } finally {
    dashboard.window.close();
    explorer?.window.close();
  }
}

main().catch(error => {
  process.stderr.write(`${error.stack}\n`);
  process.exitCode = 1;
});

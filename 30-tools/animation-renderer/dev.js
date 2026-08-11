/* ------------------------------------------------------------------
   Dev server with live reload.

   Run:  npm run dev
   Then open http://localhost:5173 in your browser.

   Save params.js and the browser reloads itself. No refreshing.
   Leave this running in a terminal tab while you work.
   Ctrl+C to stop it.

   No dependencies, just Node's built-ins.
------------------------------------------------------------------ */

const http = require('http');
const fs   = require('fs');
const path = require('path');

const PORT = 5173;
const ROOT = __dirname;

// Files that trigger a reload when saved
const WATCHED = ['params.js', 'index-gl.html', 'index.html'];

// What "/" serves. index-gl.html is what render.js actually captures, so
// that is what you want to be looking at. index.html is the original CSS
// version, still served at /index.html if you want to compare them.
const ENTRY = 'index-gl.html';

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js':   'text/javascript; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png':  'image/png',
};

// Every connected browser tab, so we can tell them all to reload
let clients = [];

// The script injected into index.html that listens for the reload signal
const RELOAD_SNIPPET = `
<script>
(function () {
  var es = new EventSource('/__reload');
  es.onmessage = function () { location.reload(); };
  es.onerror = function () {
    // Server stopped. Poll until it's back, then reload.
    es.close();
    var retry = setInterval(function () {
      fetch('/__ping').then(function () {
        clearInterval(retry);
        location.reload();
      }).catch(function () {});
    }, 800);
  };
  console.log('[dev] live reload connected');
})();
</script>
`;

const server = http.createServer((req, res) => {
  const url = req.url.split('?')[0];

  // Browsers subscribe here and hold the connection open
  if (url === '/__reload') {
    res.writeHead(200, {
      'Content-Type':  'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection':    'keep-alive',
    });
    res.write('\n');
    clients.push(res);
    req.on('close', () => { clients = clients.filter(c => c !== res); });
    return;
  }

  if (url === '/__ping') {
    res.writeHead(200);
    return res.end('ok');
  }

  const file = url === '/' ? ENTRY : decodeURIComponent(url.slice(1));
  const full = path.join(ROOT, file);

  // Don't serve anything outside the project folder
  if (!full.startsWith(ROOT)) {
    res.writeHead(403);
    return res.end('forbidden');
  }

  fs.readFile(full, (err, data) => {
    if (err) {
      res.writeHead(404);
      return res.end('not found');
    }

    const ext = path.extname(full).toLowerCase();
    res.writeHead(200, {
      'Content-Type':  TYPES[ext] || 'application/octet-stream',
      'Cache-Control': 'no-store',   // always fetch fresh, never cache
    });

    // Inject the reload listener into the preview page only
    if (ext === '.html') {
      return res.end(data.toString().replace('</body>', RELOAD_SNIPPET + '</body>'));
    }
    res.end(data);
  });
});

// Debounced so one save doesn't fire three reloads
let timer = null;
function onChange(file) {
  clearTimeout(timer);
  timer = setTimeout(() => {
    const t = new Date().toLocaleTimeString();
    console.log(`  ${t}  ${file} changed, reloading ${clients.length} tab(s)`);
    clients.forEach(c => c.write('data: reload\n\n'));
  }, 60);
}

// Watch the FOLDER, not the individual files.
// Editors like VS Code save by writing a temp file and renaming it over the
// original. That replaces the file, which kills a watcher pointed at the file
// itself, so reload would work exactly once and then quietly stop.
// The folder's identity doesn't change, so watching it survives.
fs.watch(ROOT, (event, filename) => {
  if (filename && WATCHED.includes(filename)) onChange(filename);
});

server.listen(PORT, () => {
  console.log('');
  console.log('  Ecoplex outro preview running');
  console.log('');
  console.log(`  Open:     http://localhost:${PORT}`);
  console.log(`  Watching: ${WATCHED.join(', ')}`);
  console.log('');
  console.log('  Save params.js and the browser reloads itself.');
  console.log('  Ctrl+C to stop.');
  console.log('');
});

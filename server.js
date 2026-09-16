/**
 * PixelQuote — Node.js web server
 * - Serves the HTML/CSS/JS frontend (frontend/)
 * - Connects /api/* to the Python (FastAPI + Pillow) backend on :8000
 * - Auto-starts the Python backend so `npm start` runs the whole project
 */
const path = require("path");
const { spawn } = require("child_process");
const express = require("express");
const cors = require("cors");

const WEB_PORT = process.env.PORT || 8080;
const PY_PORT = process.env.PY_PORT || 8000;
const PY_URL = `http://127.0.0.1:${PY_PORT}`;

const app = express();
app.use(cors());
app.use(express.json({ limit: "1mb" }));

// ---------- auto-start Python backend ----------
const py = spawn("python", ["-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", String(PY_PORT)], {
  cwd: __dirname,
  shell: false,
  stdio: ["ignore", "pipe", "pipe"],
});
py.stdout.on("data", (d) => process.stdout.write(`[python] ${d}`));
py.stderr.on("data", (d) => process.stderr.write(`[python] ${d}`));
py.on("error", (e) => console.error("[python] failed to start:", e.message));
process.on("exit", () => { try { py.kill(); } catch {} });
process.on("SIGINT", () => { try { py.kill(); } catch {} process.exit(0); });

// ---------- proxy /api/* -> Python (native fetch, Node 18+) ----------
app.use("/api", async (req, res) => {
  try {
    const target = PY_URL + req.originalUrl;
    const headers = { ...req.headers };
    delete headers.host;
    delete headers["content-length"];
    if (req.method === "GET" || req.method === "HEAD") {
      headers["content-type"] = undefined;
    }
    const upstream = await fetch(target, {
      method: req.method,
      headers,
      body: ["GET", "HEAD"].includes(req.method) ? undefined : JSON.stringify(req.body),
    });
    res.status(upstream.status);
    upstream.headers.forEach((v, k) => {
      if (!["content-encoding", "transfer-encoding", "connection"].includes(k.toLowerCase())) {
        res.setHeader(k, v);
      }
    });
    const buf = Buffer.from(await upstream.arrayBuffer());
    res.send(buf);
  } catch (err) {
    res.status(502).json({
      error: "Python backend unreachable",
      hint: `Start it manually: python -m uvicorn backend.main:app --port ${PY_PORT}`,
      detail: err.message,
    });
  }
});

// ---------- serve frontend ----------
app.use(express.static(path.join(__dirname, "frontend")));
// Express 5 has no "*" wildcard — use a fallback middleware instead
app.use((req, res) => {
  if (req.path.startsWith("/api")) return res.status(404).json({ error: "unknown api" });
  res.sendFile(path.join(__dirname, "frontend", "index.html"));
});

app.listen(WEB_PORT, () => {
  console.log(`\n  🎨 PixelQuote running!`);
  console.log(`  → Web (Node.js) : http://localhost:${WEB_PORT}`);
  console.log(`  → API (Python)  : http://localhost:${PY_PORT}/api/health\n`);
});

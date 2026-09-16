/* PixelQuote frontend — live Canvas preview + Python HD export via Node */
const $ = (id) => document.getElementById(id);
const canvas = $("canvas");
const ctx = canvas.getContext("2d");
// Python backend URL — local me direct, online (deploy) me PROD_API.
// DEPLOY KE BAAD: apna Render backend URL yahan daal, e.g. "https://pixelquote-api.onrender.com"
const PROD_API = "https://pixelquote-backend.onrender.com";
const LOCAL_API = "http://127.0.0.1:8000";
const API_DIRECT =
  location.hostname === "localhost" || location.hostname === "127.0.0.1" ? LOCAL_API : PROD_API;

const state = {
  theme: "Tech Dark",
  showAuthor: true,
  reviewed: false, // review diya → watermark OFF (backend me saved)
};

// fire-and-forget analytics → Python SQLite DB (direct, proxy fallback)
function track(event, meta) {
  const body = JSON.stringify({ visitor: ref.vid, event, meta: meta || {} });
  const opts = { method: "POST", headers: { "Content-Type": "application/json" }, body };
  fetch(`${API_DIRECT}/api/track`, opts).catch(() => fetch("/api/track", opts).catch(() => {}));
}

const THEME_STYLE = {
  // ---- FREE (6) ----
  "Tech Dark":     { g: ["#1e1b4b", "#6d28d9"], text: "#ffffff", sub: "#cbd5e1", accent: "#a78bfa", serif: false, frame: null, pro: false, tag: "purple/blue · sans", sw: "linear-gradient(180deg,#1e1b4b,#6d28d9)" },
  "Minimal Light": { solid: "#FAF9F6", text: "#111111", sub: "#646464", accent: "#111111", serif: true, frame: "light", pro: false, tag: "off-white · serif", sw: "#FAF9F6", swBorder: "#ddd" },
  "Ocean Depth":   { g: ["#0c4a6e", "#0e7490"], text: "#ffffff", sub: "#a5f3fc", accent: "#67e8f9", serif: false, frame: null, pro: false, tag: "navy/teal · cyan", sw: "linear-gradient(180deg,#0c4a6e,#0e7490)" },
  "Cream Paper":   { solid: "#f5efe0", text: "#3f3226", sub: "#8a7a63", accent: "#b45309", serif: true, frame: null, pro: false, tag: "cream · coffee serif", sw: "#f5efe0", swBorder: "#ddd" },
  "Charcoal":      { solid: "#1f2937", text: "#f9fafb", sub: "#9ca3af", accent: "#e5e7eb", serif: false, frame: null, pro: false, tag: "soft black · clean", sw: "#1f2937" },
  "Lavender Mist": { g: ["#ede9fe", "#c4b5fd"], text: "#2e1065", sub: "#6d28d9", accent: "#7c3aed", serif: false, frame: null, pro: false, tag: "lavender · purple", sw: "linear-gradient(180deg,#ede9fe,#c4b5fd)" },
  // ---- PRO (8) ----
  "Sunset Glow":   { g: ["#FF512F", "#DD2476"], text: "#ffffff", sub: "#ffe4e6", accent: "#ffffff", serif: false, frame: null, pro: true, tag: "orange/pink", sw: "linear-gradient(180deg,#FF512F,#DD2476)" },
  "Neon Matrix":   { solid: "#000000", text: "#ffffff", sub: "#39FF14", accent: "#39FF14", serif: false, frame: "neon", pro: true, tag: "black · neon green", sw: "#000000", swBorder: "#39FF14" },
  "Royal Gold":    { g: ["#0c0a09", "#451a03"], text: "#fef3c7", sub: "#d6a94f", accent: "#fbbf24", serif: true, frame: "accent", pro: true, tag: "black-gold · luxury", sw: "linear-gradient(180deg,#0c0a09,#b45309)" },
  "Forest Pine":   { g: ["#052e16", "#166534"], text: "#f0fdf4", sub: "#bbf7d0", accent: "#4ade80", serif: false, frame: null, pro: true, tag: "deep green · mint", sw: "linear-gradient(180deg,#052e16,#166534)" },
  "Crimson":       { g: ["#450a0a", "#b91c1c"], text: "#ffffff", sub: "#fecaca", accent: "#fca5a5", serif: true, frame: null, pro: true, tag: "maroon · bold serif", sw: "linear-gradient(180deg,#450a0a,#b91c1c)" },
  "Mono Ink":      { solid: "#ffffff", text: "#000000", sub: "#525252", accent: "#000000", serif: false, frame: "accent", pro: true, tag: "editorial · framed", sw: "#ffffff", swBorder: "#333" },
  "Midnight":      { solid: "#020617", text: "#e2e8f0", sub: "#38bdf8", accent: "#38bdf8", serif: false, frame: "accent", pro: true, tag: "black-blue · sky", sw: "#020617", swBorder: "#38bdf8" },
  "Peach Glow":    { g: ["#ffedd5", "#f9a8d4"], text: "#431407", sub: "#9a3412", accent: "#ea580c", serif: false, frame: null, pro: true, tag: "peach/pink · warm", sw: "linear-gradient(180deg,#ffedd5,#f9a8d4)" },
};

function hexRGB(h) {
  const n = parseInt(h.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
function mix(a, b, t) {
  const A = hexRGB(a), B = hexRGB(b);
  return `rgb(${Math.round(A[0]+(B[0]-A[0])*t)},${Math.round(A[1]+(B[1]-A[1])*t)},${Math.round(A[2]+(B[2]-A[2])*t)})`;
}

function wrapText(text, font, maxW) {
  const words = text.split(/\s+/).filter(Boolean);
  const lines = [];
  let cur = "";
  for (const w of words) {
    const trial = (cur + " " + w).trim();
    if (ctx.measureText(trial).width <= maxW || !cur) {
      // hard-break single huge word
      if (ctx.measureText(trial).width > maxW && trial.length > 12) {
        if (cur) lines.push(cur);
        let rest = w;
        cur = "";
        while (rest && ctx.measureText(rest).width > maxW) {
          let cut = rest.length - 1;
          while (cut > 1 && ctx.measureText(rest.slice(0, cut) + "-").width > maxW) cut--;
          lines.push(rest.slice(0, cut) + "-");
          rest = rest.slice(cut);
        }
        cur = rest;
      } else cur = trial;
    } else { lines.push(cur); cur = w; }
  }
  if (cur) lines.push(cur);
  return lines.length ? lines : [""];
}

function render() {
  const S = 1080;
  const text = $("textInput").value;
  const author = $("authorName").value;
  const handle = $("handle").value;
  let fontSize = parseInt($("fontSize").value, 10);
  const T = THEME_STYLE[state.theme];

  // --- background ---
  if (T.g) {
    for (let y = 0; y < S; y += 4) {
      ctx.fillStyle = mix(T.g[0], T.g[1], y / S);
      ctx.fillRect(0, y, S, 4);
    }
    // soft glow orbs
    const glow = (x, y, r, a) => {
      const g = ctx.createRadialGradient(x, y, 0, x, y, r);
      g.addColorStop(0, `rgba(255,255,255,${a})`);
      g.addColorStop(1, "rgba(255,255,255,0)");
      ctx.fillStyle = g; ctx.fillRect(0, 0, S, S);
    };
    glow(S * 0.1, S * 0.1, S * 0.5, 0.10);
    glow(S * 0.9, S * 0.9, S * 0.5, 0.10);
  } else {
    ctx.fillStyle = T.solid;
    ctx.fillRect(0, 0, S, S);
  }

  // --- frames (neon double / light thin / accent inset) ---
  if (T.frame === "neon") {
    ctx.strokeStyle = T.accent; ctx.lineWidth = 10;
    ctx.beginPath(); ctx.roundRect(36, 36, S - 72, S - 72, 28); ctx.stroke();
    ctx.lineWidth = 3;
    ctx.beginPath(); ctx.roundRect(58, 58, S - 116, S - 116, 20); ctx.stroke();
  } else if (T.frame === "light") {
    ctx.strokeStyle = "#e1e1e1"; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.roundRect(36, 36, S - 72, S - 72, 24); ctx.stroke();
  } else if (T.frame === "accent") {
    ctx.strokeStyle = T.accent; ctx.lineWidth = 5;
    ctx.beginPath(); ctx.roundRect(48, 48, S - 96, S - 96, 20); ctx.stroke();
  }

  const fam = T.serif ? "Georgia,'Playfair Display',serif" : "Inter,Arial,sans-serif";

  // --- decorative quote ---
  ctx.fillStyle = T.accent;
  ctx.font = `700 180px Georgia,serif`;
  ctx.textAlign = "center";
  ctx.fillText("\u201c", S / 2, 300);

  // --- main text ---
  const maxW = S - 240;
  const display = text.trim() || "Your words, beautifully styled.";
  ctx.font = `800 ${fontSize}px ${fam}`;
  let lines = wrapText(display, ctx.font, maxW);
  const lh = fontSize * 1.28;
  while (lines.length * lh > 560 && fontSize > 32) {
    fontSize -= 4;
    ctx.font = `800 ${fontSize}px ${fam}`;
    lines = wrapText(display, ctx.font, maxW);
  }
  const blockH = lines.length * lh;
  let y = 500 - blockH / 2 + lh * 0.38;
  ctx.fillStyle = T.text;
  ctx.font = `800 ${fontSize}px ${fam}`;
  for (const ln of lines) { ctx.fillText(ln, S / 2, y); y += lh; }

  // --- author ---
  if (state.showAuthor && (author.trim() || handle.trim())) {
    let ay = 500 + blockH / 2 + 60;
    ctx.fillStyle = T.accent;
    const bw = 80;
    ctx.beginPath(); ctx.roundRect(S / 2 - bw / 2, ay, bw, 6, 3); ctx.fill();
    ay += 58;
    if (author.trim()) {
      ctx.fillStyle = T.text;
      ctx.font = `700 44px Inter,Arial,sans-serif`;
      ctx.fillText(author.trim(), S / 2, ay);
      ay += 56;
    }
    if (handle.trim()) {
      let h = handle.trim();
      if (!h.startsWith("@")) h = "@" + h;
      ctx.fillStyle = T.sub;
      ctx.font = `400 38px Inter,Arial,sans-serif`;
      ctx.fillText(h, S / 2, ay);
    }
  }

  // --- watermark (free plan; review dene ke baad OFF) ---
  if (!state.reviewed) {
    ctx.fillStyle = T.sub;
    ctx.font = `400 28px Inter,Arial,sans-serif`;
    ctx.textAlign = "right";
    ctx.fillText("Made with PixelQuote", S - 60, S - 52);
    ctx.textAlign = "center";
  }

  // --- UI sync ---
  $("charCount").textContent = text.length;
  $("charFill").style.width = (text.length / 280 * 100) + "%";
  $("fontVal").textContent = $("fontSize").value + "px";
  $("activeTheme").textContent = state.theme;
}

// ---------- events ----------
$("textInput").addEventListener("input", render);
$("authorName").addEventListener("input", render);
$("handle").addEventListener("input", render);
$("fontSize").addEventListener("input", render);

$("authorToggle").addEventListener("click", () => {
  state.showAuthor = !state.showAuthor;
  $("authorToggle").classList.toggle("on", state.showAuthor);
  $("authorToggle").setAttribute("aria-checked", state.showAuthor);
  $("authorFields").style.display = state.showAuthor ? "grid" : "none";
  render();
});

// ---------- referral unlock (free Pro, no paid APIs) ----------
let PRO_THEMES = Object.keys(THEME_STYLE).filter((n) => THEME_STYLE[n].pro);
const NEEDED = 1; // sirf 1 dost kaafi hai
const ref = {
  code: localStorage.getItem("pq_ref") || "",
  vid: localStorage.getItem("pq_vid") || "",
  unlocked: JSON.parse(localStorage.getItem("pq_unlocked") || "[]"),
  unlockedAll: localStorage.getItem("pq_unlocked_all") === "1",
  pending: null, poll: null,
};
function markAllUnlocked(list) {
  ref.unlockedAll = true;
  ref.unlocked = list && list.length ? list : PRO_THEMES.slice();
  localStorage.setItem("pq_unlocked_all", "1");
  localStorage.setItem("pq_unlocked", JSON.stringify(ref.unlocked));
  paintThemes();
}
if (!ref.vid) {
  ref.vid = (crypto.randomUUID ? crypto.randomUUID() : "v-" + Date.now() + "-" + Math.random().toString(16).slice(2));
  localStorage.setItem("pq_vid", ref.vid);
}
async function apiJSON(url, opts) {
  const r = await fetch(url, opts);
  if (!r.ok) throw new Error("http " + r.status);
  return r.json();
}
async function refCall(path, body) {
  const opts = body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : undefined;
  try { return await apiJSON(`${API_DIRECT}${path}`, opts); }
  catch { return await apiJSON(path, opts); } // Node proxy fallback
}
async function ensureCode() {
  if (ref.code) return ref.code;
  try {
    const d = await refCall("/api/referral/new", { visitor: ref.vid });
    ref.code = d.code;
    localStorage.setItem("pq_ref", ref.code);
  } catch {}
  return ref.code;
}
function myLink() { return location.origin + location.pathname + "?ref=" + ref.code; }
function isUnlocked(name) { return !PRO_THEMES.includes(name) || ref.unlockedAll || ref.unlocked.includes(name); }
function paintThemes() {
  document.querySelectorAll("#themeGrid .theme").forEach((b) => {
    const name = b.dataset.theme;
    if (PRO_THEMES.includes(name) && (ref.unlockedAll || ref.unlocked.includes(name))) {
      b.classList.remove("pro");
      const badge = b.querySelector(".pro-badge");
      if (badge) { badge.textContent = "✓ Unlocked"; badge.style.background = "#34d399"; }
    }
    b.classList.toggle("selected", state.theme === name);
  });
}
async function syncUnlocked() {
  if (!ref.code) return;
  try {
    const s = await refCall("/api/referral/" + ref.code);
    ref.unlocked = s.unlocked || [];
    localStorage.setItem("pq_unlocked", JSON.stringify(ref.unlocked));
    if (ref.unlocked.length >= PRO_THEMES.length && PRO_THEMES.length) markAllUnlocked(ref.unlocked);
    paintThemes();
  } catch {}
}
function openRefModal(name) {
  ref.pending = name;
  $("proThemeName").textContent = name;
  $("refLink").value = ref.code ? myLink() : "link ban raha hai…";
  $("refCount").textContent = `0/${NEEDED}`;
  $("refFill").style.width = "0%";
  $("proModal").hidden = false;
  refreshProgress();
  clearInterval(ref.poll);
  ref.poll = setInterval(refreshProgress, 3000);
}
async function refreshProgress() {
  if (!ref.code || !ref.pending) return;
  try {
    const s = await refCall("/api/referral/" + ref.code);
    const n = Math.min(s.visits, NEEDED);
    $("refCount").textContent = `${n}/${NEEDED}`;
    $("refFill").style.width = (n / NEEDED * 100) + "%";
    if (s.visits >= NEEDED) {
      let list = [];
      try {
        const u = await refCall("/api/referral/unlock", { code: ref.code, theme: ref.pending });
        list = u.unlocked || [];
      } catch {}
      const done = ref.pending;
      markAllUnlocked(list);
      state.theme = done;
      paintThemes(); render();
      closeRefModal();
      setTimeout(() => alert("🎉 SAARE 8 Pro styles unlock ho gaye! Ab sab hamesha free rahenge."), 300);
    }
  } catch {}
}
function closeRefModal() { $("proModal").hidden = true; clearInterval(ref.poll); }

// theme grid builds dynamically from Python API (source of truth for Pro flags)
async function loadThemeGrid() {
  let order = Object.keys(THEME_STYLE);
  const proMap = {};
  order.forEach((n) => (proMap[n] = !!THEME_STYLE[n].pro));
  try {
    const t = await refCall("/api/themes"); // {name: {description, pro}}
    const apiOrder = Object.keys(t).filter((n) => THEME_STYLE[n]);
    if (apiOrder.length) {
      order = apiOrder;
      order.forEach((n) => (proMap[n] = !!t[n].pro));
    }
  } catch {}
  PRO_THEMES = order.filter((n) => proMap[n]);
  const grid = $("themeGrid");
  grid.innerHTML = "";
  order.forEach((name) => {
    const m = THEME_STYLE[name] || {};
    const b = document.createElement("button");
    b.className = "theme" + (proMap[name] ? " pro" : "") + (state.theme === name ? " selected" : "");
    b.dataset.theme = name;
    b.innerHTML = `<span class="sw" style="background:${m.sw || "#333"}${m.swBorder ? ";border:2px solid " + m.swBorder : ""}"></span>${name} ${proMap[name] ? '<em class="pro-badge">🔒 Pro</em>' : ""}<small>${m.tag || ""}</small>`;
    b.addEventListener("click", () => onThemeClick(name));
    grid.appendChild(b);
  });
  paintThemes();
}
async function onThemeClick(name) {
  if (!isUnlocked(name)) {
    await ensureCode();
    if (ref.code) $("refLink").value = myLink();
    openRefModal(name);
    return;
  }
  state.theme = name;
  paintThemes();
  render();
  track("theme_select", { theme: name });
}
$("copyRef").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText($("refLink").value); } catch {}
  $("copyRef").textContent = "Copied ✓";
  setTimeout(() => ($("copyRef").textContent = "Copy link"), 1200);
});
$("waShare").addEventListener("click", () => {
  const msg = `Bro ye app try kar — text se Instagram-ready photo banta hai, free! 👇\n${myLink()}`;
  window.open("https://wa.me/?text=" + encodeURIComponent(msg), "_blank");
});
$("followedBtn").addEventListener("click", async () => {
  const btn = $("followedBtn");
  btn.disabled = true; btn.textContent = "Checking…";
  try {
    const u = await refCall("/api/social/unlock", { visitor: ref.vid });
    markAllUnlocked(u.unlocked);
    track("social_unlock", { method: "twitter" });
    if (ref.pending) state.theme = ref.pending;
    paintThemes(); render();
    closeRefModal();
    setTimeout(() => alert("🎉 SAARE 8 Pro styles unlock ho gaye! Thanks for following!"), 300);
  } catch {
    alert("Unlock nahi ho paya — app chal rahi hai na? Phir try karo.");
  } finally {
    btn.disabled = false; btn.textContent = "I Followed ✅";
  }
});
$("proClose").addEventListener("click", closeRefModal);
$("proModal").addEventListener("click", (e) => { if (e.target.id === "proModal") closeRefModal(); });

// ---------- review → watermark OFF (naam + stars only) ----------
let revStars = 0;
function paintStars() {
  document.querySelectorAll("#revStars button").forEach((b) => {
    b.classList.toggle("lit", parseInt(b.dataset.s, 10) <= revStars);
  });
}
document.querySelectorAll("#revStars button").forEach((b) => {
  b.addEventListener("click", () => { revStars = parseInt(b.dataset.s, 10); paintStars(); });
});
function refreshReviewUI() {
  const btn = $("rmWmBtn");
  if (state.reviewed) {
    btn.textContent = "✓ Watermark OFF — enjoy! 🎉";
    btn.classList.add("off");
  } else {
    btn.textContent = "✨ Remove watermark FREE — 1 click!";
    btn.classList.remove("off");
  }
}
$("rmWmBtn").addEventListener("click", () => {
  if (state.reviewed) return;
  revStars = 0; paintStars();
  $("revName").value = "";
  $("reviewModal").hidden = false;
});
$("revClose").addEventListener("click", () => ($("reviewModal").hidden = true));
$("reviewModal").addEventListener("click", (e) => { if (e.target.id === "reviewModal") e.target.hidden = true; });
$("revSubmit").addEventListener("click", async () => {
  const name = $("revName").value.trim();
  if (name.length < 2) { alert("Apna naam likho (kam se kam 2 letters 🙂)"); return; }
  if (!revStars) { alert("Stars to do! ⭐"); return; }
  const btn = $("revSubmit");
  btn.disabled = true; btn.textContent = "Saving…";
  try {
    await refCall("/api/review", { visitor: ref.vid, name, stars: revStars });
    state.reviewed = true;
    track("review", { stars: revStars });
    refreshReviewUI(); render();
    $("reviewModal").hidden = true;
    setTimeout(() => alert(`Thanks ${name}! 🙏 Watermark hamesha ke liye OFF.`), 300);
  } catch {
    alert("Save nahi ho paya — app chal rahi hai na? Phir try karo.");
  } finally {
    btn.disabled = false; btn.textContent = "Submit & Remove watermark ✅";
  }
});
async function checkReviewStatus() {
  try {
    const s = await refCall("/api/status/" + ref.vid);
    state.reviewed = !!s.reviewed;
    if (s.pro_unlocked) markAllUnlocked(s.unlocked);
  } catch {}
  refreshReviewUI(); render();
}

// init: my code + count visit if I came from a friend's link + sync unlocks
(async () => {
  await ensureCode();
  track("page_view", {});
  await loadThemeGrid();
  await checkReviewStatus();
  const q = (new URLSearchParams(location.search).get("ref") || "").toUpperCase();
  if (q && q !== (ref.code || "").toUpperCase() && !localStorage.getItem("visited_" + q)) {
    try {
      await refCall("/api/referral/visit", { code: q, visitor: ref.vid });
      localStorage.setItem("visited_" + q, "1");
      setTimeout(() => alert("🎉 Dost ke link se aaye ho — welcome!"), 800);
    } catch {}
  }
  await syncUnlocked();
  paintThemes();
})();

$("copyBtn").addEventListener("click", async () => {
  await navigator.clipboard.writeText($("textInput").value);
  $("copyBtn").textContent = "Copied ✓";
  setTimeout(() => ($("copyBtn").textContent = "Copy text"), 1200);
});

// HD download → Python backend DIRECT (fast, no proxy hop),
// fallback to Node proxy, fallback to browser canvas
async function postPNG(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("backend " + res.status);
  return await res.blob();
}
function saveBlob(blob, name) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}
$("downloadBtn").addEventListener("click", async () => {
  const btn = $("downloadBtn");
  btn.disabled = true;
  btn.textContent = "⏳ Rendering HD…";
  const payload = {
    text: $("textInput").value.slice(0, 280),
    author_name: $("authorName").value,
    handle: $("handle").value,
    show_author: state.showAuthor,
    theme_name: state.theme,
    font_size: parseInt($("fontSize").value, 10),
    visitor: ref.vid,
  };
  const fname = `pixelquote-${state.theme.toLowerCase().replace(/\s+/g, "-")}-1080x1080.png`;
  try {
    saveBlob(await postPNG(`${API_DIRECT}/api/generate`, payload), fname);
    $("dlHint").textContent = state.reviewed
      ? "✅ HD PNG exported — no watermark, enjoy! 🎉"
      : "✅ HD PNG exported from Python (Pillow) at full 1080p.";
    track("download", { theme: state.theme, chars: payload.text.length, author: state.showAuthor });
  } catch (err1) {
    try {
      saveBlob(await postPNG("/api/generate", payload), fname);
      $("dlHint").textContent = "✅ HD PNG exported from Python (Pillow) at full 1080p.";
      track("download", { theme: state.theme, chars: payload.text.length, author: state.showAuthor });
    } catch (err2) {
      // offline fallback: browser canvas PNG
      const a = document.createElement("a");
      a.href = canvas.toDataURL("image/png");
      a.download = "pixelquote-preview-1080x1080.png";
      a.click();
      $("dlHint").textContent = "⚠️ Python backend unreachable — downloaded browser preview instead. Is the app running? (npm start)";
    }
  } finally {
    btn.disabled = false;
    btn.textContent = "⬇️ Download Image (.png)";
  }
});

// backend status dot (direct Python first, then Node proxy)
(async () => {
  for (const u of [`${API_DIRECT}/api/health`, "/api/health"]) {
    try {
      const r = await fetch(u, { cache: "no-store" });
      if (r.ok) {
        $("apiStatus").textContent = "● Python connected";
        $("apiStatus").classList.add("ok");
        return;
      }
    } catch {}
  }
  $("apiStatus").textContent = "● preview-only mode";
})();

render();

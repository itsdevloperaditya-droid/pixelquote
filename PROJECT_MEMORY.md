# PixelQuote — Project Memory (naye chat ke liye padho)

> Ye file isliye hai taaki OpenCode ka naya session (bina purani history ke)
> turant samajh jaye ye project kya hai. Pehle ye file padho, phir kaam shuru karo.

## Kya hai ye
Text-to-Graphic Generator Micro-SaaS ("PixelQuote"). User text likhta hai →
14 styled quote cards (1080x1080 PNG, Instagram/LinkedIn/X ready). Zero-cost stack,
koi paid AI image API nahi — rendering khud ke code se (Pillow + Canvas).

## Owner
17-yr-old solo builder. No payment gateway (no KYC/bank). Monetization = free +
referral-unlock + review-unlock + email-less waitlist style growth. Hinglish me baat karo.

## Architecture
- `frontend/` — static site (index.html, styles.css, app.js, admin.html). Live preview
  browser Canvas pe, HD download Python backend se. API base URL: local me
  `http://127.0.0.1:8000`, online me `PROD_API` constant (app.js + admin.html me).
- `backend/` — FastAPI + Pillow. `generator.py` = 14 themes renderer,
  `main.py` = API routes. SQLite DB `backend/data/app.db` (events + reviews),
  referrals JSON `backend/data/referrals.json`.
- `server.js` — SIRF local dev ke liye (Node static serve + Python auto-start).
  Online iski zaroorat nahi.
- `app.py` — purana Streamlit demo (legacy, 4 themes). Asli app webapp hai.

## Features (done)
14 themes (6 free: Tech Dark, Minimal Light, Ocean Depth, Cream Paper, Charcoal,
Lavender Mist / 8 Pro: Sunset Glow, Neon Matrix, Royal Gold, Forest Pine, Crimson,
Mono Ink, Midnight, Peach Glow). Theme grid `/api/themes` se dynamic banta hai.
Pro unlock = KOI 1 task → SAARE 8 Pro unlock (not single theme). Task A: referral
(?ref=CODE, 1 unique visit kaafi, backend count, REFS_NEEDED=1). Task B: X follow
button (x.com/devcoderaditya) + "I Followed" honor-system (X API paid hai, free
verify impossible). Unlocks permanent: `unlocks` table (visitor PK) + referral
code record. Status API batata hai pro_unlocked.
Analytics: POST /api/track (page_view/theme_select/download/review). Owner stats:
GET /api/stats (password protected) + `frontend/admin.html` (lock screen).

## Deploy (LIVE)
- Backend (Render Web Service, free): https://pixelquote-backend.onrender.com
- Frontend (Render Static Site, free): https://pixelquote.onrender.com
- GitHub: https://github.com/itsdevloperaditya-droid/pixelquote (branch: main)
- Render auto-deploy on `git push`. Free cold start ~1 min. Free disk ephemeral
  hai → restart/redeploy pe SQLite+referrals WIPE ho sakte hain (upgrade: Supabase/Neon).

## Secrets (KABHI code/git me mat likhna)
- `ADMIN_PASSWORD` env var: user ke PC pe setx se + Render dashboard Environment me.
  Password user se chat me mat mangna dobara — unke paas hai.
- Ye file public GitHub pe jati hai → isme password KABHI mat likhna.

## Local run
`npm start` → http://localhost:8080 (Node Python auto-start karta hai).
Ports: web 8080 (3000 pe user ka dusra project hai!), Python 8000.

## Pending ideas
Free Postgres (data permanence), admin password rotation before public sharing,
naye themes (palette + THEMES dict + THEME_STYLE + contact-sheet QA),
Streamlit app.py sync (optional).

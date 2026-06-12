# FinSignal — MBA Finance Daily Digest Portal

> **A fully-automated, 100 % free daily financial news portal powered by the Gemini AI API, GitHub Actions, and GitHub Pages.**

---

## 🗂 Project Structure

```
.
├── .github/
│   └── workflows/
│       └── daily_digest.yml     # CI/CD — triggers on PDF push
├── public/
│   ├── index.html               # Bloomberg-style frontend
│   └── digests/
│       └── digest-YYYY-MM-DD.md # Auto-generated Markdown files
├── raw_papers/                  # Drop your daily newspaper PDF here
├── analyze_news.py              # AI analysis script
├── requirements.txt
└── README.md
```

---

## 🚀 One-Time Setup

### Step 1 — Create a GitHub Repository

1. Go to [github.com/new](https://github.com/new) and create a **new public repository**.
2. Push this entire project folder to that repository:

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
   git push -u origin main
   ```

---

### Step 2 — Add the Gemini API Key as a Repository Secret

The workflow reads `GEMINI_API_KEY` from your repo's **encrypted secrets**.

1. Open your repository on GitHub.
2. Click **Settings** → **Secrets and variables** → **Actions**.
3. Click **"New repository secret"**.
4. Set:
   - **Name:** `GEMINI_API_KEY`
   - **Value:** Your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
5. Click **"Add secret"**.

> **Where to get a free API key?**  
> Visit [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey), sign in with a Google account, and click **"Create API key"**. The free tier is sufficient for this project.

---

### Step 3 — Enable GitHub Pages from `/public`

1. Go to **Settings** → **Pages** (in your GitHub repo).
2. Under **"Build and deployment"**:
   - **Source:** `GitHub Actions` *(the workflow handles deployment automatically)*
3. Click **Save**.

Your site will be live at:
```
https://<YOUR_USERNAME>.github.io/<YOUR_REPO>/
```

---

### Step 4 — Enable Workflow Permissions

The workflow commits the generated digest back to the repo. Allow this:

1. Go to **Settings** → **Actions** → **General**.
2. Scroll to **"Workflow permissions"**.
3. Select **"Read and write permissions"**.
4. Click **Save**.

---

## 📰 Daily Usage — Generating a Digest

1. Download today's financial newspaper as a **PDF** (e.g., Economic Times, Financial Times, Mint).
2. Rename it anything (e.g., `ET-2024-06-12.pdf`).
3. Drop it into the `/raw_papers/` folder.
4. **Commit and push** to the `main` branch:

   ```bash
   git add raw_papers/ET-2024-06-12.pdf
   git commit -m "Add newspaper for 2024-06-12"
   git push
   ```

5. GitHub Actions will automatically:
   - Upload the PDF to the Gemini Files API.
   - Run `gemini-1.5-flash` with the MBA finance system prompt.
   - Save the output as `public/digests/digest-YYYY-MM-DD.md`.
   - Commit the file back to the repo.
   - Deploy the updated site to GitHub Pages.

6. In ~2–3 minutes, your site is updated!

---

## 🧠 AI Prompt Design

The script instructs Gemini to produce four structured sections for every newspaper:

| # | Section | What it covers |
|---|---------|---------------|
| 1 | **Macroeconomic Context & Policy Updates** | Central bank actions, CPI, GDP, fiscal policy |
| 2 | **Equity Markets & Corporate Actions** | Stock movements, IPOs, M&A, earnings surprises |
| 3 | **Commodities & Global Trends** | Physical Gold, Silver, Crude Oil, LNG, supply chains |
| 4 | **Academic Application & Financial Concepts** | MBA-level theory: DCF, Arbitrage, Technical Analysis, etc. |

---

## 🔧 Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key (PowerShell)
$env:GEMINI_API_KEY = "YOUR_KEY_HERE"

# Drop a PDF in /raw_papers/ and run
python analyze_news.py
```

The digest will appear at `public/digests/digest-YYYY-MM-DD.md`.

---

## Notes

- **Only the most recently modified PDF** in `/raw_papers/` is processed on each run.
- Uploaded PDFs are **automatically deleted** from Gemini's servers after processing.
- The **Gemini free tier** allows ~1 500 requests/day — more than enough for one digest per day.
- Ticker data on the frontend is **static / decorative**. For live prices, integrate a free API like Yahoo Finance or NSE Python.

---

## License

MIT — free to use, modify, and distribute.

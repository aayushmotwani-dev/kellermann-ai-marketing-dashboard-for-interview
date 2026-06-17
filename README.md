# Kellermann — AI Social Media Command Center

A social media analytics dashboard built for **Kellermann GmbH**, a premium German motorcycle LED indicator brand. Tracks campaign performance, compares AI-generated vs human-written caption effectiveness, and surfaces content recommendations — all inside a dark-themed Streamlit UI.

> Built as part of my application for the Online Marketing Werkstudent role at Kellermann.

---

## What It Does

The dashboard ingests a structured social media dataset (180 posts across Instagram, TikTok, and YouTube, Jan–Jun 2024) and gives you four views:

**01 · Performance**
- KPI strip: total views, total engagements, average engagement rate, posts analyzed
- Weekly views over time, broken down by platform
- Platform bubble chart: reach vs. engagement rate vs. post volume
- Engagement type split (Likes / Comments / Shares / Saves)
- Campaign-type performance bar chart with engagement rate color encoding
- Auto-generated insight text that adapts to the filtered data

**02 · Content & AI**
- Direct comparison of AI-generated captions vs human-written ones (avg engagement rate)
- Post format breakdown: Image, Reel, Story, Video — ranked by engagement
- AI Caption × Post Format heatmap to find the highest-performing combinations
- Recommendations that update based on what the data shows

**03 · Products**
- Per-product reach and engagement rate across all 8 Kellermann indicator lines (Atto® DF, Blisk, Jetstream®, Bullet 1000®, Dayron®, BL 1000, Rhombus S, micro S)
- Views vs. ER bubble chart (bubble size = post count)
- Automated callouts for best reach product vs. best engagement product

**04 · Raw Data**
- Full filtered table sorted by total engagements
- CSV export button for the current filter state

**Sidebar filters** apply across all tabs: Platform, Product, Campaign Type, and Date Range.

---

## Stack

| Layer | Tool |
|---|---|
| Language | Python 3.9+ |
| UI / Server | Streamlit |
| Data | Pandas |
| Charts | Plotly (Express + Graph Objects) |
| Styling | Custom CSS injected via `st.markdown` (DM Mono + Syne fonts) |

No external API calls. No database. Runs entirely from a single CSV file.

---

## Dataset

`kellermann_data.csv` — 180 simulated posts, Jan 2024 to Jun 2024.

| Field | Values |
|---|---|
| Platform | Instagram, TikTok, YouTube |
| Product | Atto® DF, Blisk, Jetstream®, Bullet 1000®, Dayron®, BL 1000, Rhombus S, micro S |
| Post Type | Image, Reel, Story, Video |
| Campaign | Brand Story, Collab, Community, Product Launch, Seasonal Sale, Tutorial |
| Metrics | Views, Likes, Comments, Shares, Saves |
| AI Caption | Yes / No |

All data is simulated for demo purposes.

---

## Running It

**Requirements:** Python 3.9+

```bash
# 1. Clone
git clone https://github.com/aayushmotwani-dev/kellermann-ai-marketing-dashboard-for-interview.git
cd kellermann-ai-marketing-dashboard-for-interview

# 2. (Optional but recommended) virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install
pip install -r requirements.txt

# 4. Run
streamlit run app.py
```

Opens at `http://localhost:8501`. The CSV file must stay in the same folder as `app.py`.

---

## Project Structure

```
kellermann-ai-marketing-dashboard-for-interview/
├── app.py                  # Full dashboard — UI, logic, charts
├── kellermann_data.csv     # Simulated post dataset
├── requirements.txt        # streamlit, pandas, plotly
└── README.md
```

---

## Context

Kellermann GmbH makes high-end motorcycle LED indicators sold across Europe. The challenge this dashboard addresses: as a small marketing team, how do you quickly identify which platforms, products, post formats, and caption strategies are actually worth doubling down on — without digging through spreadsheets?

The goal was to build something that could realistically sit in a weekly marketing review and give clear, actionable answers without requiring a data analyst.

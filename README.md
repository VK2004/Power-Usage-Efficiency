# ⚡ PUE Optimizer

A Streamlit app to calculate, benchmark, and optimize your data center's **Power Usage Effectiveness (PUE)** — with an AI agent powered by Claude.

## Live Demo
Deploy via [Streamlit Cloud](https://share.streamlit.io)

## Features
- **Input table** — enter IT load, cooling, power losses, and lighting in kW
- **PUE Calculator** — instant PUE, total facility power, overhead breakdown
- **Industry Benchmark** — compare vs Google (1.09), Meta (1.08), industry avg (1.56)
- **Scenario Comparison** — Inefficient / Standard / Hyperscale presets
- **AI Agent** — autonomous tool-calling agent that diagnoses your facility, estimates ROI, and produces a prioritised improvement roadmap

## Setup

### Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Deploy to Streamlit Cloud
1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set main file to `app.py`
4. Deploy — no secrets needed (users enter their own Anthropic API key in the UI)

## Repo Structure
```
├── app.py                   # Main Streamlit app
├── requirements.txt         # Python dependencies
├── .streamlit/
│   └── config.toml          # Dark theme config
├── .gitignore               # Excludes secrets.toml and cache
└── README.md
```

## Usage
1. Enter your facility's power values in the input table
2. Optionally enter an Anthropic API key for AI recommendations
3. Click **Generate the Report**

> ⚠️ Recommendations are heuristic estimates. Validate with facility engineers before investment.

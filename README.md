# 🛡️ MicroQuery: Production-Hardened AI Data Assistant

Transform your PostgreSQL database into an intelligent, conversational analytics dashboard. Powered by local LLMs (Ollama) and high-fidelity visualizations.

## 🚀 Key Features

### ⚡ Enterprise-Grade Engine

- **Intelligent Schema Pruning**: Automatically identifies relevant tables for complex questions, reducing AI context by up to 90%.
- **SQL Caching**: Instantaneous (0ms) responses for repeated questions via an in-memory SQL cache.
- **Hyper-Scale Ready**: Tested against schemas with 9+ tables and 25,000+ records (Customers, Orders, Reviews, etc.).

### 🛡️ Professional UI/UX

- **Interactive SQL Sandbox**: Toggle "Review Mode" to inspect and edit AI-generated SQL before execution.
- **Multi-Model Support**: Hot-swap between local models (`phi3.5:latest`, `llama3.1:latest`, `mistral`, `gemma2`) on the fly.
- **Data Export**: One-click "Download as CSV" for all query results.

### 📊 Advanced Visualizations
- **High-Fidelity Charts**: Powered by **Plotly** for interactive, beautiful visuals.
  - **Composition**: Pie and Donut charts for market share and distribution.
  - **Correlation**: Automatic Heatmaps to find relationships between numeric metrics.
  - **Comparison**: Overlaid Bar and Line charts for trend analysis.
- **Export Gallery**: Every chart features a **"Download as PNG"** button for easy insertion into reports and presentations.
- **Smart Insights**: AI-powered proactive analysis accompanying every visualization.

---

## 🛠️ Quick Start

### 1. Prerequisites

- [Ollama](https://ollama.ai/) installed and running.
- PostgreSQL database accessible.

### 2. Setup

```bash
# Clone and enter directory
cd MicroQuery

# Install dependencies
python3 -m pip install -r requirements.txt --break-system-packages

# Setup the Hyper-Scale database (Seeds 25k+ records)
python3 setup_real_db.py
```

### 3. Run the App

```bash
streamlit run pg_bot.py
```

## 🧠 Architecture

- **Front-end**: Streamlit (Premium Custom CSS)
- **AI Orchestration**: Custom Micromodel Engine (Schema-Aware)
- **Local Inference**: Ollama API
- **Visuals**: Plotly Express & Streamlit Native Charts

---

Amit Prakash ❤️ for private, specialized database intelligence.

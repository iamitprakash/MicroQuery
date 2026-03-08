# 🛡️ MicroQuery: Production-Hardened AI Data Assistant

Transform your PostgreSQL database into an intelligent, conversational analytics dashboard. Powered by local LLMs (Ollama) and high-fidelity visualizations.

## 🚀 Key Features

### ⚡ Enterprise-Grade Engine

- **Persistent SQL Caching**: AI "remembers" successful queries in a local **SQLite** database (`query_cache.db`), making repeat questions instant.
- **Human-in-the-Loop Learning**: If you edit SQL in **Review Mode**, the system saves your correction to the cache, effectively "learning" from your expertise.
- **Intelligent Schema Pruning**: Automatically identifies relevant tables for complex questions, reducing AI context by up to 90%.
- **Hyper-Scale Ready**: Tested against schemas with 9+ tables and 25,000+ records.

### 🛡️ Professional UI & Analytics

- **🔍 Interactive Drill-Downs**: Use sidebar multiselect filters to live-filter charts and tables simultaneously.
- **Interactive SQL Sandbox**: Toggle "Review Mode" to inspect and edit AI-generated SQL before execution.
- **Multi-Model Support**: Hot-swap between local models (`phi3.5`, `llama3.1`, etc.) on the fly.
- **🛡️ System Explorer**: Expand the footer to peer into the AI's "memory" (cache history and feedback).

### 📊 Advanced Visualizations
- **High-Fidelity Charts**: Powered by **Plotly** for interactive, beautiful visuals.
  - **Composition**: Pie and Donut charts for market share and distribution.
  - **Correlation**: Automatic Heatmaps to find relationships between numeric metrics.
  - **Comparison**: Overlaid Bar and Line charts for trend analysis.
- **Export Gallery**: Every chart features a **"Download as PNG"** button. The main result can be exported via **"Download Filtered CSV"**.

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

### 3. Deployment via Docker (Recommended)
```bash
# Start the entire stack (App + PostgreSQL)
docker-compose up --build -d
```
The app will be available at `http://localhost:8501`.

### 4. Manual Local Run
```bash
# 1. Start your local Ollama if not running
# 2. Run the dashboard
streamlit run pg_bot.py
```

## 🧠 Architecture

- **Front-end**: Streamlit (Premium Custom CSS)
- **AI Orchestration**: Custom Micromodel Engine (Schema-Aware)
- **Local Inference**: Ollama API
- **Visuals**: Plotly Express & Streamlit Native Charts

---

Amit Prakash ❤️ for private, specialized database intelligence.

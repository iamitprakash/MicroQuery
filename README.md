# MicroQuery 🤖🐘

**MicroQuery** is a specialized, privacy-first conversational AI chatbot that lets you query your **PostgreSQL** database using a local, custom **Micromodel**.

By running entirely on your machine (via Ollama) and using a cost-optimized CPU-only approach, MicroQuery ensures your data schema and queries never leave your local environment.

## ✨ Features

- **Privacy-First**: No data is sent to external AI APIs. Everything runs locally.
- **Micromodel Engine**: Uses a specialized, quantized model (Phi-3.5) optimized for SQL generation.
- **Dynamic Schema Training**: Automatically "teaches" the local model about your PostgreSQL tables and relationships.
- **Cost-Effective**: Designed to run efficiently on low-cost hardware like Amazon EC2 `t3.large`.
- **Sleek UI**: Clean, interactive Streamlit dashboard for chatting with your data.

## 🚀 Quick Start (Local Testing)

Follow these steps to see MicroQuery in action immediately using a mock database.

### 1. Prerequisites

- **Ollama**: [Download and Install Ollama](https://ollama.com/).
- **Python**: Version 3.10 or higher.
- **PostgreSQL**: (Optional for initial testing) Running on your local machine.

### 2. Setup Environment

```bash
# Clone the repository
git clone https://github.com/iamitprakash/MicroQuery.git
cd MicroQuery

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize Mock Data

I've included a script to create a sample SQLite database so you can test the AI logic instantly without configuring PostgreSQL.

```bash
python3 create_mock_db.py
```

### 4. Run the App

```bash
streamlit run pg_bot.py
```

## ☁️ Deployment on Amazon EC2

To deploy on a cost-saving `t3.large` instance:

1. Install Ollama on your EC2 instance.
2. Setup a 2GB Swap file for stability.
3. Whitelisted your EC2 IP in your PostgreSQL firewall (Port 5432).
4. Run: `streamlit run pg_bot.py --server.port 80`

## 🛡️ Configuration

All settings are managed via the `.env` file. To connect to your real PostgreSQL:

1. Edit `.env`.
2. Update `DATABASE_URL` with your connection string:
   `postgresql+psycopg2://user:password@localhost:5432/dbname`
3. Restart the app.

---

Built with ❤️ by Amit Prakash for private, specialized database intelligence.

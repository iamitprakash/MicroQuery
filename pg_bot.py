import streamlit as st
import pandas as pd
from schema_teacher import SchemaTeacher
from micromodel_engine import MicromodelEngine
import os
from dotenv import load_dotenv

# Page configuration
st.set_page_config(
    page_title="MSSQL Micromodel Chat",
    page_icon="🤖",
    layout="wide"
)

# Design styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    .status-box {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def get_components():
    load_dotenv()
    teacher = SchemaTeacher()
    engine = MicromodelEngine()
    return teacher, engine

try:
    teacher, engine = get_components()
    schema_context = teacher.get_full_schema_context()
except Exception as e:
    st.error(f"Failed to initialize: {e}")
    st.info("Check your DATABASE_URL in the .env file.")
    st.stop()

# UI Layout
st.title("🛡️ PostgreSQL Micromodel Chatbot")
st.subheader("Query your private database using a specialized local model")

with st.sidebar:
    st.header("Database Insight")
    if st.checkbox("Show Schema 'Taught' to Model"):
        st.code(schema_context, language="markdown")
    
    st.divider()
    st.caption("Running locally via Ollama")
    st.caption("Base Model: Phi-3.5")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sql" in message:
            with st.expander("View Generated SQL"):
                st.code(message["sql"], language="sql")
        if "data" in message:
            st.dataframe(pd.DataFrame(message["data"]))

# Input
if prompt := st.chat_input("Ask a question about your data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("Solving using Micromodel...", expanded=True) as status:
            # 1. Generate SQL
            status.write("Generating T-SQL query...")
            generated_sql = engine.generate_sql(prompt, schema_context)
            
            if "-- ERROR" in generated_sql:
                st.error(generated_sql)
                status.update(label="Generation Failed", state="error")
            else:
                status.write("Executing on MSSQL...")
                # 2. Execute SQL
                result = teacher.execute(generated_sql)
                
                if result["success"]:
                    status.update(label="Success!", state="complete")
                    st.dataframe(pd.DataFrame(result["data"]))
                    
                    # Store in history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "Here is what I found:",
                        "sql": generated_sql,
                        "data": result["data"]
                    })
                else:
                    st.error(f"SQL Execution Error: {result['error']}")
                    st.code(generated_sql, language="sql")
                    status.update(label="Execution Failed", state="error")

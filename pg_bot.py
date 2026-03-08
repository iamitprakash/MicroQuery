import streamlit as st
import pandas as pd
from schema_teacher import SchemaTeacher
from micromodel_engine import MicromodelEngine
import os
import time
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
def get_engine(model_name):
    return MicromodelEngine(model_name=model_name)

@st.cache_resource
def get_teacher():
    return SchemaTeacher()

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Settings")
    
    # 1. Model Selector
    available_models = ["phi3.5", "llama3", "mistral", "gemma2"]
    selected_model = st.selectbox("Select Model (Ollama)", available_models, index=0)
    
    # 2. Review Mode
    review_mode = st.toggle("🛡️ Review Mode (Edit SQL)", value=False)
    
    st.divider()
    st.header("🔍 Database Insight")
    teacher = get_teacher()
    engine = get_engine(selected_model)
    
    if st.checkbox("Show Compact Schema"):
        st.code(teacher.get_full_schema_context(), language="markdown")
    
    st.divider()
    if st.button("🧹 Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# UI Layout
st.title("Amit Prakash's Micromodel Chatbot")
st.subheader("Query your hyper-scale database with intelligent visuals")

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
            status.write(f"Generating SQL using {selected_model}...")
            generated_sql = engine.generate_sql(prompt, teacher)
            
            # Handle Review Mode
            if review_mode:
                final_sql = st.text_area("Review/Edit Generated SQL:", value=generated_sql, height=150)
                execute_btn = st.button("🚀 Run Query", key=f"run_{prompt[:10]}")
                if not execute_btn:
                    st.info("Edit the SQL above and click 'Run Query'")
                    st.stop()
            else:
                final_sql = generated_sql

            if "-- ERROR" in final_sql:
                st.error(final_sql)
                status.update(label="Generation Failed", state="error")
            else:
                # 2. Execute SQL
                status.write("Executing on PostgreSQL...")
                result = teacher.execute(final_sql)
                
                if result["success"]:
                    status.update(label="Success!", state="complete")
                    df = pd.DataFrame(result["data"])
                    st.dataframe(df)
                    
                    # 3. Export Facility
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name=f"query_result_{int(time.time())}.csv",
                        mime='text/csv',
                    )

                    # 4. Proactive Visuals
                    if not df.empty and len(df.columns) >= 2:
                        num_cols = df.select_dtypes(include=['number']).columns.tolist()
                        cat_cols = df.select_dtypes(exclude=['number']).columns.tolist()
                        
                        if num_cols and cat_cols:
                            with st.expander("📊 Proactive Data Insights", expanded=True):
                                suggested_chart = "Bar"
                                reason = "Data distribution comparison detected."
                                
                                if "-- CHART:" in final_sql:
                                    parts = final_sql.split("-- CHART:")[1].split("|")
                                    suggested_chart = parts[0].strip()
                                    if len(parts) > 1 and "REASON:" in parts[1]:
                                        reason = parts[1].replace("REASON:", "").strip()
                                
                                st.info(f"💡 **Insight:** {reason}")
                                tabs = st.tabs(["Bar Chart", "Line Chart", "Pie Chart"])
                                with tabs[0]:
                                    st.bar_chart(df.set_index(cat_cols[0])[num_cols[0]])
                                with tabs[1]:
                                    st.line_chart(df.set_index(cat_cols[0])[num_cols[0]])
                                with tabs[2]:
                                    st.info("Pie Chart optimization recommended for this dataset.")

                    # History
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "I've analyzed the data for you:",
                        "sql": final_sql,
                        "data": result["data"]
                    })
                else:
                    st.error(f"SQL Error: {result['error']}")
                    st.code(final_sql, language="sql")
                    status.update(label="Execution Failed", state="error")

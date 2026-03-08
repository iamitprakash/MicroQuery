import streamlit as st
import pandas as pd
from schema_teacher import SchemaTeacher
from micromodel_engine import MicromodelEngine
import os
import time
import plotly.express as px
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
    available_models = ["phi3.5:latest", "llama3.1:latest", "mistral", "gemma2"]
    index = 0
    selected_model = st.selectbox("Select Model (Ollama)", available_models, index=index)
    
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
                    # 4. Proactive Visuals
                    if not df.empty and len(df.columns) >= 2:
                        num_cols = df.select_dtypes(include=['number']).columns.tolist()
                        cat_cols = df.select_dtypes(exclude=['number', 'datetime']).columns.tolist()
                        date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
                        
                        if num_cols:
                            with st.expander("📊 Proactive Data Insights", expanded=True):
                                suggested_chart = "Bar"
                                reason = "Data visualization prepared for trend/distribution analysis."
                                
                                if "-- CHART:" in final_sql:
                                    parts = final_sql.split("-- CHART:")[1].split("|")
                                    suggested_chart = parts[0].strip()
                                    if len(parts) > 1 and "REASON:" in parts[1]:
                                        reason = parts[1].replace("REASON:", "").strip()
                                
                                tabs = st.tabs(["📊 Bar/Line", "🍩 Composition", "🔥 Correlation"])
                                
                                # Determine X-axis: Categorical -> Date -> Index
                                x_axis = None
                                if cat_cols: x_axis = cat_cols[0]
                                elif date_cols: x_axis = date_cols[0]
                                
                                # Metrics
                                y_axes = num_cols[:3]
                                chart_data = df.set_index(x_axis)[y_axes] if x_axis else df[y_axes]
                                
                                with tabs[0]:
                                    st.subheader("Comparison Analysis")
                                    fig_bar = px.bar(df, x=x_axis, y=y_axes, barmode="group", title="Metric Comparison (Bar)")
                                    st.plotly_chart(fig_bar, use_container_width=True)
                                    img_bar = fig_bar.to_image(format="png")
                                    st.download_button(label="📥 Save Bar Chart as PNG", data=img_bar, file_name="bar_chart.png", mime="image/png")
                                    
                                    fig_line = px.line(df, x=x_axis, y=y_axes, title="Trend Analysis (Line)")
                                    st.plotly_chart(fig_line, use_container_width=True)
                                    img_line = fig_line.to_image(format="png")
                                    st.download_button(label="📥 Save Line Chart as PNG", data=img_line, file_name="line_chart.png", mime="image/png")
                                
                                with tabs[1]:
                                    if x_axis and len(num_cols) > 0:
                                        fig_pie = px.pie(df, names=x_axis, values=num_cols[0], title="Market Share (Pie)")
                                        st.plotly_chart(fig_pie, use_container_width=True)
                                        img_pie = fig_pie.to_image(format="png")
                                        st.download_button(label="📥 Save Pie Chart as PNG", data=img_pie, file_name="pie_chart.png", mime="image/png")
                                        
                                        fig_donut = px.pie(df, names=x_axis, values=num_cols[0], hole=0.5, title="Composition (Donut)")
                                        st.plotly_chart(fig_donut, use_container_width=True)
                                        img_donut = fig_donut.to_image(format="png")
                                        st.download_button(label="📥 Save Donut Chart as PNG", data=img_donut, file_name="donut_chart.png", mime="image/png")
                                    else:
                                        st.warning("Pie/Donut requires a categorical column and a numeric value.")
                                
                                with tabs[2]:
                                    if len(num_cols) >= 2:
                                        corr_df = df[num_cols].corr()
                                        fig_heat = px.imshow(corr_df, text_auto=True, title="Metric Correlation Heatmap", aspect="auto")
                                        st.plotly_chart(fig_heat, use_container_width=True)
                                        img_heat = fig_heat.to_image(format="png")
                                        st.download_button(label="📥 Save Heatmap as PNG", data=img_heat, file_name="heatmap.png", mime="image/png")
                                    else:
                                        st.warning("Heatmap requires multiple numeric metrics to analyze correlation.")

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

import streamlit as st
import pandas as pd
from schema_teacher import SchemaTeacher
from micromodel_engine import MicromodelEngine
import os
import time
import plotly.express as px

import json

def load_db_profiles():
    with open("db_profiles.json", "r") as f:
        return json.load(f)

@st.cache_data
def get_plotly_image(df, chart_type, x_axis, y_axes):
    """Generates Plotly PNG bytes with caching to prevent UI lag."""
    if chart_type == "bar":
        fig = px.bar(df, x=x_axis, y=y_axes, barmode="group", title="Metric Comparison (Bar)")
    elif chart_type == "line":
        fig = px.line(df, x=x_axis, y=y_axes, title="Trend Analysis (Line)")
    elif chart_type == "pie":
        fig = px.pie(df, names=x_axis, values=y_axes[0], title="Market Share (Pie)")
    elif chart_type == "donut":
        fig = px.pie(df, names=x_axis, values=y_axes[0], hole=0.5, title="Composition (Donut)")
    elif chart_type == "heatmap":
        corr_df = df[y_axes].corr()
        fig = px.imshow(corr_df, text_auto=True, title="Metric Correlation Heatmap", aspect="auto")
    else:
        return None
    
    return fig.to_image(format="png")
from fpdf import FPDF
import io

def create_pdf_report(df, question, sql, images=None):
    """Generates a professional PDF report from query results."""
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "MicroQuery Analysis Report", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Generated on: {time.ctime()}", ln=True, align='C')
    pdf.ln(10)
    
    # Question & SQL
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Natural Language Question:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, question)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Generated SQL Engine:", ln=True)
    pdf.set_font("Courier", size=8)
    pdf.multi_cell(0, 5, sql)
    pdf.ln(10)
    
    # Data Preview
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Data Insights (Showing top {min(len(df), 15)} rows):", ln=True)
    pdf.set_font("Arial", size=8)
    
    # Header
    col_width = pdf.epw / min(len(df.columns), 6)
    for col in df.columns[:6]:
        pdf.cell(col_width, 10, str(col), border=1)
    pdf.ln()
    
    # Rows
    for i in range(min(len(df), 15)):
        for col in df.columns[:6]:
            pdf.cell(col_width, 8, str(df.iloc[i][col])[:20], border=1)
        pdf.ln()
    
    # Images (Charts)
    if images:
        for title, img_bytes in images.items():
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, title, ln=True, align='C')
            img_stream = io.BytesIO(img_bytes)
            pdf.image(img_stream, x=10, y=30, w=190)
            
    return pdf.output()

from dotenv import load_dotenv

# --- AUTHENTICATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login_screen():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/1053/1053210.png", width=80)
        st.title("🛡️ Secure Access")
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            if user == "admin" and pw == "admin123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.stop()

# Page configuration (MUST be the first Streamlit command if not stopping)
if not st.session_state.authenticated:
    st.set_page_config(page_title="MicroQuery Login", page_icon="🛡️")
    login_screen()

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
def get_teacher(conn_str):
    return SchemaTeacher(connection_string=conn_str)

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Settings")
    
    # 0. Database Profile Selector
    profiles = load_db_profiles()
    profile_names = [p["name"] for p in profiles]
    selected_p_name = st.selectbox("Database Profile", profile_names)
    selected_p = next(p for p in profiles if p["name"] == selected_p_name)
    
    # Construct Connection String
    conn_str = f"postgresql+psycopg2://{selected_p['user']}:{selected_p['pass']}@{selected_p['host']}:{selected_p['port']}/{selected_p['database']}"
    
    # 1. Model Selector
    available_models = ["phi3.5:latest", "llama3.1:latest", "mistral", "gemma2"]
    index = 0
    selected_model = st.selectbox("Select Model (Ollama)", available_models, index=index)
    
    # 2. Review Mode
    review_mode = st.toggle("🛡️ Review Mode (Edit SQL)", value=False)
    
    st.divider()
    if st.sidebar.button("🔓 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    st.sidebar.divider()
    st.header("🔍 Database Insight")
    teacher = get_teacher(conn_str)
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
        result = None
        df = None
        final_sql = ""

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
                
                # LEARNING: If the user edited the SQL, update the cache with the human-corrected version
                if final_sql != generated_sql:
                    engine.cache.store_sql(prompt, selected_model, final_sql)
                    st.toast("Human correction saved to persistent cache! 🧠", icon="💾")
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
                    
                    # 2.1 Sanitize Data Types (Cast Decimals to Floats)
                    with st.spinner("🔢 Processing database types..."):
                        import decimal
                        for col in df.columns:
                            if df[col].apply(lambda x: isinstance(x, decimal.Decimal)).any():
                                df[col] = df[col].astype(float)
                else:
                    st.error(f"SQL Error: {result['error']}")
                    st.code(final_sql, language="sql")
                    status.update(label="Execution Failed", state="error")

        # 3. Render Results (Outside status block for visibility)
        if result and result["success"]:
            if df.empty:
                st.warning("📭 **No results found.** The query executed successfully but returned zero rows. Try adjusting your filters.")
                if "city" in final_sql.lower():
                    with st.expander("🔍 Check available cities"):
                        city_check = teacher.execute("SELECT city, count(*) FROM customers GROUP BY city ORDER BY count(*) DESC LIMIT 5")
                        if city_check["success"]:
                            st.write("Top cities in your database:")
                            st.table(pd.DataFrame(city_check["data"]))
            else:
                # 3. Interactive Drill-Downs
                cat_cols = df.select_dtypes(exclude=['number', 'datetime']).columns.tolist()
                filtered_df = df.copy()
                
                if cat_cols:
                    primary_dim = cat_cols[0]
                    with st.sidebar.expander("🔍 Interactive Drill-Down", expanded=True):
                        st.write(f"Filter by **{primary_dim}**:")
                        unique_vals = sorted(df[primary_dim].unique().tolist())
                        selected_vals = st.multiselect("Select values to focus on:", unique_vals, default=unique_vals)
                        
                        if selected_vals:
                            filtered_df = df[df[primary_dim].isin(selected_vals)]
                        else:
                            st.warning("Please select at least one value.")
                            filtered_df = df.iloc[0:0] # Empty but keeps schema

                st.dataframe(filtered_df, use_container_width=True)
                
                # Export Facility (Filtered)
                col_csv, col_pdf = st.columns(2)
                with col_csv:
                    csv = filtered_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Filtered CSV",
                        data=csv,
                        file_name=f"filtered_result_{int(time.time())}.csv",
                        mime='text/csv',
                    )
                
                with col_pdf:
                    if st.button("📄 Generate PDF Report", use_container_width=True):
                        with st.spinner("🖋️ Authoring PDF Report..."):
                            report_images = {}
                            num_cols = filtered_df.select_dtypes(include=['number']).columns.tolist()
                            cat_cols = filtered_df.select_dtypes(exclude=['number', 'datetime']).columns.tolist()
                            date_cols = filtered_df.select_dtypes(include=['datetime']).columns.tolist()
                            x_axis = cat_cols[0] if cat_cols else (date_cols[0] if date_cols else None)
                            y_axes = num_cols[:3]
                            
                            if x_axis and y_axes:
                                report_images["Comparison Analysis (Bar)"] = get_plotly_image(filtered_df, "bar", x_axis, y_axes)
                                report_images["Composition (Donut)"] = get_plotly_image(filtered_df, "donut", x_axis, y_axes)
                            
                            if len(num_cols) >= 2:
                                report_images["Metric Correlation (Heatmap)"] = get_plotly_image(filtered_df, "heatmap", None, num_cols)
                            
                            pdf_bytes = create_pdf_report(filtered_df, prompt, final_sql, report_images)
                            st.download_button(
                                label="📥 Save PDF Report",
                                data=pdf_bytes,
                                file_name=f"analysis_report_{int(time.time())}.pdf",
                                mime='application/pdf'
                            )

                # 4. Proactive Visuals
                if not filtered_df.empty and len(filtered_df.columns) >= 2:
                    num_cols = filtered_df.select_dtypes(include=['number']).columns.tolist()
                    cat_cols = filtered_df.select_dtypes(exclude=['number', 'datetime']).columns.tolist()
                    date_cols = filtered_df.select_dtypes(include=['datetime']).columns.tolist()
                    
                    if num_cols:
                        with st.expander("📊 Proactive Data Insights", expanded=True):
                            with st.spinner("📈 Generating interactive visuals..."):
                                suggested_chart = "Bar"
                                reason = "Data visualization prepared for trend/distribution analysis."
                                
                                if "-- CHART:" in final_sql:
                                    parts = final_sql.split("-- CHART:")[1].split("|")
                                    suggested_chart = parts[0].strip()
                                    if len(parts) > 1 and "REASON:" in parts[1]:
                                        reason = parts[1].replace("REASON:", "").strip()
                                
                                tabs = st.tabs(["📊 Bar/Line", "🍩 Composition", "🔥 Correlation"])
                                
                                # Determine X-axis
                                x_axis = cat_cols[0] if cat_cols else (date_cols[0] if date_cols else None)
                                y_axes = num_cols[:3]
                                
                                with tabs[0]:
                                    st.subheader("Comparison Analysis")
                                    fig_bar = px.bar(filtered_df, x=x_axis, y=y_axes, barmode="group", title="Metric Comparison (Bar)")
                                    st.plotly_chart(fig_bar, use_container_width=True)
                                    # Use filtered_df for cached image
                                    img_bar = get_plotly_image(filtered_df, "bar", x_axis, y_axes)
                                    st.download_button(label="📥 Save Bar Chart as PNG", data=img_bar, file_name="bar_chart.png", mime="image/png")
                                    
                                    fig_line = px.line(filtered_df, x=x_axis, y=y_axes, title="Trend Analysis (Line)")
                                    st.plotly_chart(fig_line, use_container_width=True)
                                    img_line = get_plotly_image(filtered_df, "line", x_axis, y_axes)
                                    st.download_button(label="📥 Save Line Chart as PNG", data=img_line, file_name="line_chart.png", mime="image/png")
                                
                                with tabs[1]:
                                    if x_axis and len(num_cols) > 0:
                                        fig_pie = px.pie(filtered_df, names=x_axis, values=num_cols[0], title="Market Share (Pie)")
                                        st.plotly_chart(fig_pie, use_container_width=True)
                                        img_pie = get_plotly_image(filtered_df, "pie", x_axis, num_cols)
                                        st.download_button(label="📥 Save Pie Chart as PNG", data=img_pie, file_name="pie_chart.png", mime="image/png")
                                        
                                        fig_donut = px.pie(filtered_df, names=x_axis, values=num_cols[0], hole=0.5, title="Composition (Donut)")
                                        st.plotly_chart(fig_donut, use_container_width=True)
                                        img_donut = get_plotly_image(filtered_df, "donut", x_axis, num_cols)
                                        st.download_button(label="📥 Save Donut Chart as PNG", data=img_donut, file_name="donut_chart.png", mime="image/png")
                                    else:
                                        st.warning("Pie/Donut requires a categorical column and a numeric value.")
                                
                                with tabs[2]:
                                    if len(num_cols) >= 2:
                                        fig_heat = px.imshow(filtered_df[num_cols].corr(), text_auto=True, title="Metric Correlation Heatmap", aspect="auto")
                                        st.plotly_chart(fig_heat, use_container_width=True)
                                        img_heat = get_plotly_image(filtered_df, "heatmap", None, num_cols)
                                        st.download_button(label="📥 Save Heatmap as PNG", data=img_heat, file_name="heatmap.png", mime="image/png")
                                    else:
                                        st.warning("Heatmap requires multiple numeric metrics to analyze correlation.")

            # History & Feedback
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "I've analyzed the data for you:",
                "sql": final_sql,
                "data": filtered_df.to_dict('records') if not filtered_df.empty else [],
                "question": prompt,
                "model": selected_model
            })

            c1, c2, c3 = st.columns([1,1,10])
            with c1:
                if st.button("👍", key=f"up_{int(time.time())}"):
                    engine.cache.update_feedback(prompt, selected_model, 1)
                    st.toast("Thanks for the feedback!", icon="✅")
            with c2:
                if st.button("👎", key=f"down_{int(time.time())}"):
                    engine.cache.update_feedback(prompt, selected_model, -1)
                    st.toast("Feedback recorded.", icon="⚠️")

# 🛡️ System Administration (Footer)
st.divider()
with st.expander("🛡️ System Activity & Cache Explorer"):
    st.info("The AI caches generated SQL in a local **SQLite** database for privacy and speed. This is separate from your main **PostgreSQL** data.")
    all_cache = engine.cache.get_all_cache()
    if all_cache:
        cache_df = pd.DataFrame(all_cache)
        st.dataframe(cache_df, use_container_width=True)
    else:
        st.write("Cache is currently empty.")


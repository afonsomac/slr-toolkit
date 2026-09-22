import streamlit as st

# --- Configuração da Página ---
st.set_page_config(
    page_title="SLR Toolkit | Home",
    page_icon="📚",
    layout="centered"
)

# --- Cabeçalho ---
st.title("📚 SLR Toolkit")
st.subheader("Deterministic Tools for Systematic Literature Reviews")

st.markdown("""
Welcome to the **SLR Toolkit**. This environment is built to help researchers automate and structure their literature reviews with complete methodological transparency, moving away from unreliable generative AI "black boxes".

👈 **Please select a tool from the sidebar to begin:**
""")

st.markdown("---")

# --- Descrição das Ferramentas ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📥 1. PDF Downloader")
    st.markdown("""
    **Missing the PDFs?**
    - Upload your Scopus / Web of Science export files (CSV, XLS, XLSX).
    - Automatically batch-download Open Access papers using the Unpaywall API.
    - Get a clean ZIP file ready for analysis.
    """)

with col2:
    st.markdown("### 📊 2. Matrix Generator")
    st.markdown("""
    **Already have your PDFs?**
    - Perform robust thematic analysis using RegEx keyword tracking.
    - Identify research gaps through co-occurrence matrices.
    - Export data and visualize interactive literature network graphs.
    """)

st.markdown("---")

# --- Créditos / Citação ---
st.info("""
**Methodological Integrity:**  
No generative AI is used in data processing. Keyword tracking is deterministic, mathematical, and 100% reproducible.
""")

with st.expander("ℹ️ About & How to Cite"):
    st.markdown("""
    **SLR Toolkit v1.0**  
    Developed to support academic research in logistics, supply chain, and sustainability.
    
    **Suggested Citation:**  
    Carvalho, A. (2026). *A Deterministic Matrix Framework for Mapping Literature Gaps*. [Journal Name].
    """)
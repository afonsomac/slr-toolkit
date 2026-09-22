import streamlit as st
import streamlit.components.v1 as components
import pymupdf
import pandas as pd
import re
from pyvis.network import Network

# --- Page Configuration ---
st.set_page_config(page_title="SLR Matrix Generator", layout="wide")

st.title("Deterministic Matrix Generator for Literature Review")
st.markdown("Extract theme correlations across scientific papers using advanced RegEx tracking.")

# --- 1. Sidebar Configuration ---
st.sidebar.header("Search Dictionary")

# Initialize session state for base groups and UI memory
if 'theme_groups' not in st.session_state:
    st.session_state['theme_groups'] = {
        "Methods": "machine learning, heuristic\\w*, simulat\\w*",
        "Logistics Problems": "container drayage, routing, hinterland",
        "Sustainability": "circular economy, science based targets, emission\\w*"
    }

# Callback to add a new group safely
def add_new_group():
    name = st.session_state.new_group_name
    words = st.session_state.new_group_words
    if name.strip() and words.strip():
        st.session_state['theme_groups'][name] = words
        st.session_state.new_group_name = ""
        st.session_state.new_group_words = ""

st.sidebar.write("Add New Group")
st.sidebar.text_input("Group Name (e.g., Technologies)", key="new_group_name")
st.sidebar.text_input("Keywords (comma separated)", key="new_group_words")
st.sidebar.button("Add Group", on_click=add_new_group, type="secondary")

st.sidebar.divider()

# Rigor Setting: Minimum occurrences threshold
st.sidebar.subheader("Analysis Rigor")
min_occurrences = st.sidebar.number_input(
    "Minimum keyword matches to validate a theme", 
    min_value=1, max_value=20, value=1, step=1,
    help="A theme is marked as present (1) only if its keywords appear at least this many times."
)

st.sidebar.divider()
st.sidebar.write("Current Groups:")

theme_dictionary = {}
groups_to_remove = []

# Display all saved groups allowing edition or removal
for group_name, words in st.session_state['theme_groups'].items():
    col1, col2 = st.sidebar.columns([5, 1]) 
    
    with col1:
        input_words = st.text_input(group_name, value=words, key=f"input_{group_name}")
        if input_words:
            theme_dictionary[group_name] = [x.strip() for x in input_words.split(",")]
            st.session_state['theme_groups'][group_name] = input_words
            
    with col2:
        st.write("") 
        st.write("")
        if st.button("🗑️", key=f"del_{group_name}", help=f"Remove {group_name}"):
            groups_to_remove.append(group_name)

# Process removals
if groups_to_remove:
    for group in groups_to_remove:
        del st.session_state['theme_groups'][group]
    st.rerun()

st.sidebar.divider()

# --- NEW: Academic ROI (Citation) ---
with st.sidebar.expander("ℹ️ About & How to Cite"):
    st.markdown("""
    **SLR Matrix Generator v1.0**  
    A deterministic, transparent framework for systematic literature reviews and research gap identification.
    
    **Suggested Citation:**  
    Carvalho, A. (2026). *A Deterministic Matrix Framework for Mapping Literature Gaps*. [Journal Name].
    """)

# --- 2. Main Area (Upload & Execution) ---
st.header("1. Upload Papers (PDF)")
pdf_files = st.file_uploader("Drag and drop your PDF files here", type=["pdf"], accept_multiple_files=True)

st.markdown("---")
st.header("2. Run Analysis")

# --- NEW: Run and Clear Buttons side by side ---
col_run, col_clear = st.columns([4, 1])
with col_run:
    execute_button = st.button("Generate Literature Matrices", type="primary", use_container_width=True)
with col_clear:
    if st.button("Clear Analysis", use_container_width=True, help="Reset results to start a new analysis"):
        for key in ['df_asym_bin', 'df_asym_abs', 'df_sym']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Processing Logic
if pdf_files and execute_button:
    results_binary = []
    results_absolute = []
    
    # Progress UI Elements
    progress_text = st.empty()
    progress_bar = st.progress(0)
    total_files = len(pdf_files)
    
    for index, file in enumerate(pdf_files):
        progress_text.text(f"Analyzing paper {index + 1} of {total_files}: {file.name}...")
        progress_bar.progress((index + 1) / total_files)
        
        text = ""
        try:
            with pymupdf.open(stream=file.read(), filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text().lower()
            
            # Data Quality: Fix words cut by line breaks
            text = text.replace("-\n", "")
            
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")
            continue
        
        paper_bin = {"Paper": file.name}
        paper_abs = {"Paper": file.name}
        
        for theme, expressions in theme_dictionary.items():
            total_matches = 0
            for expression in expressions:
                matches = re.findall(r"\b" + expression + r"\b", text, re.IGNORECASE)
                total_matches += len(matches)
            
            paper_abs[theme] = total_matches
            paper_bin[theme] = 1 if total_matches >= min_occurrences else 0
            
        results_binary.append(paper_bin)
        results_absolute.append(paper_abs)

    if results_binary:
        progress_text.empty()
        progress_bar.empty()
        
        df_asym_bin = pd.DataFrame(results_binary).set_index("Paper")
        df_asym_abs = pd.DataFrame(results_absolute).set_index("Paper")
        df_sym = df_asym_bin.T.dot(df_asym_bin) 
        
        st.session_state['df_asym_bin'] = df_asym_bin
        st.session_state['df_asym_abs'] = df_asym_abs
        st.session_state['df_sym'] = df_sym
        st.success(f"Analysis successfully completed for {total_files} papers!")

# --- 3. Display Results & Dashboard ---
if 'df_asym_bin' in st.session_state:
    df_sym = st.session_state['df_sym']
    df_asym_bin = st.session_state['df_asym_bin']
    df_asym_abs = st.session_state['df_asym_abs']
    
    st.markdown("---")
    st.header("📊 Results Dashboard")
    
    # KPIs
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    most_studied_theme = df_sym.sum().idxmax() if not df_sym.empty else "N/A"
    total_gaps = (df_sym.values == 0).sum() // 2 if not df_sym.empty else 0
    
    col_kpi1.metric("Papers Analyzed", len(df_asym_bin))
    col_kpi2.metric("Dominant Theme", most_studied_theme)
    col_kpi3.metric("Research Gaps Identified", total_gaps, help="Theme intersections with zero occurrences.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Symmetric Matrix (Heatmap)
    st.subheader("Symmetric Matrix (Theme Co-occurrence)")
    st.info("Darker colors indicate stronger correlation. White cells represent zero occurrences (Gaps).")
    st.dataframe(df_sym.style.background_gradient(cmap='YlGnBu', axis=None), use_container_width=True)
    st.download_button("Download Symmetric Matrix (CSV)", df_sym.to_csv().encode('utf-8'), "symmetric_matrix.csv", "text/csv")
    
    st.markdown("---")
    
    # Interactive Network Graph
    st.subheader("🌐 Network Graph: Theme Relationships")
    st.info("Interactive graph! Drag the nodes, zoom in/out. Node size = Total papers. Line thickness = Co-occurrences.")
    
    net = Network(height='500px', width='100%', bgcolor='#f8f9fa', font_color='#2c3e50')
    temas = df_sym.columns.tolist()
    
    for tema in temas:
        frequencia = int(df_sym.loc[tema, tema])
        if frequencia > 0:
            net.add_node(tema, label=tema, title=f"{tema} (Total: {frequencia})", size=10 + (frequencia * 3))
            
    for i, tema_A in enumerate(temas):
        for j, tema_B in enumerate(temas):
            if i < j:
                coocorrencia = int(df_sym.loc[tema_A, tema_B])
                if coocorrencia > 0:
                    net.add_edge(tema_A, tema_B, value=coocorrencia, title=f"Co-occurrence: {coocorrencia}")
                    
    net.repulsion(node_distance=150, central_gravity=0.2, spring_length=150, spring_strength=0.05, damping=0.09)
    
    try:
        path_html = "pyvis_graph.html"
        net.save_graph(path_html)
        with open(path_html, 'r', encoding='utf-8') as HtmlFile:
            source_code = HtmlFile.read()
            components.html(source_code, height=520)
            
            # --- NEW: Download button for the HTML Graph ---
            st.download_button(
                label="Download Interactive Graph (HTML)",
                data=source_code,
                file_name="literature_network_graph.html",
                mime="text/html",
                help="Download the graph to open it in your browser offline or share it."
            )
            
    except Exception as e:
        st.error(f"Error rendering graph: {e}")

    st.markdown("---")
    
    # Detail Matrices
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Asymmetric Matrix (Binary)")
        st.info(f"0 = Absent | 1 = Present (Min. {min_occurrences} occurrences)")
        st.dataframe(df_asym_bin.style.background_gradient(cmap='Greys', axis=None), use_container_width=True)
        st.download_button("Download Binary Matrix (CSV)", df_asym_bin.to_csv().encode('utf-8'), "asymmetric_binary.csv", "text/csv")
        
    with col_b:
        st.subheader("Absolute Frequency Matrix")
        st.info("Exact number of keyword occurrences per paper.")
        st.dataframe(df_asym_abs.style.background_gradient(cmap='Reds', axis=None), use_container_width=True)
        st.download_button("Download Frequency Matrix (CSV)", df_asym_abs.to_csv().encode('utf-8'), "asymmetric_frequency.csv", "text/csv")
import streamlit as st
import requests
import pandas as pd
import time
import io
import zipfile
import re

# --- Page Configuration ---
st.set_page_config(page_title="Open Access PDF Downloader", layout="wide")

st.title("Open Access PDF Downloader")
st.markdown("Automate the retrieval of Open Access scientific papers using the Unpaywall API.")

# --- 1. Authentication ---
st.subheader("1. Authentication")
st.info("The Unpaywall API is free but requires a valid email address.")
email = st.text_input("Your Email Address", placeholder="researcher@university.edu")

st.markdown("---")

# --- 2. Input Methods (Tabs) ---
st.subheader("2. Provide DOIs")
st.info("Choose how you want to input your DOIs. We will automatically clean URLs and extract the exact DOI.")

tab1, tab2 = st.tabs(["📋 Paste Text", "📁 Upload File (CSV / Excel)"])

raw_dois = [] # Variable to hold raw input from either method

with tab1:
    doi_input = st.text_area(
        "List of DOIs (one per line)", 
        height=150, 
        placeholder="https://doi.org/10.1016/j.jclepro.2020.125793\n10.1016/j.tre.2019.101844"
    )
    if doi_input.strip():
        raw_dois = doi_input.split('\n')

with tab2:
    # Dica visual amigável (UX)
    st.info("💡 **Tip for Scopus/WoS users:** If your `.xls` file gives an error, open it in Excel, click 'Save As...', and choose **CSV** or **.xlsx**.")
    
    uploaded_file = st.file_uploader("Upload your Scopus/WoS export file", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            # Motor de leitura inteligente (Plano A e Plano B)
            if uploaded_file.name.endswith('.csv'):
                df_upload = pd.read_csv(uploaded_file)
            else:
                try:
                    # Plano A: Tenta ler como Excel real
                    df_upload = pd.read_excel(uploaded_file)
                except Exception:
                    # Plano B: Tenta ler como o falso .xls da Scopus (texto separado por Tabs)
                    uploaded_file.seek(0)
                    df_upload = pd.read_csv(uploaded_file, sep='\t')
                    
            st.success("File uploaded successfully!")
            
            # Tentar adivinhar a coluna que tem o DOI
            col_names = df_upload.columns.tolist()
            guess_col = next((col for col in col_names if 'doi' in col.lower()), col_names[0])
            
            # Caixa de seleção para o utilizador confirmar a coluna certa
            selected_col = st.selectbox("Which column contains the DOIs?", col_names, index=col_names.index(guess_col))
            
            if selected_col:
                raw_dois = df_upload[selected_col].dropna().astype(str).tolist()
                st.write(f"Found **{len(raw_dois)}** rows in column '{selected_col}'.")
                
        except Exception as e:
            st.error(f"Error reading file: Please follow the tip above and save as CSV. (Technical error: {e})")

st.markdown("---")

# --- 3. Execution ---
st.subheader("3. Run Download")

if st.button("Fetch PDFs", type="primary", use_container_width=True):
    if not email or "@" not in email:
        st.error("Please provide a valid email address.")
    elif not raw_dois:
        st.error("Please provide at least one DOI via text or file upload.")
    else:
        # DATA CLEANING: Regex infalível
        lista_dois = []
        for line in raw_dois:
            match = re.search(r'(10\.\d{4,9}/[-._;()/:a-zA-Z0-9]+)', str(line))
            if match:
                doi_encontrado = match.group(1)
                doi_limpo = doi_encontrado.rstrip(').,;:]')
                
                if doi_limpo not in lista_dois:
                    lista_dois.append(doi_limpo)
                    
        total_dois = len(lista_dois)
        
        if total_dois == 0:
            st.error("No valid DOIs found. Please ensure they contain the standard format (e.g., 10.1016/...)")
            st.stop()
            
        st.info(f"Successfully extracted {total_dois} unique valid DOIs to process.")
            
        zip_buffer = io.BytesIO()
        log_resultados = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        tabela_placeholder = st.empty()
        
        sucessos = 0
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for index, doi in enumerate(lista_dois):
                status_text.text(f"Checking DOI {index + 1} of {total_dois}: {doi}...")
                progress_bar.progress((index + 1) / total_dois)
                
                url_api = f"https://api.unpaywall.org/v2/{doi}?email={email}"
                estado = "Not Found"
                titulo_artigo = doi 
                
                try:
                    resposta = requests.get(url_api, timeout=10)
                    
                    if resposta.status_code == 200:
                        dados = resposta.json()
                        
                        if dados.get("title"):
                            titulo_artigo = str(dados.get("title"))
                            
                        if dados.get("is_oa") and dados.get("best_oa_location"):
                            url_pdf = dados["best_oa_location"].get("url_for_pdf")
                            
                            if url_pdf:
                                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                                pdf_resposta = requests.get(url_pdf, headers=headers, timeout=15)
                                
                                if pdf_resposta.status_code == 200 and b"%PDF" in pdf_resposta.content[:10]:
                                    safe_title = re.sub(r'[\\/*?:"<>|]', '', titulo_artigo)[:100]
                                    safe_filename = f"{safe_title}.pdf"
                                    
                                    zip_file.writestr(safe_filename, pdf_resposta.content)
                                    estado = "Success"
                                    sucessos += 1
                                else:
                                    estado = "Error: Invalid PDF / Publisher block"
                            else:
                                estado = "Paywall / No direct link"
                        else:
                            estado = "Paywall (Closed Access)"
                    elif resposta.status_code == 404:
                         estado = "DOI not found in database"
                except requests.exceptions.RequestException:
                    estado = "Network timeout / Server error"
                
                log_resultados.append({"DOI": doi, "Title": titulo_artigo, "Status": estado})
                
                df_temp = pd.DataFrame(log_resultados)
                tabela_placeholder.dataframe(df_temp, use_container_width=True)
                
                time.sleep(1)

        status_text.empty()
        progress_bar.empty()
        
        # --- 4. Results & Downloads ---
        st.success(f"Task completed! Downloaded {sucessos} Open Access PDFs out of {total_dois} DOIs.")
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.subheader("📦 Get Your PDFs")
            if sucessos > 0:
                st.download_button(
                    label="Download ZIP File with PDFs",
                    data=zip_buffer.getvalue(),
                    file_name="open_access_papers.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.warning("No PDFs were found to download.")
                
        with col_res2:
            st.subheader("📄 Download Report")
            st.download_button(
                label="Download Status Report (CSV)",
                data=df_temp.to_csv(index=False).encode('utf-8'),
                file_name="download_report.csv",
                mime="text/csv",
                use_container_width=True
            )
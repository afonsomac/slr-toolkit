# 📚 SLR Toolkit: A Deterministic Framework for Systematic Literature Reviews

**🚀 Try the Web App directly here:** https://slr-toolkit-4pt8cidkybh8mhmprvyzvq.streamlit.app/

The **SLR Toolkit** is an open-source, Streamlit-based web application designed to assist researchers in automating and structuring their Systematic Literature Reviews (SLRs). 

Unlike recent "black-box" generative AI tools, this toolkit prioritizes **methodological transparency, reproducibility, and deterministic data processing**, making it fully suitable for rigorous academic workflows and peer-reviewed publications.

---

## ⚙️ Core Modules

### 1. 📥 PDF Downloader (Unpaywall API Integration)
A robust automation tool to bypass the manual labor of downloading individual Open Access papers.
* **Batch Processing:** Upload your Scopus or Web of Science export files (CSV, XLS, XLSX). Includes defensive reading for incorrectly formatted database exports.
* **Smart Extraction:** Automatically identifies DOIs and cleans URL parameters.
* **Open Access Fetching:** Connects to the Unpaywall API to retrieve legal, open-access PDFs.
* **Zip Export:** Packages all successfully downloaded PDFs into a single ZIP file ready for analysis, alongside a detailed status report.

### 2. 📊 Matrix Generator
A thematic analysis engine for processing full-text PDFs and mapping research gaps.
* **Deterministic Text Mining:** Uses exact RegEx matching (via PyMuPDF) to track custom keywords across dozens of papers.
* **Co-occurrence Matrices:** Automatically generates relationship matrices between tracked themes.
* **Interactive Network Graphs:** Visualizes literature gaps and theme clusters using dynamic HTML network graphs (via Pyvis).
* **Data Export:** Download the structured matrix as an Excel file to be used as supplementary material in your research paper.

---

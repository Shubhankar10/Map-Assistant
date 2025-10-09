# temp.py
import streamlit as st
import time
from main import main

def display_markdown(md_content: str):
    """
    Display a Markdown string in Streamlit in a clean and professional format.
    """
    st.markdown("---")  # horizontal separator
    st.markdown(md_content, unsafe_allow_html=True)


# --------------------------
# Simulated main function
# --------------------------

def run_app():
    st.set_page_config(page_title="Map Mentor", page_icon="🗺️", layout="wide")
    st.title("🗺️ Map Mentor - LLM Output Viewer")

    # Input field
    query = st.text_area("Enter your query:", height=100)

    # Button to submit
    if st.button("Submit Query") and query.strip():
        with st.spinner("Processing your query..."):
            response_md = main(query)
            display_markdown(response_md)


# --------------------------
# Entry point
# --------------------------
if __name__ == "__main__":
    run_app()

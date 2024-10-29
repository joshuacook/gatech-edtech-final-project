# frontend/Home.py

import streamlit as st

def main():
    st.set_page_config(
        page_title="Chelle Knowledge Management",
        page_icon="🧠",
        layout="wide"
    )
    
    st.title("🧠 Chelle Knowledge Management")
    
    st.markdown("""
    ### Welcome to Chelle Knowledge Management System
    
    This system helps organizations manage their knowledge through three main components:
    
    1. **📚 Concepts Management**
       - Define and organize organizational knowledge
       - Manage definitions, citations, and understanding levels
    
    2. **🔗 Relationships Management**
       - Create and manage connections between concepts
       - Visualize knowledge networks
    
    3. **⚙️ Operational Elements**
       - Implement concepts in practical contexts
       - Manage procedures, tools, and validations
    
    Navigate through these components using the sidebar menu.
    """)
    
    # Display some example stats in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Total Concepts", value="25", delta="2 new")
    
    with col2:
        st.metric(label="Relationships", value="43", delta="5 new")
    
    with col3:
        st.metric(label="Implementations", value="12", delta="1 new")

if __name__ == "__main__":
    main()
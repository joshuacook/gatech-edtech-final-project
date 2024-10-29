# frontend/pages/1_Concepts.py

import streamlit as st
import pandas as pd
from datetime import datetime

from utils.session_state import init_session_state

def init_session_state():
    if 'concepts' not in st.session_state:
        st.session_state.concepts = {
            'User': {
                'definition': 'A User is an individual person who is using the product via a logged in account.',
                'citations': ['Users are managed externally to the product, via Clerk.',
                            'Users can be either Mentors or Learners.'],
                'synonyms': ['Account Holder', 'System User'],
                'created_at': '2024-10-28',
                'understanding_level': 'Practical'
            },
            'Organization': {
                'definition': 'An Organization is a group of Users that use the product in tandem.',
                'citations': ['Organizations are managed externally to the product, via Clerk.',
                            'It is not possible to use Chelle and not belong to an Organization'],
                'synonyms': ['Company', 'Team'],
                'created_at': '2024-10-28',
                'understanding_level': 'Proficient'
            }
        }

def create_concept():
    with st.form("new_concept_form"):
        concept_name = st.text_input("Concept Name")
        definition = st.text_area("Definition")
        citations = st.text_area("Citations (one per line)")
        synonyms = st.text_input("Synonyms (comma-separated)")
        understanding_level = st.selectbox(
            "Understanding Level",
            ["None", "Functional", "Practical", "Proficient"]
        )
        
        submit_button = st.form_submit_button("Create Concept")
        
        if submit_button and concept_name:
            st.session_state.concepts[concept_name] = {
                'definition': definition,
                'citations': citations.split('\n') if citations else [],
                'synonyms': [s.strip() for s in synonyms.split(',')] if synonyms else [],
                'created_at': datetime.now().strftime('%Y-%m-%d'),
                'understanding_level': understanding_level
            }
            st.success(f"Created concept: {concept_name}")

def view_concepts():
    if st.session_state.concepts:
        concept_list = list(st.session_state.concepts.keys())
        selected_concept = st.selectbox("Select Concept", concept_list)
        
        if selected_concept:
            concept = st.session_state.concepts[selected_concept]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### Definition")
                st.write(concept['definition'])
                
                st.markdown("### Citations")
                for citation in concept['citations']:
                    st.write(f"• {citation}")
            
            with col2:
                st.markdown("### Metadata")
                st.write(f"**Created:** {concept['created_at']}")
                st.write(f"**Understanding Level:** {concept['understanding_level']}")
                
                st.markdown("### Synonyms")
                for synonym in concept['synonyms']:
                    st.write(f"• {synonym}")
                
            if st.button("Edit Concept"):
                st.session_state.editing = selected_concept

def edit_concept(concept_name):
    concept = st.session_state.concepts[concept_name]
    
    with st.form("edit_concept_form"):
        st.write(f"Editing: {concept_name}")
        
        definition = st.text_area("Definition", value=concept['definition'])
        citations = st.text_area("Citations", value='\n'.join(concept['citations']))
        synonyms = st.text_input("Synonyms", value=', '.join(concept['synonyms']))
        understanding_level = st.selectbox(
            "Understanding Level",
            ["None", "Functional", "Practical", "Proficient"],
            index=["None", "Functional", "Practical", "Proficient"].index(concept['understanding_level'])
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("Save Changes")
        with col2:
            cancel = st.form_submit_button("Cancel")
        
        if submit:
            st.session_state.concepts[concept_name].update({
                'definition': definition,
                'citations': citations.split('\n') if citations else [],
                'synonyms': [s.strip() for s in synonyms.split(',')] if synonyms else [],
                'understanding_level': understanding_level
            })
            st.session_state.editing = None
            st.success("Changes saved!")
            st.rerun()
            
        if cancel:
            st.session_state.editing = None
            st.rerun()

def main():
    st.title("📚 Concepts Management")
    
    init_session_state()
    
    action = st.sidebar.radio(
        "Concept Actions",
        ["View Concepts", "Create New Concept"]
    )
    
    if action == "View Concepts":
        if 'editing' in st.session_state and st.session_state.editing:
            edit_concept(st.session_state.editing)
        else:
            view_concepts()
    else:
        create_concept()
    
    st.sidebar.markdown("### Concept Overview")
    if st.session_state.concepts:
        df = pd.DataFrame([
            {
                'Concept': k,
                'Understanding': v['understanding_level'],
                'Created': v['created_at']
            }
            for k, v in st.session_state.concepts.items()
        ])
        st.sidebar.dataframe(df, hide_index=True)

if __name__ == "__main__":
    main()
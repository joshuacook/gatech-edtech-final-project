# frontend/pages/3_Operational_Elements.py

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.session_state import init_session_state

def init_operational_state():
    init_session_state()
    
    if 'implementations' not in st.session_state:
        st.session_state.implementations = {
            'Primary Brand Colors': {
                'type': 'Implementation',
                'description': 'Core brand color palette',
                'details': {
                    'Slate Blue': '#5B7C99',
                    'Apricot': '#ED820E'
                },
                'concept': 'Brand',
                'status': 'Active',
                'created_at': '2024-10-28'
            },
            'Sales Pipeline Setup': {
                'type': 'Implementation',
                'description': 'Hubspot deal stages configuration',
                'details': {
                    'Prospecting': '10%',
                    'Qualification': '25%',
                    'Proposal': '50%',
                    'Negotiation': '75%',
                    'Closed': '100%'
                },
                'concept': 'Sales Process',
                'status': 'Active',
                'created_at': '2024-10-28'
            }
        }
    
    if 'procedures' not in st.session_state:
        st.session_state.procedures = {
            'Lead Qualification': {
                'type': 'Procedure',
                'steps': [
                    'Check company size and industry match',
                    'Verify budget authority',
                    'Score against ideal customer profile',
                    'Route to appropriate sales team'
                ],
                'concept': 'Sales Process',
                'status': 'Active',
                'created_at': '2024-10-28'
            }
        }
    
    if 'tools' not in st.session_state:
        st.session_state.tools = {
            'Figma': {
                'type': 'Tool',
                'purpose': 'UI/UX implementation',
                'concepts': ['Design System', 'User Interface'],
                'status': 'Active',
                'created_at': '2024-10-28'
            },
            'HubSpot': {
                'type': 'Tool',
                'purpose': 'CRM implementation',
                'concepts': ['Sales Process', 'Customer Management'],
                'status': 'Active',
                'created_at': '2024-10-28'
            }
        }

def create_implementation():
    st.subheader("Create Implementation")
    
    with st.form("implementation_form"):
        name = st.text_input("Implementation Name")
        description = st.text_area("Description")
        
        st.write("Implementation Details")
        num_details = st.number_input("Number of detail fields", min_value=1, value=1)
        details = {}
        for i in range(num_details):
            col1, col2 = st.columns(2)
            with col1:
                key = st.text_input(f"Key {i+1}")
            with col2:
                value = st.text_input(f"Value {i+1}")
            if key and value:
                details[key] = value
        
        concept = st.selectbox("Related Concept", options=list(st.session_state.concepts.keys()))
        status = st.selectbox("Status", options=["Active", "Draft", "Archived"])
        
        submit = st.form_submit_button("Create Implementation")
        
        if submit and name and description:
            st.session_state.implementations[name] = {
                'type': 'Implementation',
                'description': description,
                'details': details,
                'concept': concept,
                'status': status,
                'created_at': datetime.now().strftime('%Y-%m-%d')
            }
            st.success(f"Implementation '{name}' created successfully!")
            st.rerun()

def create_procedure():
    st.subheader("Create Procedure")
    
    with st.form("procedure_form"):
        name = st.text_input("Procedure Name")
        
        st.write("Procedure Steps")
        num_steps = st.number_input("Number of steps", min_value=1, value=1)
        steps = []
        for i in range(num_steps):
            step = st.text_input(f"Step {i+1}")
            if step:
                steps.append(step)
        
        concept = st.selectbox("Related Concept", options=list(st.session_state.concepts.keys()))
        status = st.selectbox("Status", options=["Active", "Draft", "Archived"])
        
        submit = st.form_submit_button("Create Procedure")
        
        if submit and name and steps:
            st.session_state.procedures[name] = {
                'type': 'Procedure',
                'steps': steps,
                'concept': concept,
                'status': status,
                'created_at': datetime.now().strftime('%Y-%m-%d')
            }
            st.success(f"Procedure '{name}' created successfully!")
            st.rerun()

def create_tool():
    st.subheader("Create Tool")
    
    with st.form("tool_form"):
        name = st.text_input("Tool Name")
        purpose = st.text_area("Purpose")
        
        concepts = st.multiselect(
            "Related Concepts",
            options=list(st.session_state.concepts.keys())
        )
        
        status = st.selectbox("Status", options=["Active", "Draft", "Archived"])
        
        submit = st.form_submit_button("Create Tool")
        
        if submit and name and purpose and concepts:
            st.session_state.tools[name] = {
                'type': 'Tool',
                'purpose': purpose,
                'concepts': concepts,
                'status': status,
                'created_at': datetime.now().strftime('%Y-%m-%d')
            }
            st.success(f"Tool '{name}' created successfully!")
            st.rerun()

def view_implementations():
    st.subheader("Implementations")
    
    if st.session_state.implementations:
        for name, impl in st.session_state.implementations.items():
            with st.expander(f"📦 {name}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Description:**", impl['description'])
                    st.write("**Details:**")
                    for key, value in impl['details'].items():
                        st.write(f"- {key}: {value}")
                
                with col2:
                    st.write("**Concept:**", impl['concept'])
                    st.write("**Status:**", impl['status'])
                    st.write("**Created:**", impl['created_at'])
    else:
        st.info("No implementations defined yet.")

def view_procedures():
    st.subheader("Procedures")
    
    if st.session_state.procedures:
        for name, proc in st.session_state.procedures.items():
            with st.expander(f"📝 {name}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Steps:**")
                    for i, step in enumerate(proc['steps'], 1):
                        st.write(f"{i}. {step}")
                
                with col2:
                    st.write("**Concept:**", proc['concept'])
                    st.write("**Status:**", proc['status'])
                    st.write("**Created:**", proc['created_at'])
    else:
        st.info("No procedures defined yet.")

def view_tools():
    st.subheader("Tools")
    
    if st.session_state.tools:
        for name, tool in st.session_state.tools.items():
            with st.expander(f"🔧 {name}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Purpose:**", tool['purpose'])
                    st.write("**Related Concepts:**")
                    for concept in tool['concepts']:
                        st.write(f"- {concept}")
                
                with col2:
                    st.write("**Status:**", tool['status'])
                    st.write("**Created:**", tool['created_at'])
    else:
        st.info("No tools defined yet.")

def view_operational_summary():
    st.subheader("Operational Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Implementations",
            len(st.session_state.implementations),
            f"{len([i for i in st.session_state.implementations.values() if i['status'] == 'Active'])} active"
        )
    
    with col2:
        st.metric(
            "Procedures",
            len(st.session_state.procedures),
            f"{len([p for p in st.session_state.procedures.values() if p['status'] == 'Active'])} active"
        )
    
    with col3:
        st.metric(
            "Tools",
            len(st.session_state.tools),
            f"{len([t for t in st.session_state.tools.values() if t['status'] == 'Active'])} active"
        )
    
    st.subheader("Concept Coverage")
    
    concept_coverage = {}
    for concept in st.session_state.concepts:
        implementations = len([i for i in st.session_state.implementations.values() if i['concept'] == concept])
        procedures = len([p for p in st.session_state.procedures.values() if p['concept'] == concept])
        tools = len([t for t in st.session_state.tools.values() if concept in t['concepts']])
        
        concept_coverage[concept] = {
            'Implementations': implementations,
            'Procedures': procedures,
            'Tools': tools,
            'Total Coverage': implementations + procedures + tools
        }
    
    coverage_df = pd.DataFrame(concept_coverage).T
    st.dataframe(coverage_df)

def main():
    st.title("⚙️ Operational Elements")
    
    init_operational_state()
    
    action = st.sidebar.radio(
        "Operational Actions",
        ["View Elements", "Create Implementation", "Create Procedure", "Create Tool"]
    )
    
    if action == "View Elements":
        view_operational_summary()
        view_implementations()
        view_procedures()
        view_tools()
    elif action == "Create Implementation":
        create_implementation()
    elif action == "Create Procedure":
        create_procedure()
    else:  # Create Tool
        create_tool()

if __name__ == "__main__":
    main()
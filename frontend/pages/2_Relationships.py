# frontend/pages/2_Relationships.py

import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from datetime import datetime
from utils.session_state import init_session_state  # Import the session state initialization

def init_relationship_state():
    init_session_state()
    
    if 'relationships' not in st.session_state:
        st.session_state.relationships = {
            ('User', 'Organization'): {
                'type': 'Related',
                'connection_type': 'Functional',
                'strength': 0.4,
                'created_at': '2024-10-28'
            },
            ('Concept', 'Definition'): {
                'type': 'Subsumption',
                'strength': 0.8,
                'created_at': '2024-10-28'
            }
        }
    
    if 'relationship_types' not in st.session_state:
        st.session_state.relationship_types = {
            'Equivalence': 1.0,
            'Subsumption': 0.8,
            'Overlap': 0.6,
            'Related': 0.4,
            'Disjoint': 0.2,
            'None': 0.0
        }
    
    if 'connection_types' not in st.session_state:
        st.session_state.connection_types = [
            'Causal',
            'Temporal',
            'Spatial',
            'Functional'
        ]

def create_relationship():
    st.subheader("Create New Relationship")
    
    if len(st.session_state.concepts) < 2:
        st.warning("Please create at least two concepts before creating relationships.")
        return
    
    with st.form("new_relationship_form"):
        concepts = list(st.session_state.concepts.keys())
        
        col1, col2 = st.columns(2)
        with col1:
            source = st.selectbox("Source Concept", concepts, key="source")
        with col2:
            target = st.selectbox("Target Concept", concepts, key="target")
            
        relationship_type = st.selectbox(
            "Relationship Type",
            list(st.session_state.relationship_types.keys())
        )
        
        connection_type = None
        if relationship_type == 'Related':
            connection_type = st.selectbox(
                "Connection Type",
                st.session_state.connection_types
            )
        
        strength = st.session_state.relationship_types[relationship_type]
        st.write(f"Relationship Strength: {strength}")
        
        submit = st.form_submit_button("Create Relationship")
        
        if submit:
            if source == target:
                st.error("Cannot create a relationship between a concept and itself.")
            elif (source, target) in st.session_state.relationships or (target, source) in st.session_state.relationships:
                st.error("A relationship already exists between these concepts.")
            else:
                relationship = {
                    'type': relationship_type,
                    'strength': strength,
                    'created_at': datetime.now().strftime('%Y-%m-28')
                }
                if connection_type:
                    relationship['connection_type'] = connection_type
                    
                st.session_state.relationships[(source, target)] = relationship
                st.success("Relationship created successfully!")
                st.rerun()

def visualize_relationships():
    st.subheader("Concept Network")
    
    if not st.session_state.concepts:
        st.info("No concepts available. Please create some concepts first.")
        return
    
    G = nx.Graph()
    
    for concept in st.session_state.concepts:
        G.add_node(concept)
    
    for (source, target), rel in st.session_state.relationships.items():
        G.add_edge(
            source, 
            target, 
            weight=rel['strength'],
            title=f"{rel['type']}: {rel.get('connection_type', '')}"
        )
    
    if len(G.nodes()) > 0:
        pos = nx.spring_layout(G)
        
        edge_x = []
        edge_y = []
        edge_text = []
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_text.append(edge[2]['title'])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='text',
            text=edge_text,
            mode='lines'
        )
        
        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="top center",
            marker=dict(
                size=20,
                color='#1f77b4',
                line_width=2
            )
        )
        
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=0, l=0, r=0, t=0),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No relationships to visualize yet.")

def view_relationships():
    st.subheader("Relationship List")
    
    if st.session_state.relationships:
        relationships_df = pd.DataFrame([
            {
                'Source': source,
                'Target': target,
                'Type': rel['type'],
                'Connection': rel.get('connection_type', ''),
                'Strength': rel['strength'],
                'Created': rel['created_at']
            }
            for (source, target), rel in st.session_state.relationships.items()
        ])
        
        st.dataframe(
            relationships_df,
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No relationships defined yet.")

def main():
    st.title("🔗 Relationships Management")
    
    init_relationship_state()
    
    action = st.sidebar.radio(
        "Relationship Actions",
        ["View Network", "Create Relationship"]
    )
    
    if action == "View Network":
        visualize_relationships()
        
        view_relationships()
        
        if st.session_state.relationships:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Total Relationships",
                    len(st.session_state.relationships)
                )
            with col2:
                avg_strength = sum(r['strength'] for r in st.session_state.relationships.values()) / len(st.session_state.relationships)
                st.metric(
                    "Average Strength",
                    f"{avg_strength:.2f}"
                )
            with col3:
                st.metric(
                    "Network Density",
                    f"{len(st.session_state.relationships) / (len(st.session_state.concepts) * (len(st.session_state.concepts) - 1) / 2):.2%}" if len(st.session_state.concepts) > 1 else "0%"
                )
    else:
        create_relationship()

if __name__ == "__main__":
    main()
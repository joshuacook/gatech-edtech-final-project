# frontend/utils/session_state.py

import streamlit as st
from datetime import datetime

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
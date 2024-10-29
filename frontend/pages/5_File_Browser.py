# frontend/pages/5_File_Browser.py

import os
import streamlit as st
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
import json

def init_mongo():
    """Initialize MongoDB connection"""
    client = MongoClient(os.getenv('MONGODB_URI'))
    return client['chelle']

def format_size(size_in_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} TB"

def view_file_details(asset):
    """Display detailed information about a file"""
    st.subheader(f"📄 {asset['original_name']}")
    
    # Basic Info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("File Size", format_size(asset['file_size']))
    with col2:
        st.metric("Upload Date", asset['upload_date'].strftime("%Y-%m-%d"))
    with col3:
        status_color = "🟢" if asset.get('processed', False) else "🟡"
        st.metric("Status", f"{status_color} {'Processed' if asset.get('processed', False) else 'Processing'}")
    
    # File Details Tab
    with st.expander("File Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Original Name:**", asset['original_name'])
            st.write("**File Type:**", asset['file_type'])
            st.write("**File Hash:**", asset['file_hash'])
        with col2:
            st.write("**Stored Name:**", asset['stored_name'])
            st.write("**Status:**", asset['status'])
            if 'page_count' in asset:
                st.write("**Page Count:**", asset['page_count'])
    
    # Processing Results
    if asset.get('processed', False) and 'processed_paths' in asset:
        with st.expander("Processing Results"):
            # Markdown Content Preview
            if 'markdown' in asset['processed_paths']:
                st.markdown("### Content Preview")
                try:
                    with open(asset['processed_paths']['markdown'], 'r') as f:
                        content = f.read()
                        st.markdown(content[:500] + "..." if len(content) > 500 else content)
                except Exception as e:
                    st.error(f"Error reading markdown: {str(e)}")
            
            # Images
            if 'images' in asset['processed_paths'] and asset['processed_paths']['images']:
                st.markdown("### Images")
                image_cols = st.columns(3)
                for idx, (img_name, img_path) in enumerate(asset['processed_paths']['images'].items()):
                    with image_cols[idx % 3]:
                        st.write(f"**{img_name}**")
                        try:
                            with open(img_path, 'rb') as f:
                                st.image(f.read(), use_column_width=True)
                        except Exception as e:
                            st.error(f"Error loading image: {str(e)}")
            
            # Metadata
            if 'meta' in asset['processed_paths']:
                st.markdown("### Metadata")
                try:
                    with open(asset['processed_paths']['meta'], 'r') as f:
                        meta_data = json.load(f)
                        st.json(meta_data)
                except Exception as e:
                    st.error(f"Error reading metadata: {str(e)}")

def main():
    st.title("📚 File Browser")
    
    db = init_mongo()
    raw_assets = db['raw_assets']
    
    # Fetch all assets
    assets = list(raw_assets.find().sort('upload_date', -1))
    
    if not assets:
        st.info("No files have been uploaded yet.")
        return
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Files", len(assets))
    with col2:
        processed = sum(1 for a in assets if a.get('processed', False))
        st.metric("Processed", f"{processed}/{len(assets)}")
    with col3:
        total_size = sum(a['file_size'] for a in assets)
        st.metric("Total Size", format_size(total_size))
    with col4:
        avg_pages = sum(a.get('page_count', 0) for a in assets) / len(assets)
        st.metric("Avg Pages", f"{avg_pages:.1f}")
    
    # Create files table
    files_df = pd.DataFrame([
        {
            'File Name': asset['original_name'],
            'Upload Date': asset['upload_date'].strftime("%Y-%m-%d %H:%M"),
            'Size': format_size(asset['file_size']),
            'Status': '🟢 Processed' if asset.get('processed', False) else '🟡 Processing',
            'Pages': asset.get('page_count', '-'),
            '_id': str(asset['_id'])
        }
        for asset in assets
    ])
    
    # Allow user to select a file from the table
    selected_indices = st.data_editor(
        files_df.drop('_id', axis=1),
        hide_index=True,
        width=None,
        height=400,
        use_container_width=True,
        column_config={
            "File Name": st.column_config.TextColumn(
                "File Name",
                width="large",
            ),
            "Upload Date": st.column_config.TextColumn(
                "Upload Date",
                width="medium",
            ),
            "Size": st.column_config.TextColumn(
                "Size",
                width="small",
            ),
            "Status": st.column_config.TextColumn(
                "Status",
                width="medium",
            ),
            "Pages": st.column_config.TextColumn(
                "Pages",
                width="small",
            ),
        },
        key="file_table"
    )
    
    if st.session_state.file_table:
        selected_idx = st.session_state.file_table['edited_rows']
        if selected_idx:
            idx = list(selected_idx.keys())[0]
            selected_id = files_df.iloc[idx]['_id']
            selected_asset = raw_assets.find_one({'_id': selected_id})
            if selected_asset:
                view_file_details(selected_asset)

if __name__ == "__main__":
    main()
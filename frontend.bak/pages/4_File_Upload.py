import os
import streamlit as st
from datetime import datetime
from pymongo import MongoClient
import hashlib
from redis import Redis
from rq import Queue

def init_mongo():
    """Initialize MongoDB connection"""
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client['chelle']
    return db

def init_redis():
    """Initialize Redis connection"""
    return Redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379'))

def save_file(uploaded_file, file_store_path):
    """Save file to local filestore and return file details"""
    file_hash = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
    
    file_extension = os.path.splitext(uploaded_file.name)[1]
    filename = f"{file_hash}{file_extension}"
    
    raw_dir = os.path.join(file_store_path, 'raw')
    os.makedirs(raw_dir, exist_ok=True)
    filepath = os.path.join(raw_dir, filename)
    
    with open(filepath, 'wb') as f:
        f.write(uploaded_file.getvalue())
    
    return {
        'original_name': uploaded_file.name,
        'stored_name': filename,
        'file_path': filepath,
        'file_hash': file_hash,
        'file_type': uploaded_file.type,
        'file_size': uploaded_file.size
    }

def main():
    st.title("📝 File Upload")
    
    db = init_mongo()
    redis_conn = Redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379'))
    q = Queue(connection=redis_conn)
    
    raw_assets = db['raw_assets']
    
    FILE_STORE_PATH = os.path.join(os.getcwd(), 'filestore')
    
    uploaded_file = st.file_uploader(
        "Choose a file to upload",
        type=['txt', 'pdf', 'doc', 'docx', 'md']
    )
    
    if uploaded_file:
        st.write("File Details:")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {uploaded_file.name}")
            st.write(f"**Type:** {uploaded_file.type}")
        with col2:
            st.write(f"**Size:** {uploaded_file.size/1024:.2f} KB")
        
        if st.button("Upload File"):
            with st.spinner("Processing file..."):
                try:
                    file_details = save_file(uploaded_file, FILE_STORE_PATH)
                    
                    asset_record = {
                        'original_name': file_details['original_name'],
                        'stored_name': file_details['stored_name'],
                        'file_path': file_details['file_path'],
                        'file_hash': file_details['file_hash'],
                        'file_type': file_details['file_type'],
                        'file_size': file_details['file_size'],
                        'upload_date': datetime.now(),
                        'status': 'uploaded',
                        'processed': False
                    }
                    
                    result = raw_assets.insert_one(asset_record)
                    
                    job = q.enqueue('jobs.process_with_marker', file_details['file_hash'])
                    
                    st.success(f"File uploaded successfully! Asset ID: {result.inserted_id}")
                    st.info(f"Marker processing job queued (Job ID: {job.id})")
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
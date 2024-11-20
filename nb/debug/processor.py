import json
import logging
from datetime import datetime
import requests
from jobs.assets.base import AssetProcessor
from utils.db_utils import init_mongo
from langfuse import Langfuse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_debug_session(file_hash: str):
    """Setup a new debug processing session for an asset"""
    run_id = f"debug-{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # Update asset with debug run_id
    db = init_mongo()
    db["raw_assets"].update_one(
        {"file_hash": file_hash},
        {"$set": {"current_run_id": run_id}}
    )
    
    # Initialize trace
    trace = Langfuse().trace(
        name="asset-processing-debug",
        id=run_id,
        metadata={
            "file_hash": file_hash,
            "debug_session": True,
            "timestamp": datetime.now().isoformat()
        }
    )
    
    print(f"Debug session initialized with run_id: {run_id}")
    return run_id, trace

async def execute_single_processor(file_hash: str, processor_type: str, run_id: str):
    """Execute a single processor and return its results"""
    processor = AssetProcessor(file_hash, processor_type)
    
    # Create span for this processor
    span = processor.trace.span(
        name=f"{processor_type}_processing_debug",
        metadata={
            "processor_type": processor_type,
            "dependencies": AssetProcessor.PROCESSOR_REGISTRY[processor_type],
            "debug_execution": True
        }
    )
    
    try:
        # Get asset data first
        db = init_mongo()
        asset = db["raw_assets"].find_one({"file_hash": file_hash})
        if not asset:
            raise Exception(f"Asset not found: {file_hash}")
            
        # Make API call to processor endpoint
        headers = {"X-Span-ID": span.id, "X-Run-ID": run_id}
        response = requests.post(
            f"http://nginx:80/assets/process_{processor_type}/{file_hash}",
            headers=headers
        )
        
        if not response.ok:
            raise Exception(f"Processing failed with status {response.status_code}: {response.text}")
            
        result = response.json()
        
        # Print detailed results based on processor type
        print(f"\nResults for {processor_type}:")
        if processor_type == "tables":
            print(f"Found {result.get('table_count', 0)} tables")
            if result.get('table_paths'):
                print("Table paths:", json.dumps(result['table_paths'], indent=2))
        elif processor_type == "images":
            print(f"Found {result.get('image_count', 0)} images")
        elif processor_type == "refined":
            print("Content processed and saved")
            if 'processed_paths' in asset:
                print("Processed paths:", json.dumps(asset['processed_paths'], indent=2))
        elif processor_type == "refined_metadata":
            if 'metadata' in result:
                print("Metadata:", json.dumps(result['metadata'], indent=2))
        elif processor_type == "refined_splitting":
            if 'splitting' in result:
                print("Splitting recommendations:", json.dumps(result['splitting'], indent=2))
        elif processor_type == "lexemes":
            print(f"Found {len(asset.get('lexemes', []))} lexemes")
        elif processor_type == "citations":
            if 'citations' in result:
                print("Citations:", json.dumps(result['citations'], indent=2))
        elif processor_type == "definitions":
            print(f"Processed {result.get('definition_count', 0)} definitions")
            
        span.event(
            name=f"{processor_type}_completed",
            metadata={"result": result}
        )
        
        return result
        
    except Exception as e:
        error_msg = f"Error in {processor_type} processing: {str(e)}"
        print(f"\nERROR: {error_msg}")
        span.event(
            name=f"{processor_type}_error",
            metadata={"error": str(e)},
            level="error"
        )
        raise
    finally:
        span.end()

def check_processor_dependencies(processor_type: str, file_hash: str):
    """Check and display dependencies for a processor"""
    deps = AssetProcessor.PROCESSOR_REGISTRY[processor_type]
    print(f"\nProcessor: {processor_type}")
    print(f"Dependencies: {deps if deps else 'None'}")
    
    if deps:
        print("\nChecking dependency statuses:")
        db = init_mongo()
        asset = db["raw_assets"].find_one({"file_hash": file_hash})
        
        for dep in deps:
            status = "Unknown"
            if asset:
                if f"{dep}_complete" in asset.get("status", ""):
                    status = "Complete"
                elif f"{dep}_error" in asset.get("status", ""):
                    status = f"Error: {asset.get('error', 'Unknown error')}"
                elif f"processing_{dep}" in asset.get("status", ""):
                    status = "Processing"
            print(f"  - {dep}: {status}")
    
    return deps

def display_processing_dag(file_hash: str = None):
    """Display the full processing DAG"""
    print("Processing DAG:")
    print("\nInitial processors (no dependencies):")
    for proc, deps in AssetProcessor.PROCESSOR_REGISTRY.items():
        if not deps:
            print(f"  - {proc}")
    
    print("\nDependent processors:")
    for proc, deps in AssetProcessor.PROCESSOR_REGISTRY.items():
        if deps:
            print(f"  - {proc} (depends on: {deps})")
            
    if file_hash:
        print("\nCurrent asset status:")
        db = init_mongo()
        asset = db["raw_assets"].find_one({"file_hash": file_hash})
        if asset:
            print(f"Status: {asset.get('status', 'Unknown')}")
            print("\nProcessed paths:")
            for path_type, path in asset.get('processed_paths', {}).items():
                print(f"  - {path_type}: {path}")
        else:
            print(f"No asset found with hash: {file_hash}")

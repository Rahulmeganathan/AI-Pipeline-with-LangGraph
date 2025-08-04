#!/usr/bin/env python3
"""
Script to restart Streamlit app with cache clearing.
"""

import os
import subprocess
import sys
import time

def clear_cache_and_restart():
    """Clear Streamlit cache and restart the app."""
    
    print("🧹 Clearing Streamlit cache...")
    
    # Clear Streamlit cache
    try:
        subprocess.run(["streamlit", "cache", "clear"], check=True)
        print("✅ Streamlit cache cleared")
    except subprocess.CalledProcessError:
        print("⚠️  Could not clear cache via command")
    
    # Remove temporary data directories
    import glob
    temp_dirs = glob.glob("temp_data_*")
    for temp_dir in temp_dirs:
        try:
            import shutil
            shutil.rmtree(temp_dir)
            print(f"✅ Removed temporary directory: {temp_dir}")
        except Exception as e:
            print(f"⚠️  Could not remove {temp_dir}: {e}")
    
    # Clear Python cache
    try:
        import glob
        cache_files = glob.glob("**/__pycache__", recursive=True)
        for cache_dir in cache_files:
            try:
                import shutil
                shutil.rmtree(cache_dir)
                print(f"✅ Removed Python cache: {cache_dir}")
            except Exception:
                pass
    except Exception:
        pass
    
    print("\n🚀 Starting Streamlit app...")
    print("📝 Use Ctrl+C to stop the app")
    print("=" * 50)
    
    # Start the enhanced Streamlit app
    try:
        subprocess.run([
            "streamlit", "run", "ui/streamlit_app_enhanced.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Streamlit app stopped by user")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

if __name__ == "__main__":
    clear_cache_and_restart() 
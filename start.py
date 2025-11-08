#!/usr/bin/env python
"""Start script that ensures proper Python path before starting uvicorn"""
import sys
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change to script directory
os.chdir(script_dir)

# Add to Python path
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Set environment variable for subprocess
os.environ['PYTHONPATH'] = script_dir + os.pathsep + os.environ.get('PYTHONPATH', '')

if __name__ == "__main__":
    import uvicorn
    
    # Verify we can import the app
    try:
        from app.main import app
        print(f"Starting server from: {os.getcwd()}")
        print("Server will be available at: http://localhost:8000")
        print("API docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop the server\n")
        
        # For reload to work, we need to pass the app as an import string
        # But we also need to ensure PYTHONPATH is set for the subprocess
        # So we'll use uvicorn's CLI interface with proper environment
        import subprocess
        
        # Set environment for subprocess
        env = os.environ.copy()
        env['PYTHONPATH'] = script_dir + os.pathsep + env.get('PYTHONPATH', '')
        
        # Run uvicorn as subprocess with import string
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, env_file=None)
    except ImportError as e:
        print(f"ERROR: Cannot import app module: {e}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


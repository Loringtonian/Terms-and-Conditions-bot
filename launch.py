#!/usr/bin/env python3
"""
Full-stack launcher for both the Flask backend and Next.js frontend.
Run this script directly from your IDE to start both development servers.
"""
import os
import sys
import subprocess
import signal
import time
from pathlib import Path
from threading import Thread

def run_backend(base_dir):
    """Run the Flask backend server"""
    print("🔥 Starting Flask backend server...")
    backend_script = base_dir / 'src' / 'terms_analyzer' / 'api' / 'app.py'
    
    if not backend_script.exists():
        print(f"❌ Error: Backend script not found at {backend_script}")
        return
    
    try:
        os.chdir(base_dir)
        # Run as module to fix import issues
        subprocess.run(['python', '-m', 'src.terms_analyzer.api.app'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting backend server: {e}")
    except Exception as e:
        print(f"\n❌ Backend server error: {e}")

def run_frontend(base_dir):
    """Run the Next.js frontend server"""
    print("🌐 Starting Next.js frontend server...")
    frontend_dir = base_dir / 'frontend'
    
    if not frontend_dir.exists():
        print(f"❌ Error: 'frontend' directory not found at {frontend_dir}")
        return
    
    try:
        os.chdir(frontend_dir)
        subprocess.run(['npm', 'run', 'dev'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting frontend server: {e}")
    except Exception as e:
        print(f"\n❌ Frontend server error: {e}")

def main():
    print("🚀 Starting full-stack development servers...")
    
    # Get the directory of this script
    base_dir = Path(__file__).parent.absolute()
    
    print(f"📂 Base directory: {base_dir}")
    print("🔥 Backend API will be available at: http://localhost:5001")
    print("🌐 Frontend will be available at: http://localhost:3000")
    print("\n🔄 Starting both servers...\n")
    
    # Start backend in a separate thread
    backend_thread = Thread(target=run_backend, args=(base_dir,), daemon=True)
    backend_thread.start()
    
    # Give backend a moment to start
    time.sleep(2)
    
    try:
        # Start frontend in main thread
        run_frontend(base_dir)
    except KeyboardInterrupt:
        print("\n👋 Development servers stopped.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

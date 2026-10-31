import subprocess
import time
import webbrowser
import os
import sys

def main():
    print("=" * 70)
    print(" ⚡ STARTING AI-POWERED DRIVING EFFICIENCY OPTIMIZER")
    print("    Backend:  FastAPI / Scikit-learn (http://127.0.0.1:8000)")
    print("    Frontend: Next.js 16 + React 19  (http://127.0.0.1:3000)")
    print("=" * 70)

    # 1. Start Python ML backend
    print("\n[1/2] Starting Python FastAPI & Scikit-learn Backend...")
    backend_proc = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT
    )

    # 2. Start Next.js frontend
    print("[2/2] Starting Next.js Frontend Server...")
    frontend_proc = subprocess.Popen(
        "npm --prefix frontend run dev",
        shell=True
    )

    # Wait for servers to spin up and open browser
    time.sleep(3.5)
    url = "http://localhost:3000"
    print(f"\n🚀 Opening Next.js Dashboard in browser: {url} ...")
    webbrowser.open(url)
    print("\nSystem running! Press Ctrl+C to stop both servers.")

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    main()


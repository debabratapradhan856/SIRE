import webbrowser
import threading
import time
import uvicorn

def open_browser():
    time.sleep(1.5)
    url = "http://127.0.0.1:8000"
    print(f"\nOpening Dashboard in browser: {url} ...")
    webbrowser.open(url)

if __name__ == "__main__":
    print("=" * 70)
    print(" ⚡ AI-POWERED DRIVING EFFICIENCY OPTIMIZER DASHBOARD")
    print("=" * 70)
    print(" Starting FastAPI backend and web interface on http://127.0.0.1:8000")
    print(" Press CTRL+C to stop the server.\n")

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("app:app", host="127.0.0.1", port=8000, log_level="info")


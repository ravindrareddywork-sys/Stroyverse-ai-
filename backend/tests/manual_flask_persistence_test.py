"""
StoryVerse AI — Live Flask Process Lifecycle & ChromaDB Persistence Test
========================================================================
Performs a genuine operating-system level process lifecycle test:
  1. Starts Flask server in a subprocess.
  2. Ingests a unique knowledge document via HTTP POST /api/rag/ingest.
  3. Completely terminates and kills the Flask server process.
  4. Starts a fresh Flask server subprocess.
  5. Performs HTTP GET /api/rag/documents/<doc_id> and POST /api/rag/query.
  6. Confirms that ChromaDB persistent storage maintained the document across process restarts.
"""

import sys
import os
import time
import uuid
import subprocess
import requests

TEST_PORT = 5005
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


def wait_for_server(timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            res = requests.get(f"{BASE_URL}/api/health", timeout=1)
            if res.status_code == 200:
                return True
        except Exception:
            time.sleep(0.5)
    return False


def run_persistence_test():
    print("[1/6] Launching initial Flask server process on port", TEST_PORT)
    env = os.environ.copy()
    env["FLASK_RUN_PORT"] = str(TEST_PORT)
    env["PORT"] = str(TEST_PORT)
    env["AI_MOCK_MODE"] = "true"

    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    proc1 = subprocess.Popen(
        [sys.executable, "-c", f"""
from app import create_app
app = create_app('development')
app.run(host='127.0.0.1', port={TEST_PORT}, debug=False)
"""],
        cwd=backend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        if not wait_for_server(20):
            stdout, stderr = proc1.communicate(timeout=2)
            print("Failed to start server 1. Stderr:", stderr.decode())
            sys.exit(1)
        print("  -> Flask Server 1 is LIVE and healthy.")

        unique_id = uuid.uuid4().hex[:8]
        unique_title = f"Chroma Persistence Document {unique_id}"
        unique_content = f"The sacred chronocrystal chamber {unique_id} remains sealed in the deep vaults."

        print(f"[2/6] Ingesting unique document via POST {BASE_URL}/api/rag/ingest")
        payload = {
            "title": unique_title,
            "content": unique_content,
            "doc_type": "lore",
            "genre": "fantasy",
            "language": "English"
        }
        res_ingest = requests.post(f"{BASE_URL}/api/rag/ingest", json=payload, timeout=5)
        assert res_ingest.status_code == 201, f"Ingest failed: {res_ingest.text}"
        doc_id = res_ingest.json()["data"]["document_id"]
        print(f"  -> Ingestion successful! Document ID: {doc_id}")

        print("[3/6] Completely terminating and stopping Flask Process 1...")
        proc1.terminate()
        try:
            proc1.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc1.kill()
            proc1.wait(timeout=2)
        print("  -> Flask Process 1 is confirmed STOPPED and DEAD.")

        # Verify server is down
        try:
            requests.get(f"{BASE_URL}/api/health", timeout=1)
            print("ERROR: Server is still responding after terminate!")
            sys.exit(1)
        except Exception:
            print("  -> Verified: Server is unreachable (Process successfully terminated).")

        print("[4/6] Starting a FRESH Flask server process (Process 2)...")
        proc2 = subprocess.Popen(
            [sys.executable, "-c", f"""
from app import create_app
app = create_app('development')
app.run(host='127.0.0.1', port={TEST_PORT}, debug=False)
"""],
            cwd=backend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            if not wait_for_server(20):
                stdout, stderr = proc2.communicate(timeout=2)
                print("Failed to start server 2. Stderr:", stderr.decode())
                sys.exit(1)
            print("  -> Fresh Flask Server 2 is LIVE and healthy.")

            print(f"[5/6] Querying restarted Flask server for document ID '{doc_id}'...")
            res_get = requests.get(f"{BASE_URL}/api/rag/documents/{doc_id}", timeout=5)
            assert res_get.status_code == 200, f"Document not found on restarted server! Status: {res_get.status_code}"
            doc_data = res_get.json()["data"]
            assert doc_data["title"] == unique_title
            assert unique_content in doc_data["content"]
            print(f"  -> SUCCESS: Retrieved document by ID after complete process restart!")

            print(f"[6/6] Executing semantic search on restarted Flask server...")
            res_query = requests.post(f"{BASE_URL}/api/rag/query", json={
                "query": f"chronocrystal chamber {unique_id}",
                "n_results": 2
            }, timeout=5)
            assert res_query.status_code == 200
            query_data = res_query.json()["data"]
            assert query_data["count"] >= 1
            retrieved_text = query_data["retrieved_chunks"][0]["text"]
            assert unique_id in retrieved_text
            print(f"  -> SUCCESS: Semantic vector search on restarted server successfully matched chunk!")

            # Cleanup document
            requests.delete(f"{BASE_URL}/api/rag/documents/{doc_id}", timeout=5)

            print("\n=======================================================")
            print("GENUINE FLASK PROCESS PERSISTENCE TEST: FULLY VERIFIED")
            print("=======================================================")

        finally:
            proc2.terminate()
            try:
                proc2.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc2.kill()
                proc2.wait(timeout=2)
            print("Cleaned up Flask Process 2.")

    finally:
        if proc1.poll() is None:
            proc1.kill()


if __name__ == "__main__":
    run_persistence_test()

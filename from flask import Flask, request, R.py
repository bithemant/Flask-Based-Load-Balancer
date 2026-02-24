from flask import Flask, request, Response
import requests
import threading

app = Flask(__name__)

# 3 backend servers
servers = [
    {"name": "Server 1", "url": "http://127.0.0.1:5001", "active": 0},
    {"name": "Server 2", "url": "http://127.0.0.1:5002", "active": 0},
    {"name": "Server 3", "url": "http://127.0.0.1:5003", "active": 0},
]

LOCK = threading.Lock()
counter = 0  # for round robin

def pick_server():
    global counter
    with LOCK:
        srv = servers[counter % len(servers)]
        counter += 1
        srv["active"] += 1
        return srv

@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def proxy(path):
    srv = pick_server()
    if not srv:
        return Response("⚠️ No servers available. Try again later.", status=503)

    try:
        # Forward request to chosen server
        target = f"{srv['url']}/{path}"
        resp = requests.request(
            request.method,
            target,
            headers={k: v for k, v in request.headers if k.lower() != "host"},
            data=request.get_data(),
            params=request.args,
            timeout=10,
        )

        # Add a clear message about which server handled it
        return Response(
            f"👉 You are served by {srv['name']} 👈\n\n{resp.text}",
            status=resp.status_code,
        )
    finally:
        with LOCK:
            srv["active"] -= 1

if __name__ == "__main__":
    print("🚦 Load Balancer running on http://127.0.0.1:8080")
    app.run(port=8080)

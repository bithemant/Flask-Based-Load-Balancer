from flask import Flask
import argparse

app = Flask(__name__)

@app.route("/")
def index():
    return f"Welcome! 🎉 You are on {app.config['NAME']}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--name", type=str, required=True)
    args = parser.parse_args()

    app.config["NAME"] = args.name
    app.run(host="0.0.0.0", port=args.port)

# Flask-Based Load Balancer

A small HTTP load balancer built with Flask that distributes incoming requests across three backend servers using round-robin routing — a hands-on demo of how traffic distribution works in distributed systems.

## What it does

Three Flask backend servers run on ports 5001, 5002 and 5003. The load balancer listens on port 8080 and forwards each incoming request to the next backend in turn (round robin), so traffic is spread evenly. The response tells you which server handled your request. The balancer also serves a playable Minesweeper game at `/game`.

## Features

- Round-robin request distribution across 3 backend servers
- Thread-safe server selection (a lock guards the shared counter)
- Active-connection tracking per server
- Proxies both GET and POST requests, including query parameters and request bodies
- 10-second timeout on upstream requests
- Returns a 503 response when no backend server is available
- Each proxied response is prefixed with the name of the server that handled it, so you can watch the rotation
- Built-in Minesweeper game at `/game` (8×8 board, 10 mines, click to reveal, right-click to flag)

## Tech stack

- Python
- Flask — backend servers and the load balancer itself
- `requests` — forwarding requests to backends
- `threading` — lock for thread-safe round-robin selection

## How to run

There is no `requirements.txt` in this repo, so install the two dependencies first:

```bash
pip install flask requests
```

Start the three backend servers (each in its own terminal):

```bash
python backend.py --port 5001 --name "Server 1"
python backend.py --port 5002 --name "Server 2"
python backend.py --port 5003 --name "Server 3"
```

Then start the load balancer:

```bash
python load_balancer.py
```

Open http://127.0.0.1:8080/ in your browser. Refresh a few times and watch the "You are served by Server 1 / 2 / 3" line rotate. Open http://127.0.0.1:8080/game to play Minesweeper.

To expose it publicly (optional):

```bash
ngrok http 8080
```

## Project structure

```
Flask-Based-Load-Balancer/
├── load_balancer.py   # Round-robin proxy on port 8080, plus the Minesweeper game at /game
├── backend.py         # Simple backend server; takes --port and --name arguments
├── index.html         # Leftover file in the repo, not used by the load balancer
└── README.md          # This file
```

# Python HTTP Load Balancer

## Overview
A custom HTTP load balancer built using Python and Flask.  
This project distributes incoming client requests across multiple backend servers using the Round Robin algorithm to simulate real-world traffic routing in distributed systems.

## Architecture
- Multiple backend servers running on different ports
- Central load balancer handling incoming requests
- Round Robin traffic distribution strategy

## How It Works
Incoming client requests are forwarded sequentially to backend servers in a cyclic order (Round Robin), ensuring even distribution of traffic.

## How to Run

### 1. Start Backend Servers
```
python backend.py --port 5001 --name "Server 1"
python backend.py --port 5002 --name "Server 2"
python backend.py --port 5003 --name "Server 3"
```

### 2. Start Load Balancer
```
python load_balancer.py
```

### 3. (Optional) Expose Using ngrok
```
ngrok http 8000
```

## Technologies Used
- Python
- Flask
- HTTP Routing
- Round Robin Load Balancing
- Basic Distributed Systems Concepts

## Objective
To demonstrate request routing and traffic distribution using a Round Robin load balancing strategy.

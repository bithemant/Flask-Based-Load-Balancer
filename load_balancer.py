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

# Serve Minesweeper game
@app.route("/game")
def game():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Professional Minesweeper</title>
        <style>
            body { font-family: Arial; text-align: center; background:#f0f2f5; }
            h1 { color:#333; }
            #game-container { display:inline-block; padding:20px; background:white; border-radius:10px; box-shadow:0 0 15px rgba(0,0,0,0.2); }
            table { border-collapse: collapse; margin:auto; }
            td { width:35px; height:35px; border:1px solid #999; text-align:center; vertical-align: middle; font-weight:bold; font-size:18px; cursor:pointer; user-select:none; }
            td.revealed { background:#ddd; cursor:default; }
            td.flag { background:#ffeb3b; color:red; }
            #info { margin:10px; font-size:16px; }
        </style>
    </head>
    <body>
        <h1>🎮 Professional Minesweeper</h1>
        <div id="game-container">
            <div id="info">
                Mines: <span id="mines-count">0</span> | Time: <span id="timer">0</span>s
            </div>
            <table id="board"></table>
        </div>
        <script>
        const ROWS=8, COLS=8, MINES=10;
        let board=[], revealedCount=0, flags=0, time=0, timerInterval;

        function initGame(){
            board = Array.from({length:ROWS},()=>Array(COLS).fill(0));
            revealedCount = 0; flags = 0;
            document.getElementById('mines-count').textContent = MINES;
            placeMines();
            renderBoard();
            clearInterval(timerInterval);
            time = 0;
            document.getElementById('timer').textContent = time;
            timerInterval = setInterval(()=>document.getElementById('timer').textContent = ++time, 1000);
        }

        function placeMines(){
            let placed=0;
            while(placed<MINES){
                let r=Math.floor(Math.random()*ROWS);
                let c=Math.floor(Math.random()*COLS);
                if(board[r][c]===0){board[r][c]='M'; placed++;}
            }
            for(let r=0;r<ROWS;r++){
                for(let c=0;c<COLS;c++){
                    if(board[r][c]!=='M'){
                        let count=0;
                        for(let i=-1;i<=1;i++){for(let j=-1;j<=1;j++){
                            let nr=r+i, nc=c+j;
                            if(nr>=0 && nr<ROWS && nc>=0 && nc<COLS && board[nr][nc]==='M') count++;
                        }}
                        board[r][c]=count;
                    }
                }
            }
        }

        function renderBoard(){
            const t = document.getElementById('board');
            t.innerHTML='';
            for(let r=0;r<ROWS;r++){
                const row=t.insertRow();
                for(let c=0;c<COLS;c++){
                    const cell=row.insertCell();
                    cell.addEventListener('click',()=>revealCell(r,c,cell));
                    cell.addEventListener('contextmenu', e=>{e.preventDefault(); toggleFlag(cell);});
                }
            }
        }

        function revealCell(r,c,cell){
            if(cell.classList.contains('revealed') || cell.classList.contains('flag')) return;
            cell.classList.add('revealed');
            if(board[r][c]==='M'){cell.textContent='💣'; alert('💥 Boom! Game Over!'); initGame();}
            else {
                cell.textContent = board[r][c] || '';
                revealedCount++;
                if(board[r][c]===0) revealAdjacent(r,c);
            }
        }

        function revealAdjacent(r,c){
            for(let i=-1;i<=1;i++){for(let j=-1;j<=1;j++){
                let nr=r+i, nc=c+j;
                if(nr>=0 && nr<ROWS && nc>=0 && nc<COLS){
                    let cell=document.getElementById('board').rows[nr].cells[nc];
                    if(!cell.classList.contains('revealed') && !cell.classList.contains('flag')){
                        cell.classList.add('revealed');
                        if(board[nr][nc]==='M'){cell.textContent='💣';}
                        else{cell.textContent=board[nr][nc]||''; if(board[nr][nc]===0) revealAdjacent(nr,nc);}
                        revealedCount++;
                    }
                }
            }}
        }

        function toggleFlag(cell){
            if(cell.classList.contains('revealed')) return;
            if(cell.classList.contains('flag')){cell.classList.remove('flag'); flags--;}
            else{cell.classList.add('flag'); flags++;}
            document.getElementById('mines-count').textContent = MINES - flags;
        }

        initGame();
        </script>
    </body>
    </html>
    '''
    return Response(html, mimetype="text/html")

# Proxy route (round-robin load balancer)
@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def proxy(path):
    # Skip /game route since it’s served above
    if path.startswith("game"):
        return game()

    srv = pick_server()
    if not srv:
        return Response("⚠️ No servers available. Try again later.", status=503)

    try:
        target = f"{srv['url']}/{path}"
        resp = requests.request(
            request.method,
            target,
            headers={k: v for k, v in request.headers if k.lower() != "host"},
            data=request.get_data(),
            params=request.args,
            timeout=10,
        )
        return Response(f"👉 You are served by {srv['name']} 👈\n\n{resp.text}", status=resp.status_code)
    finally:
        with LOCK:
            srv["active"] -= 1

if __name__ == "__main__":
    print("🚦 Load Balancer running on http://127.0.0.1:8080")
    app.run(port=8080)

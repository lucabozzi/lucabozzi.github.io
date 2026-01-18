import numpy as np
from numba import njit
from fastapi import FastAPI, WebSocket
import asyncio
import json

app = FastAPI()

N = 300
conf = np.random.choice([-1, 1], (N, N))

J, B, T, speed = 1.0, 0.0, 2.3, 1.0
paused = False

@njit
def calc_dE(conf, x, y, J, B):
    N = conf.shape[0]
    s = conf[x,y]
    nn = conf[(x+1)%N,y] + conf[(x-1)%N,y] + conf[x,(y+1)%N] + conf[x,(y-1)%N]
    return 2*J*s*nn - 2*B*s

@njit
def step(conf, J, B, T, speed):
    N = conf.shape[0]
    for _ in range(int(speed*N*N)):
        x = np.random.randint(0, N)
        y = np.random.randint(0, N)
        dE = calc_dE(conf, x, y, J, B)
        if dE <= 0 or np.random.rand() < np.exp(-dE/T):
            conf[x,y] *= -1

@app.websocket("/ws")
async def ws(ws: WebSocket):
    global J, B, T, speed, paused
    await ws.accept()
    while True:

        try:
            msg = await asyncio.wait_for(ws.receive_text(), timeout=0.0001)
            print("RECEIVED:", msg)
            data = json.loads(msg)
        
            if data["type"] == 'params':
                T = data["T"]
                J = data["J"]
                B = data["B"]
                speed = data["speed"]
                paused = data["paused"]
            print("RECEIVING")

        except asyncio.TimeoutError:
            pass

        if not paused:
            step(conf, J, B, T, speed)
        
        await ws.send_bytes(conf.astype(np.int8).tobytes())
        await asyncio.sleep(0.016)

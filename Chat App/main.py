from fastapi import FastAPI, WebSocket
from connection_manager import manager

app = FastAPI()

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    # accept connection
    await manager.connect(room_id, websocket)

    while True:
        try:
            data = await websocket.receive_text()
            await manager.boradcast(room_id, f"Room Id:{room_id}, Message: {data}")
        except Exception as e:
            print(f"WebSocket disconnected: {e}")
            break
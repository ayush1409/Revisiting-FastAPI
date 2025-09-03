from typing import Dict, Set
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        """Accept connection and add it to room"""
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(websocket)
    
    async def disconnect(self, room_id: str, websocket: WebSocket):
        """Disconnect the connection from room"""
        if room_id in self.rooms:
            self.rooms[room_id].discard(websocket)
            if not self.rooms[room_id]:
                del self.rooms[room_id]

    async def boradcast(self, room_id: str, message: str):
        """Broadcast the message to all connection in the same room"""
        if room_id in self.rooms:
            for ws in list(self.rooms[room_id]):
                try:
                    await ws.send_text(message)
                except Exception as e:
                    self.disconnect(room_id, ws)

manager = ConnectionManager()
    
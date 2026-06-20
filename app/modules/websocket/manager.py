from collections import defaultdict
from fastapi import WebSocket

class ConnectionManager:

    def __init__(self):
        self.connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: str, websocket: WebSocket):

        await websocket.accept()

        self.connections[user_id].add(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket):
        sockets: set[WebSocket] = self.connections.get(user_id)

        if not sockets:
            return
        
        sockets.discard(websocket)

        if not sockets:
            self.connections.pop(user_id, None)

    async def send_to_user(self, user_id: str, payload: dict):

        dead_connections = []

        websockets: set[WebSocket] = self.connections.get(user_id, set())

        for websocket in websockets.copy():
            try:
                await websocket.send_json(payload)

            except Exception:
                dead_connections.append(websocket)

        for websocket in dead_connections:
            self.disconnect(user_id, websocket)  

    async def broadcast(self, payload: dict):

        dead_connections: list[tuple[str, WebSocket]] = []

        for user_id, websockets in self.connections.items():

            for websocket in websockets.copy():
                try: 
                    await websocket.send_json(payload)

                except Exception:
                    dead_connections.append((user_id, websocket))

        for user_id, websocket in dead_connections:
            self.disconnect(user_id, websocket)


manager = ConnectionManager()
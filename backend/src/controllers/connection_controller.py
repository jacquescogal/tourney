from fastapi import WebSocket
from typing import List,Tuple,Dict

class ConnectionController:
    instance = None
    def __init__(self):
        self.active_connections: Dict[Tuple,List[WebSocket]] = {}

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = ConnectionController()
        return cls.instance
    
    async def connect(self, subscription, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[subscription] = self.active_connections.get(subscription,[])
        self.active_connections[subscription].append(websocket)

    def disconnect(self, subscription,websocket: WebSocket):
        self.active_connections.setdefault(subscription, [])
        self.active_connections[subscription].remove(websocket)

    async def broadcast(self, subscription,message: str):
        for connection in self.active_connections.get(subscription, []):
            await connection.send_text(message)
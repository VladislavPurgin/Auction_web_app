from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, lot_id: int):
        await websocket.accept()
        if lot_id not in self.active_connections:
            self.active_connections[lot_id] = []
        self.active_connections[lot_id].append(websocket)

    def disconnect(self, websocket: WebSocket, lot_id: int):
        if lot_id in self.active_connections:
            self.active_connections[lot_id].remove(websocket)
            # Якщо підключень більше немає — видаляємо ключ, щоб не їсти пам'ять
            if not self.active_connections[lot_id]:
                del self.active_connections[lot_id]

    async def broadcast(self, lot_id: int, message: dict):
        if lot_id in self.active_connections:
            for connection in self.active_connections[lot_id]:
                # Надсилаємо JSON всім підписаним клієнтам
                await connection.send_json(message)

# Створюємо один екземпляр для всього додатка (Singleton)
manager = ConnectionManager()
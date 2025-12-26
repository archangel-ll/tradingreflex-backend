from fastapi import WebSocket
from typing import List, Dict, Any


class ConnectionManager:
    """Manages WebSocket connections and broadcasting"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection and add it to the active connections"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection from active connections"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        await websocket.send_text(message)
    
    async def send_personal_json(self, data: Dict[Any, Any], websocket: WebSocket):
        """Send a JSON message to a specific WebSocket connection"""
        await websocket.send_json(data)
    
    async def broadcast(self, message: str):
        """Broadcast a text message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_json(self, data: Dict[Any, Any]):
        """Broadcast a JSON message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


# Global instance of the connection manager
manager = ConnectionManager()


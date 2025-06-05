from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_
from database import get_db
from models import Queue, Service

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[Connected] Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[Disconnected] Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)
            print("Sent to client")

manager = ConnectionManager()

@router.websocket("/ws/queue")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Optional: if you want clients to send anything
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def get(que):
    return {
        "queue_id": que.id,
        "number": que.number,
        "service": que.service.name,
        "time": str(que.time)
    }

@router.get("/waitlist")
async def get_waitlist(db: Session = Depends(get_db)):
   
    queues = db.query(Queue).filter(
        or_(Queue.step == 1, Queue.step == 2)
    ).all()

    return {
        'waiting': [get(que) for que in queues if que.step == 1],
        'meeting': [get(que) for que in queues if que.step == 2],
    }

@router.get("/call/{queue_id}")
async def call_ticket(queue_id: int, db: Session = Depends(get_db)):
    queue = db.query(Queue).filter_by(id=queue_id, step=1).first()
    if not queue:
        raise HTTPException(404, "Ticket not found")

    queue.step = 2
    db.commit()
    db.refresh(queue)

    await manager.broadcast({
        "type": "updated-ticket",
        "payload": get(queue)
    })

    raise HTTPException(200, "Called")

@router.post("/finish/{queue_id}")
async def finish_ticket(queue_id: int, db: Session = Depends(get_db)):
    queue = db.query(Queue).filter_by(id=queue_id, step=2).first()
    if not queue:
        raise HTTPException(404, "Ticket not found")

    queue.step = 3
    db.commit()
    db.refresh(queue)

    await manager.broadcast({
        "type": "finish-ticket",
        "payload": get(queue)
    })

    raise HTTPException(200, "Finished")

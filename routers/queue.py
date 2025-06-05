from fastapi_crudrouter import SQLAlchemyCRUDRouter as CRUDRouter
from fastapi import Depends, HTTPException, Query
from models import Queue, Service
from schemas import CreateQueueSchema, QueueSchema
from database import get_db
from sqlalchemy.orm import Session
import math
from datetime import datetime, timedelta
from .waitlist import manager
from .auth import get_current_active_user, Annotated, UserSchema

router = CRUDRouter(
    schema=QueueSchema,
    create_schema=CreateQueueSchema , 
    db_model=Queue,
    db=get_db
)

@router.get("")
async def get_all_queues(
     current_user: Annotated[UserSchema, Depends(get_current_active_user)],
    db:Session = Depends(get_db),
):
    queues = db.query(Queue)
    
    if current_user.role == 'client':
        queues = queues.filter_by(client_id=current_user.id)
    return queues.all()

@router.post("")
async def reserve_ticket(
    form_data: CreateQueueSchema,
    db:Session = Depends(get_db),
):
    
    db_model: Queue = Queue(**form_data.dict())
    
    db_model
    
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    new_ticket = {
        "queue_id": db_model.id,
        "number": db_model.number,
        "time": str(form_data.time),
        "status": db_model.step,
        "service": db_model.service.name,
    }
    
    
    print("sending to client")
    await manager.broadcast({
        "type": "new-ticket",
        "payload": new_ticket
    })
    
    return db_model



@router.get("/reservables/list")
async def possible_tickets(
    date: str = Query(..., example="2025-05-30"),
    service_id: int = Query(..., example=1),
    db:Session = Depends(get_db),
):
        service = db.query(Service).get(service_id)
        
        if not service:
            raise HTTPException(404, "Service was not found")
        
        now = datetime.now()
        
        # Get time range from the service
        from_time = datetime.combine(now.date(), service.from_time)
        to_time = datetime.combine(now.date(), service.to_time)

        # Calculate total minutes of operation
        work_minutes = (to_time - from_time).total_seconds() / 60

        # avg_minute is stored as Text, so convert it to float or int first
        avg_minute = float(service.avg_minute)

        number_of_queues = math.ceil(work_minutes / avg_minute)
        
        res = []

        for num in range(1, number_of_queues+1):

            next_que = db.query(Queue).filter(
                Queue.date == date,
                Queue.step > 0,
                Queue.step < 3,
                Queue.service_id == service_id,
                Queue.time >= from_time.strftime("%H:%M:%S"),
                Queue.time < (from_time + timedelta(minutes=service.avg_minute)).strftime("%H:%M:%S"),
            ).order_by(Queue.id.desc()).first()

            if next_que:
                poss = False
            else:
                poss = True

            if date == now.strftime("%Y-%m-%d"):
                if from_time.strftime("%H:%M") < now.strftime("%H:%M"):
                    poss = False

            res.append({
                "queue_number": num,
                "time": from_time.strftime("%H:%M"),
                "possible": poss
            })

            from_time += timedelta(minutes=service.avg_minute)

        return res
    


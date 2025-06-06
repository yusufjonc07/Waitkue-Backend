from models import User
from schemas import CreateUserSchema, ReportYearlyChart
from database import get_db
from .auth import get_password_hash
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import label
from sqlalchemy import func
from fastapi import Depends, APIRouter
from models import Queue


router = APIRouter(tags=['Reports'], prefix='/report')

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


@router.get("/queues/{year}", response_model=list[ReportYearlyChart])
async def get_queues_reports(year: int, db: Session = Depends(get_db)):
    
    queues = db.query(
        func.count(Queue.id).label("tickets"),
       func.extract('month', Queue.created_at).label("month")
    ).select_from(Queue).filter(
        func.extract('year', Queue.created_at) == year
    ).group_by(func.extract('month', Queue.created_at)).all()
    
    
     # Convert to dict: {month_number: ticket_count}
    month_ticket_map = {month: tickets for tickets, month in queues}

    # Ensure all 12 months are represented
    full_year_data = [
        {
            "tickets": month_ticket_map.get(i, 0),
            "month": MONTHS[i - 1]
        }
        for i in range(1, 13)
    ]

    return full_year_data

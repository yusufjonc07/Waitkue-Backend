from fastapi_crudrouter import SQLAlchemyCRUDRouter as CRUDRouter
from models import Service
from schemas import CreateServiceSchema, ServiceSchema
from database import get_db


router = CRUDRouter(
    schema=ServiceSchema,
    create_schema=CreateServiceSchema , 
    db_model=Service,
    db=get_db
)
from fastapi_crudrouter import SQLAlchemyCRUDRouter as CRUDRouter
from models import Client
from schemas import CreateClientSchema, ClientSchema
from database import get_db


router = CRUDRouter(
    schema=ClientSchema,
    create_schema=CreateClientSchema, 
    db_model=Client,
    db=get_db
)


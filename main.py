from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
import uvicorn
import routers

from routers.auth import get_current_active_user as get_user

app = FastAPI(
    title= "WaitQue",
)

app.mount("/files", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers.client, dependencies=[Depends(get_user)])
app.include_router(routers.service)
app.include_router(routers.queue, dependencies=[Depends(get_user)])
app.include_router(routers.report, dependencies=[Depends(get_user)])
app.include_router(routers.user, dependencies=[Depends(get_user)])
app.include_router(routers.upload, dependencies=[Depends(get_user)])
app.include_router(routers.waitlist)

app.include_router(routers.auth)

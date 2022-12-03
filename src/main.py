from fastapi.responses import ORJSONResponse
import uvicorn
from fastapi import FastAPI
from api.v1 import base
from api.v1 import healthcheck
from core.config import app_settings
from users.manager import auth_backend
from schemas.schemas_user import UserRead, UserCreate, UserUpdate
from users.manager import fastapi_users


app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['Auth'],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix='/users',
    tags=['users'],
)

app.include_router(healthcheck.router, prefix='/api/v1')
app.include_router(base.router, prefix='/api/v1')

if __name__ == "__main__":
    uvicorn.run(app, host=app_settings.host, port=app_settings.port)

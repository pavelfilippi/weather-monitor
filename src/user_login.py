from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select

from dependencies.database import get_database, Database
from src.models import MonitorUser

router = APIRouter()


class User(BaseModel):
    username: str


class UserInDB(User):
    password: str


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Database = Depends(get_database),
):
    async with db.session() as session:
        query = select(MonitorUser).where(MonitorUser.username == form_data.username)
        result = await session.execute(query)
        user = result.scalar()

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(username=user.username, password=user.password)
    if not form_data.password == user.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}

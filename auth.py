from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional


# app = FastAPI()


from sqlmodel import Field, Session, SQLModel, create_engine, select

# Code here omitted 👈

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    hash_password: str


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


# def create_db_and_tables():
SQLModel.metadata.create_all(engine)

# create_db_and_tables()
with Session(engine) as sess:
    user = User(username="randomsuer", hash_password="randompassword")
    sess.add(user)
    sess.commit()
    print(user.id)
    sess.delete(user)
    sess.commit()

    # Fetching data
    results = sess.exec(select(User)).all()
    print(results)

    for result in results:
        print(result.id, result.username, result.hash_password)

    user_to_update = sess.exec(select(User).where(User.id == 2)).all()[0]
    user_to_update.username = "new_username"
    user_to_update.hash_password = "new_password"
    sess.commit()

    # user_to_delete = sess.exec(select(User).where(User.id == 1)).all()[0]
    # sess.delete(user_to_delete)
    # sess.commit()
    # print(results)

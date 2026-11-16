

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .database import connect_db, initialize_database


app = FastAPI(title="IT 요청·장애 관리 도구")

initialize_database()


class RequestCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=40)
    description: str = Field(min_length=1)
    priority: str = "보통"


@app.get("/")
def home():
    return {"message": "IT 요청·장애 관리 도구 API"}


@app.get("/requests")
def get_requests():
    connection = connect_db()

    try:
        rows = connection.execute(
            "SELECT * FROM requests ORDER BY id DESC"
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        connection.close()


@app.post("/requests", status_code=201)
def create_request(request: RequestCreate):
    connection = connect_db()

    try:
        cursor = connection.execute(
            """
            INSERT INTO requests (title, category, description, priority)
            VALUES (?, ?, ?, ?)
            """,
            (
                request.title,
                request.category,
                request.description,
                request.priority,
            ),
        )
        connection.commit()

        row = connection.execute(
            "SELECT * FROM requests WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

        return dict(row)
    finally:
        connection.close()

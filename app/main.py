from .csv_import import router as csv_import_router
from pathlib import Path
from fastapi.responses import FileResponse
from .csv_export import router as csv_router
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .database import connect_db, initialize_database


app = FastAPI(title="IT 요청·장애 관리 도구")
app.include_router(csv_import_router)
app.include_router(csv_router)

initialize_database()


class RequestCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=40)
    description: str = Field(min_length=1)
    priority: str = "보통"


class RequestStatusUpdate(BaseModel):
    status: Literal["접수", "처리 중", "완료"]


@app.get("/")
def home():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


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
            (request.title, request.category, request.description, request.priority),
        )
        connection.commit()

        row = connection.execute(
            "SELECT * FROM requests WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        return dict(row)
    finally:
        connection.close()


@app.patch("/requests/{request_id}/status")
def update_request_status(request_id: int, request: RequestStatusUpdate):
    connection = connect_db()

    try:
        existing = connection.execute(
            "SELECT * FROM requests WHERE id = ?",
            (request_id,),
        ).fetchone()

        if existing is None:
            raise HTTPException(
                status_code=404,
                detail="해당 요청을 찾을 수 없습니다.",
            )

        connection.execute(
            "UPDATE requests SET status = ? WHERE id = ?",
            (request.status, request_id),
        )
        connection.commit()

        updated = connection.execute(
            "SELECT * FROM requests WHERE id = ?",
            (request_id,),
        ).fetchone()
        return dict(updated)
    finally:
        connection.close()

from csv import DictWriter
from io import StringIO

from fastapi import APIRouter, Response

from .database import connect_db


router = APIRouter()


@router.get("/requests/export.csv", summary="요청 목록 CSV 다운로드")
def export_requests_csv():
    connection = connect_db()

    try:
        rows = connection.execute(
            "SELECT * FROM requests ORDER BY id DESC"
        ).fetchall()
        request_rows = [dict(row) for row in rows]
    finally:
        connection.close()

    output = StringIO()
    fieldnames = [
        "id",
        "title",
        "category",
        "description",
        "priority",
        "status",
        "created_at",
    ]

    writer = DictWriter(
        output,
        fieldnames=fieldnames,
        lineterminator="\r\n",
    )
    writer.writeheader()
    writer.writerows(request_rows)

    return Response(
        content="\ufeff" + output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="requests.csv"'
        },
    )

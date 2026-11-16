from fastapi import APIRouter

from .database import connect_db


router = APIRouter()


@router.get("/requests/stats", summary="요청 현황 집계")
def get_request_stats():
    connection = connect_db()

    try:
        total = connection.execute(
            "SELECT COUNT(*) AS count FROM requests"
        ).fetchone()["count"]

        status_rows = connection.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM requests
            GROUP BY status
            ORDER BY status
            """
        ).fetchall()

        category_rows = connection.execute(
            """
            SELECT category, COUNT(*) AS count
            FROM requests
            GROUP BY category
            ORDER BY count DESC, category
            """
        ).fetchall()

        priority_rows = connection.execute(
            """
            SELECT priority, COUNT(*) AS count
            FROM requests
            GROUP BY priority
            ORDER BY priority
            """
        ).fetchall()

        month_rows = connection.execute(
            """
            SELECT strftime('%Y-%m', created_at) AS month,
                   COUNT(*) AS count
            FROM requests
            GROUP BY month
            ORDER BY month
            """
        ).fetchall()

        return {
            "total": total,
            "by_status": {row["status"]: row["count"] for row in status_rows},
            "by_category": {row["category"]: row["count"] for row in category_rows},
            "by_priority": {row["priority"]: row["count"] for row in priority_rows},
            "by_month": [dict(row) for row in month_rows],
        }
    finally:
        connection.close()

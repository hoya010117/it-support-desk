import csv
from io import StringIO

from fastapi import APIRouter, File, HTTPException, UploadFile

from .database import connect_db


router = APIRouter()
REQUIRED_COLUMNS = {"title", "category", "description"}
VALID_PRIORITIES = {"낮음", "보통", "높음"}


@router.post("/requests/import.csv", summary="CSV 요청 일괄 등록")
async def import_requests_csv(file: UploadFile = File(...)):
    filename = (file.filename or "").lower()

    if not filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드할 수 있습니다.")

    raw_content = await file.read()

    if not raw_content:
        raise HTTPException(status_code=400, detail="파일이 비어 있습니다.")

    try:
        content = raw_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            content = raw_content.decode("cp949")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="파일 인코딩을 읽을 수 없습니다. CSV UTF-8 형식으로 저장해 주세요.",
            )

    reader = csv.DictReader(StringIO(content))

    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV 헤더가 없습니다.")

    reader.fieldnames = [
        name.strip() if name else ""
        for name in reader.fieldnames
    ]

    missing = REQUIRED_COLUMNS - set(reader.fieldnames)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"필수 열이 없습니다: {', '.join(sorted(missing))}",
        )

    records = []
    errors = []

    for row in reader:
        line_number = reader.line_num

        if not row or not any((value or "").strip() for value in row.values()):
            continue

        title = (row.get("title") or "").strip()
        category = (row.get("category") or "").strip()
        description = (row.get("description") or "").strip()
        priority = (row.get("priority") or "보통").strip() or "보통"

        missing_values = [
            name
            for name, value in (
                ("title", title),
                ("category", category),
                ("description", description),
            )
            if not value
        ]

        if missing_values:
            errors.append(
                f"{line_number}행: 값이 비어 있음 ({', '.join(missing_values)})"
            )
            continue

        if priority not in VALID_PRIORITIES:
            errors.append(
                f"{line_number}행: priority는 낮음, 보통, 높음 중 하나여야 함"
            )
            continue

        records.append((title, category, description, priority))

    if errors:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "오류가 있어 파일 전체를 등록하지 않았습니다.",
                "errors": errors,
            },
        )

    if not records:
        raise HTTPException(status_code=400, detail="등록할 요청이 없습니다.")

    connection = connect_db()

    try:
        for record in records:
            connection.execute(
                """
                INSERT INTO requests (title, category, description, priority)
                VALUES (?, ?, ?, ?)
                """,
                record,
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    return {
        "message": f"{len(records)}건의 요청을 등록했습니다.",
        "imported_count": len(records),
    }

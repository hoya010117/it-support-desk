# IT 요청·장애 관리 도구

IT 요청을 등록하고 처리 상태를 관리하며, 요청 데이터를 CSV로 가져오고 내보내는 포트폴리오 프로젝트입니다.

## 주요 기능

- IT 요청 등록 및 목록 조회
- 요청 상태 변경: 접수, 처리 중, 완료
- 상태별 요청 건수를 보여주는 대시보드
- CSV 파일로 요청 여러 건 일괄 등록
- CSV 데이터의 필수 항목과 우선순위 검증
- Excel에서 한글이 깨지지 않도록 CSV 내보내기 처리

## 기술 스택

- Python, FastAPI
- SQLite
- HTML, CSS, JavaScript
- Git, GitHub

## 실행 방법

```bash
git clone https://github.com/hoya010117/it-support-desk.git
cd it-support-desk

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

uvicorn app.main:app --reload

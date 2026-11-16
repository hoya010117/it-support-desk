from fastapi import FastAPI

app = FastAPI(title="IT 요청·장애 관리 도구")


@app.get("/")
def home():
    return {"message": "IT 요청·장애 관리 도구 API"}


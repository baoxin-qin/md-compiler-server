"""项目主程序入口"""

from fastapi import FastAPI

app = FastAPI(title="md-compiler-server", version="0.1.0")

@app.get("/")
def test_root():
    return {
        "code": 200,
        "msg": "Welcome to FastAPI",
    }

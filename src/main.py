"""项目主程序入口"""

from fastapi import FastAPI
from src.api.health import router as healthRouter
from src.api.compiler import router as compilerRouter

app = FastAPI(title="md-compiler-server", version="0.1.0")

@app.get("/")
def test_root():
    return {
        "code": 200,
        "msg": "Welcome to my Markdown-To-HTML Compiler APP",
    }

app.include_router(healthRouter, prefix="/api")
app.include_router(compilerRouter, prefix="/api")

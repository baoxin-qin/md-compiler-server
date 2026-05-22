"""项目主程序入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.health import router as healthRouter
from src.api.compiler import router as compilerRouter
from src.api.config import ALLOW_ORIGINS

app = FastAPI(title="md-compiler-server", version="0.1.0")

# FastAPI 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def test_root():
    return {
        "code": 200,
        "msg": "Welcome to my Markdown-To-HTML Compiler APP",
    }

app.include_router(healthRouter, prefix="/api")
app.include_router(compilerRouter, prefix="/api")

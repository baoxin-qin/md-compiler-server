"""Markdown 编译 API"""

import os
from fastapi import APIRouter
from pydantic import BaseModel

from src.service.instance import Token
from src.service.lexer import Lexer

class CompileRequest(BaseModel):
    markdown: str

router = APIRouter()

# 基于 __file__ 计算输出路径
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")

@router.post("/compile")
def CompileMarkdown(request: CompileRequest):
    # TODO: html = compiler.compile(request.markdown)
    # 1. 词法分析
    lexer = Lexer(request.markdown)
    tokens: list[Token] = lexer.run(os.path.join(OUTPUT_DIR, 'tokens.json'))

    return {"html": "<h1>Waiting to be done ...</h1>"}
"""Markdown 编译 API"""

import os
from fastapi import APIRouter
from pydantic import BaseModel

from src.service.instance import Token, AstNode
from src.service.lexer import Lexer
from src.service.parser import Parser
from src.service.builder import Builder, HtmlBuilder

class CompileRequest(BaseModel):
    markdown: str

router = APIRouter()

# 基于 __file__ 计算输出路径
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")

@router.post("/compile")
def CompileMarkdown(request: CompileRequest):
    """Markdown 编译 API"""
    # 1. 词法分析
    lexer = Lexer(request.markdown)
    tokens: list[Token] = lexer.run(os.path.join(OUTPUT_DIR, 'tokens.json'))

    # 2. 语法分析
    parser = Parser(tokens)
    ast: AstNode = parser.run(os.path.join(OUTPUT_DIR, 'ast.json'))

    lexer.clear()
    del lexer, tokens  # 释放内存

    # 3. 目标代码生成
    builder: Builder = HtmlBuilder(ast)
    html = builder.run(os.path.join(OUTPUT_DIR, 'ir.txt'))

    parser.clear()
    del parser, ast # 释放内存

    builder.clear()
    del html
    return {
        "code": 200,
        "msg": "Success",
        "data": "Waiting for HTML file ..."
    }
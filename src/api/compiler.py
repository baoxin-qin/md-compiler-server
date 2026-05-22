"""Markdown 编译 API"""

from fastapi import APIRouter
from pydantic import BaseModel

from src.service.instance import Token, AstNode
from src.service.lexer import Lexer
from src.service.parser import Parser
from src.service.builder import Builder, HtmlBuilder

class CompileRequest(BaseModel):
    markdown: str

router = APIRouter()

@router.options("/compile")
def OptionsCompile():
    return {"code": 200, "msg": "Options", "flag": True, "data": None}

@router.post("/compile")
def CompileMarkdown(request: CompileRequest):
    """Markdown 编译 API"""
    # 1. 词法分析
    lexer = Lexer(request.markdown)
    tokens: list[Token] = lexer.run()
    if not tokens:
        print('[Error] Lexer could not tokenize the input Markdown.')
        return {"code": 400, "msg": "Lexer Error", "flag": False, "data": None}

    # 2. 语法分析
    parser = Parser(tokens)
    ast: AstNode = parser.run()
    if ast is None:
        print('[Error] Parser could not parse the tokens.')
        return {"code": 400, "msg": "Parser Error", "flag": False, "data": None}

    # 3. 目标代码生成
    builder: Builder = HtmlBuilder(ast)
    html = builder.run()
    if not html:
        print('[Error] Builder could not build the HTML output.')
        return {"code": 400, "msg": "Builder Error", "flag": False, "data": None}
    
    print('[Success] Markdown compilation completed successfully.')
    return {
        "code": 200,
        "msg": "Success",
        "flag": True,
        "data": html
    }
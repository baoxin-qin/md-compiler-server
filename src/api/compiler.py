"""Markdown 编译 API"""

from fastapi import APIRouter
from pydantic import BaseModel

class CompileRequest(BaseModel):
    markdown: str

router = APIRouter()

@router.post("/compile")
def CompileMarkdown(request: CompileRequest):
    # TODO: html = compiler.compile(request.markdown)
    return {"html": "<h1>Waiting to be done ...</h1>"}
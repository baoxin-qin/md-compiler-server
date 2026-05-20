"""相关类与实例的定义"""

from pydantic import BaseModel
from enum import Enum

class TokenType(Enum):
    """Token 类型枚举"""
    Heading         = "Heading"
    UnorderedList   = "UnorderedList"
    OrderedList     = "OrderedList"
    HorizontalRule  = "HorizontalRule"
    Blockquote      = "Blockquote"
    Link            = "Link"
    Image           = "Image"
    InlineCode      = "InlineCode"
    CodeBlock       = "CodeBlock"
    Bold            = "Bold"
    Italic          = "Italic"
    Strikethrough   = "Strikethrough"
    Paragraph       = "Paragraph"
    Newline         = "Newline"

class Token(BaseModel):
    """Token 类"""
    type    : TokenType  # Token 类型
    value   : str        # Token 值
    indent  : int        # Token 在源文件中的缩进数

"""
正则表达式模式
注：列表项前的空格数作为缩进数，适配不同缩进的列表项，以此实现列表项的嵌套
"""
RegExpPattern: dict[TokenType, str] = {
    TokenType.Heading       : r"^(#{1,6}) (.*)$",
    TokenType.UnorderedList : r"^( *)[-*] (.*)$",
    TokenType.OrderedList   : r"^( *)(\d+)\. (.*)$",
    TokenType.HorizontalRule: r"^(?:-{3,}|\*{3,})\s*$",
    TokenType.Blockquote    : r"^> (.*)$",
    TokenType.Link          : r"\[([^\]]*)\]\(([^)]+)\)",
    TokenType.Image         : r"!\[([^\]]*)\]\(([^)]+)\)",
    TokenType.InlineCode    : r"`([^`]+)`",
    TokenType.CodeBlock     : r"```(\w*)\n([\s\S]*?)\n```",
    TokenType.Bold          : r"\*\*(.*?)\*\*",
    TokenType.Italic        : r"\*(.*?)\*",
    TokenType.Strikethrough : r"~~(.*?)~~",
}
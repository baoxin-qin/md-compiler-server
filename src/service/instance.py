"""相关类与实例的定义"""

from pydantic import BaseModel
from enum import Enum
from typing import Optional, List

class TokenType(Enum):
    """Token 类型枚举"""
    Document        = "Document"  # 文档根节点
    Heading         = "Heading"
    UnorderedList   = "UnorderedList"
    OrderedList     = "OrderedList"
    ListItem        = "ListItem"
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
    Text            = "Text"
    Newline         = "Newline"
    LineBreak       = "LineBreak"  # 换行符
    Whitespace      = "Whitespace"  # 空格

class Token(BaseModel):
    """Token 类"""
    type    : TokenType  # Token 类型
    value   : str        # Token 值
    indent  : int        # Token 在源文件中的缩进数

class AstNode(BaseModel):
    """AST 节点类"""
    type    : TokenType
    value   : Optional[str] = None  # 有些节点不需要值
    children: List["AstNode"] = []

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

# 节点类型标签映射
HtmlMap: dict[TokenType, tuple[str, str]] = {
    TokenType.Document          : ("", ""),
    TokenType.Heading           : lambda n: (f"<h{n['level']}>", f"</h{n['level']}>"),
    TokenType.UnorderedList     : ("<ul>", "</ul>"),
    TokenType.OrderedList       : ("<ol>", "</ol>"),
    TokenType.ListItem          : ("<li>", "</li>"),
    TokenType.Blockquote        : ("<blockquote>", "</blockquote>"),
    TokenType.HorizontalRule    : ("<hr>", ""),
    TokenType.Link              : lambda n: (f"<a href='{n['url']}'>", "</a>"),
    TokenType.Image             : lambda n: (f"<img src='{n['url']}' alt='{n['alt']}' />", ""),
    TokenType.CodeBlock: lambda n: (
        f"<pre><code class='language-{n['lang']}'>",
        "</code></pre>"
    ),
    TokenType.InlineCode        : ("<code>", "</code>"),
    TokenType.Paragraph         : ("<p>", "</p>"),
    TokenType.Bold              : ("<strong>", "</strong>"),
    TokenType.Italic            : ("<em>", "</em>"),
    TokenType.Strikethrough     : ("<del>", "</del>"),
    TokenType.Text              : ("", ""),
    TokenType.Whitespace        : ("", ""),
    TokenType.Newline           : ("\n", ""),
    TokenType.LineBreak         : ("<br>", ""),
}
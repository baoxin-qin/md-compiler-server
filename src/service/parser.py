"""语法分析器"""

import re
import json
from unittest import result
from src.service.instance import Token, TokenType, AstNode, RegExpPattern

class Parser:
    """解析 token 流，构建 AST"""
    def __init__(self, tokens: list[Token]):
        self.tokens: list[Token] = tokens
        self.ast: AstNode = None
    
    def run(self, filePath: str) -> AstNode:
        """运行解析器，返回 AST"""
        self.ast = self.parse()
        self.writeJSON(filePath)
        return self.ast
    
    def parse(self) -> AstNode:
        root = AstNode(type=TokenType.Document, value=None, children=[])
        stack: list[tuple[AstNode, int]] = []  # 处理嵌套层级的栈

        i: int = 0
        while i < len(self.tokens):
            token = self.tokens[i]

            # 空行
            if token.type == TokenType.Newline:
                stack.clear()  # 重置栈
                i += 1
                continue

            # 标题
            if token.type == TokenType.Heading:
                heading: list[str] = token.value.split(' ', 1)
                level: int = int(heading[0])  # 标题层级
                text: str = heading[1] if len(heading) > 1 else ""  # 标题文本
                root.children.append(AstNode(
                    type=TokenType.Heading,
                    value=f"{level}",
                    children=self.parseInline(text)
                ))
                stack.clear()
                i += 1
                continue
            # 水平分割线
            elif token.type == TokenType.HorizontalRule:
                root.children.append(AstNode(type=TokenType.HorizontalRule))
                stack.clear()
                i += 1
                continue
            # 引用
            elif token.type == TokenType.Blockquote:
                # 如果引用连续，且没有使用空行符分割，则将它们合并
                content: str = token.value
                i += 1
                while i < len(self.tokens) and self.tokens[i].type == TokenType.Blockquote:
                    content += '\n' + self.tokens[i].value
                    i += 1
                root.children.append(AstNode(
                    type=TokenType.Blockquote,
                    children=self.parseInline(content)
                ))
                stack.clear()
                continue
            # 代码块
            elif token.type == TokenType.CodeBlock:
                codeBlock: list[str] = token.value.split('\n', 1)
                lang: str = codeBlock[0]
                content: str = codeBlock[1] if len(codeBlock) > 1 else ""
                root.children.append(AstNode(
                    type=TokenType.CodeBlock,
                    value=lang,
                    children=[AstNode(type=TokenType.Text, value=content)]
                ))
                stack.clear()
                continue
            # 段落
            elif token.type == TokenType.Paragraph:
                # 段落之间是连续的，没有换行符分割，则将它们合并
                paragraph: list[str] = []

                paragraph.extend(self.parseInline(token.value))
                i += 1
                while i < len(self.tokens) and self.tokens[i].type == TokenType.Paragraph:
                    paragraph.append(AstNode(type=TokenType.LineBreak))  # 先添加换行符
                    paragraph.extend(self.parseInline(self.tokens[i].value))  # 再解析下一个段落
                    i += 1
                root.children.append(AstNode(
                    type=TokenType.Paragraph,
                    children=paragraph
                ))
                stack.clear()
                continue
            # UL/OL 列表
            elif token.type in (TokenType.UnorderedList, TokenType.OrderedList):
                thisType: TokenType = token.type
                thisIndent: int = token.indent
                thisText: str = token.value

                # 若当前的缩进大于栈顶，则需要退栈
                while stack and stack[-1][1] >= thisIndent:
                    stack.pop()
                node: AstNode = AstNode(type=TokenType.ListItem, value=self.parseInline(thisText))

                if not stack:
                    root.children.append(AstNode(type=thisType, children=[node]))
                    stack.append((node, thisIndent))
                else:
                    parentNode, parentIndent = stack[-1]
                    if thisIndent > parentIndent:
                        lastNode = parentNode.children[-1]
                        sub: AstNode | None = None
                        for child in reversed(lastNode.children):
                            if child.type == thisType:
                                sub = child
                                break
                        if not sub:
                            sub = AstNode(type=thisType, children=[])
                            lastNode.children.append(sub)
                        sub.children.append(node)
                        stack.append((sub, thisIndent))
                    else:
                        parentNode.children.append(node)
                i += 1
                continue

            i += 1

        return root

    def parseInline(self, text: str) -> list[AstNode]:
        """解析内联元素"""
        result: list[AstNode] = []
        remaining: str = text
        # 内联元素解析优先级
        priority: list[tuple[TokenType, str]] = [
            (TokenType.Image, RegExpPattern[TokenType.Image]),
            (TokenType.Link, RegExpPattern[TokenType.Link]),
            (TokenType.InlineCode, RegExpPattern[TokenType.InlineCode]),
            (TokenType.Bold, RegExpPattern[TokenType.Bold]),
            (TokenType.Italic, RegExpPattern[TokenType.Italic]),
            (TokenType.Strikethrough, RegExpPattern[TokenType.Strikethrough]),
        ]

        while remaining:
            matched: bool = False
            for nodeType, pattern in priority:
                match = re.match(pattern, remaining)
                if match:
                    if nodeType == TokenType.Image:
                        result.append(AstNode(
                            type=nodeType,
                            value=f"{match.group(2)|match.group(1)}"
                        ))
                    elif nodeType == TokenType.Link:
                        result.append(AstNode(
                            type=nodeType,
                            value=match.group(2),
                            children=[AstNode(type=TokenType.Text, value=match.group(1))]
                        ))
                    elif nodeType == TokenType.InlineCode:
                        result.append(AstNode(
                            type=nodeType,
                            children=[AstNode(type=TokenType.Text, value=match.group(1))]
                        ))
                    elif nodeType in (TokenType.Bold, TokenType.Italic, TokenType.Strikethrough):
                        result.append(AstNode(
                            type=nodeType,
                            children=[AstNode(type=TokenType.Text, value=match.group(1))]
                        ))
                    remaining = remaining[match.end():]
                    matched = True
                    break
            if not matched:
                # 收集连续的普通文本字符，直到遇到内联元素的开始位置
                text_content = ""
                while remaining:
                    has_match = False
                    for _, pattern in priority:
                        if re.match(pattern, remaining):
                            has_match = True
                            break
                    if has_match:
                        break
                    text_content += remaining[0]
                    remaining = remaining[1:]
                if text_content:
                    result.append(AstNode(type=TokenType.Text, value=text_content))

        return result
    
    def _nodeToDict(self, node: 'AstNode') -> dict:
        """递归将单个 AstNode 转换为字典"""
        result = {
            'type': node.type.value,  # 将 TokenType Enum 转换为字符串
            'value': node.value
        }
        if node.children:
            result['children'] = [self._nodeToDict(child) for child in node.children]
        return result

    def toDict(self) -> dict:
        """将 AST 转换为字典"""
        if self.ast:
            return self._nodeToDict(self.ast)
        return {}

    def writeJSON(self, filePath: str):
        """将 AST 写入 JSON 文件"""
        try:
            with open(filePath, 'w', encoding='utf-8') as f:
                json.dump(self.toDict(), f, ensure_ascii=False, indent=2)
                print(f"AST 写入 JSON 文件: {filePath}")
        except Exception as e:
            print(f"写入 JSON 文件失败: {e}")
        finally:
            print("语法分析结束")
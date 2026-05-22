"""目标代码生成器"""

from abc import abstractmethod
from typing import override
from src.service.instance import AstNode, TokenType, HtmlMap

class Builder:
    def __init__(self, AstTree: AstNode) -> None:
        self.AstTree = AstTree
    @abstractmethod
    def run(self):
        pass
    @abstractmethod
    def build(self):
        pass

class HtmlBuilder(Builder):
    """HTML生成器"""
    def __init__(self, AstTree: AstNode) -> None:
        super().__init__(AstTree)
        self.html: str = ""
    
    @override
    def run(self) -> str:
        self.html = self.build()
        return self.html

    @override
    def build(self) -> str:
        result: list[str] = []
        self.traverse(self.AstTree, result)
        return "\n".join(result)
    
    def traverse(self, node: AstNode, result: list[str]):
        """遍历AST树，生成HTML代码"""
        thisType: TokenType = node.type
        thisValue: str = node.value
        thisChildren: list[AstNode] = node.children

        if thisType in HtmlMap:
            tag: tuple = HtmlMap[thisType]
            if callable(tag):
                # 调用函数生成 HTML
                try:
                    openTag, closeTag = tag({
                        "type": thisType,
                        "level": thisValue,
                        "url": thisValue.split('|')[0] if '|' in thisValue else thisValue,
                        "alt": thisValue.split('|')[1] if '|' in thisValue else "",
                        "lang": thisValue
                    })
                except:
                    openTag, closeTag = ("", "")
            else:
                openTag, closeTag = tag
        else:
            openTag, closeTag = ("", "")
        
        # 文档节点直接遍历子节点
        if thisType == TokenType.Document:
            for child in thisChildren:
                self.traverse(child, result)

        # 列表节点遍历子节点
        elif thisType in (TokenType.UnorderedList, TokenType.OrderedList):
            result.append(openTag)
            for child in thisChildren:
                self.traverse(child, result)
            result.append(closeTag)

        # 列表项节点遍历子节点
        elif thisType == TokenType.ListItem:
            hasChildren: bool = any(
                child.type in (TokenType.UnorderedList, TokenType.OrderedList) for child in thisChildren
            )
            if hasChildren:
                # 还有子列表
                innerText: list = []
                for child in thisChildren:
                    if child.type not in (TokenType.UnorderedList, TokenType.OrderedList):
                        self.traverseInline(child, innerText)
                result.append(f"{openTag}{''.join(innerText)}")
                for child in thisChildren:
                    if child.type in (TokenType.UnorderedList, TokenType.OrderedList):
                        self.traverse(child, result)
                result.append(f"{closeTag}")
            else:
                # 没有子列表，直接在一行
                inner = []
                for child in thisChildren:
                    self.traverseInline(child, inner)
                result.append(f"{openTag}{''.join(inner)}{closeTag}")

        # 行级元素节点遍历子节点
        elif thisType in (
            TokenType.Bold, TokenType.Italic,
            TokenType.Strikethrough, TokenType.InlineCode
        ):
            # 行级元素，直接输出
            inner = []
            for child in thisChildren:
                self.traverseInline(child, inner)
            result.append(f"{openTag}{''.join(inner)}{closeTag}")
        
        # 链接类型
        elif thisType == TokenType.Link:
            inner = []
            for child in thisChildren:
                self.traverseInline(child, inner)
            result.append(f"{openTag}{''.join(inner)}{closeTag}")
        
        # 图片类型
        elif thisType == TokenType.Image:
            result.append(f"{openTag}")
        
        # 代码块类型
        elif thisType == TokenType.CodeBlock:
            inner = []
            for child in thisChildren:
                self.traverseInline(child, inner)
            result.append(f"{openTag}{''.join(inner)}{closeTag}")
        
        # 标题类型
        elif thisType == TokenType.Heading:
            inner = []
            for child in thisChildren:
                self.traverseInline(child, inner)
            result.append(f"{openTag}{''.join(inner)}{closeTag}")
        
        # 段落类型
        elif thisType == TokenType.Paragraph:
            inner = []
            for child in thisChildren:
                self.traverseInline(child, inner)
            result.append(f"{openTag}{''.join(inner)}{closeTag}")
        
        # 引用类型
        elif thisType == TokenType.Blockquote:
            inner = []
            for child in thisChildren:
                self.traverseInline(child, inner)
            result.append(f"{openTag}{''.join(inner)}{closeTag}")
        
        # 水平线类型
        elif thisType == TokenType.HorizontalRule:
            result.append(f"{openTag}")
        
        # 文本类型
        elif thisType == TokenType.Text:
            result.append(thisValue)
        
        # 换行类型
        elif thisType == TokenType.LineBreak:
            result.append(openTag)

    def traverseInline(self, node: AstNode, result: list[str]):
        """遍历行内元素节点"""
        subType: TokenType = node.type
        subValue: str = node.value
        subChildren: list[AstNode] = node.children

        if subType in HtmlMap:
            tag = HtmlMap[subType]
            if callable(tag):
                try:
                    openTag, closeTag = tag({
                        "type": subType,
                        "level": subValue,
                        "url": subValue.split('|')[0] if '|' in subValue else subValue,
                        "alt": subValue.split('|')[1] if '|' in subValue else "",
                        "lang": subValue
                    })
                except:
                    openTag, closeTag = ("", "")
            else:
                openTag, closeTag = tag
        else:
            openTag, closeTag = ("", "")
        
        if subType == TokenType.Text:
            result.append(subValue)
        elif subType == TokenType.LineBreak:
            result.append(openTag)
        elif subType in (
            TokenType.Bold, TokenType.Italic,
            TokenType.Strikethrough, TokenType.InlineCode
        ):
            inner = []
            for child in subChildren:
                self.traverseInline(child, inner)
            result.append(f"{openTag}{''.join(inner)}{closeTag}")
        elif subType == TokenType.Link:
            inner = []
            for child in subChildren:
                self.traverseInline(child, inner)
            result.append(f"{openTag}{''.join(inner)}{closeTag}")
        elif subType == TokenType.Image:
            result.append(f"{openTag}")
        else:
            # 其他类型，直接遍历子节点
            for child in subChildren:
                self.traverseInline(child, result)

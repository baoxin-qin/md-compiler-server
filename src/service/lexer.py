"""词法分析器"""

import re
import json
from src.service.instance import RegExpPattern, Token, TokenType

class Lexer:
    """解析 Markdown 文本流，生成 Token 流"""
    def __init__(self, md: str):
        self.md = md
        self.tokens: list[Token] = []
    
    def setInput(self, md: str):
        self.md = md
        self.tokens.clear()
    
    def run(self, filePath: str) -> list[Token]:
        """运行词法分析器"""
        self.tokenize()
        self.writeJSON(filePath)
        return self.tokens
    
    def tokenize(self):
        """
        主分词方法，根据正则表达式模式匹配文本流，生成 Token 流
        仅处理块级元素，不处理内联元素
        """

        lines: list[str] = self.md.split('\n')
        matched = None
        in_code_block: bool = False
        code_language: str = ''
        code_content: str = ''

        for line in lines:
            # 1. 处理代码块
            if line.startswith('```'):
                if not in_code_block:
                    # 开始进入代码块模式
                    in_code_block = True
                    code_language = line[3:].strip()
                    code_content = ''
                else:
                    in_code_block = False
                    self.tokens.append(Token(
                        type=TokenType.CodeBlock, indent=0,
                        value=f"{code_language}\n{code_content}"
                    ))
                continue
            if in_code_block:
                # 拼接代码块内容
                code_content += line + '\n'
                continue

            # 2. 处理空行
            if line.strip() == '':
                self.tokens.append(Token(type=TokenType.Newline, indent=0, value=''))
                continue
            
            # 3. 处理标题
            matched = re.match(RegExpPattern[TokenType.Heading], line)
            if matched:
                level: int = len(matched.group(1))
                self.tokens.append(Token(
                    type=TokenType.Heading, indent=0,
                    value=f"{level} {matched.group(2)}"
                ))
                continue

            # 4. 处理无序列表
            matched = re.match(RegExpPattern[TokenType.UnorderedList], line)
            if matched:
                indent: int = len(matched.group(1))
                self.tokens.append(Token(
                    type=TokenType.UnorderedList, indent=indent,
                    value=matched.group(2)
                ))
                continue

            # 5. 处理有序列表
            matched = re.match(RegExpPattern[TokenType.OrderedList], line)
            if matched:
                indent: int = len(matched.group(1))
                self.tokens.append(Token(
                    type=TokenType.OrderedList, indent=indent,
                    value=matched.group(3)
                ))
                continue

            # 6. 处理水平分割线
            matched = re.match(RegExpPattern[TokenType.HorizontalRule], line)
            if matched:
                self.tokens.append(Token(type=TokenType.HorizontalRule, indent=0, value=''))
                continue

            # 7. 处理引用
            matched = re.match(RegExpPattern[TokenType.Blockquote], line)
            if matched:
                self.tokens.append(Token(type=TokenType.Blockquote, indent=0, value=matched.group(1)))
                continue

            # 8. 处理段落（包含内联元素）
            self.tokens.append(Token(type=TokenType.Paragraph, indent=0, value=line))
    
    def toDict(self):
        """将 Token 流转换为 字典列表"""
        result = []
        for token in self.tokens:
            token_dict = token.model_dump()
            # 将 TokenType Enum 转换为字符串，因为 Enum 不能直接序列化
            token_dict['type'] = token_dict['type'].value
            result.append(token_dict)
        return result
    
    def writeJSON(self, filePath: str):
        """将 Token 流写入 JSON 文件"""
        try:
            with open(filePath, 'w', encoding='utf-8') as f:
                json.dump(self.toDict(), f, ensure_ascii=False, indent=2)
                print(f"Tokens 流写入 JSON 文件: {filePath}")
        except Exception as e:
            print(f"写入 JSON 文件失败: {e}")
        finally:
            print("词法分析结束")
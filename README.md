# md-compiler-server

- Web 版在线 Markdown 解析渲染器，后端部分；基于 FastAPI 框架
- 前端部分基于 Vue3 + TypeScript 实现。[点击前往](https://github.com/baoxin-qin/md-compiler-web)

## 技术选型

| 技术 | 描述 |
| --- | --- |
| FastAPI | 后端框架 |
| Pydantic | 数据验证、结构化、序列化 |

## 项目结构

```text
src/ # 项目源代码目录
|———— main.py  # FastAPI 主程序入口
|———— api/  # API 路由模块
|     |———— config.py  # 配置文件
|     |———— health.py  # 健康检查接口
|     |———— compiler.py  # 编译接口
|———— service/  # 核心编译解析服务模块
|     |———— lexer.py  # 词法分析器
|     |———— parser.py  # 语法分析器
|     |———— builder.py  # 输出构建器

scripts/  # 脚本目录
|———— run.sh / run.cmd / run.ps1  # 运行脚本
```

## 快速开始

- 安装依赖

```bash
pip install -e .
```

- 运行项目

```bash
cd md-compiler-server
scripts/run.ps1  # if in Windows
scripts/run.sh  # if in Linux/MacOS
```
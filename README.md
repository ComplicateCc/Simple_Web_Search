# Simple Web Search
95%以上代码由Trae完成，甚至是这个Readme

基于Google搜索和大语言模型的智能检索系统，提供智能搜索查询优化、结果分析和总结等功能。 

## 功能特性

- 🔍 智能搜索查询优化：使用大语言模型优化用户的搜索关键词
- 🌐 Google搜索集成：利用Google Custom Search API获取高质量搜索结果
- 🤖 智能结果分析：使用大语言模型分析和总结搜索结果
- 📝 Markdown格式输出：生成结构化的搜索报告
- 🎯 内容过滤：自动过滤低质量和不相关的搜索结果

## 技术架构

### 后端技术栈

- FastAPI：高性能的Python Web框架
- Google Custom Search API：提供搜索服务
- 火山引擎大语言模型：提供智能分析能力
- Python 3.8+

### 前端技术栈

- React：用户界面框架
- Material-UI：UI组件库

## 快速开始

### 环境要求

- Python 3.8 或更高版本
- Node.js 14 或更高版本
- Google Custom Search API密钥
- 火山引擎API密钥

### 安装步骤

1. 克隆项目并安装Python依赖：
```bash
git clone [项目地址]
cd Simple_Web_Search
pip install -r requirements.txt
```

2. 配置环境变量：
创建.env文件并添加以下配置：
```
GOOGLE_API_KEY=你的Google API密钥
GOOGLE_SEARCH_ENGINE_ID=你的搜索引擎ID
DOUBAO_API_KEY=你的火山引擎API密钥
```

3. 安装前端依赖：
```bash
cd frontend
npm install
```

### 启动服务

1. 启动后端服务：
```bash
python main.py --port 8003
```

2. 启动前端开发服务器：
```bash
cd frontend
npm run dev
```

访问 http://localhost:5173 即可使用系统。

## API文档

启动服务后访问 http://localhost:8003/docs 查看详细的API文档。

### 主要接口

- POST /search：搜索接口
  - 请求体：{"query": "搜索关键词"}
  - 返回：{"response": "Markdown格式的分析结果"}

## 测试

运行单元测试：
```bash
python -m pytest test_main.py
```

运行直接测试：
```bash
python test_direct.py
```

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。

## 致谢

- Google Custom Search API
- 火山引擎
- FastAPI
- React

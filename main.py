from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
from typing import List
from googleapiclient.discovery import build
import requests
from volcenginesdkarkruntime import Ark

# 加载环境变量
load_dotenv()

# 初始化FastAPI应用
app = FastAPI(title="AI Web Search API", description="基于Google搜索和大语言模型的智能检索系统")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:8003"],  # 允许前端开发服务器的源
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 明确指定允许的HTTP方法
    allow_headers=["Content-Type", "Authorization", "Accept"],  # 明确指定允许的请求头
)

@app.get("/")
async def root():
    """重定向到API文档页面"""
    return {"message": "欢迎使用AI Web Search API", "docs_url": "/docs"}

# 配置Google搜索API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

# 配置大模型API
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
client = Ark(api_key=DOUBAO_API_KEY)

class SearchQuery(BaseModel):
    query: str

class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str

def generate_search_query(query: str) -> str:
    """使用大模型生成优化后的搜索查询"""
    prompt = f"请根据以下用户问题，生成一个简短的、适合Google搜索的查询语句（不要生成多个选项，直接返回最优的一个查询语句）：\n{query}"
    
    try:
        completion = client.chat.completions.create(
            model="doubao-pro-32k-240615",
            messages=[
                {"role": "system", "content": "你是一个搜索优化专家，请生成简短、精确的搜索查询语句，不要生成多个选项。"},
                {"role": "user", "content": prompt}
            ]
        )
        # 清理并简化返回的查询语句
        query = completion.choices[0].message.content.strip()
        # 移除可能的序号和多余的格式
        query = query.split('\n')[0].strip('123456789.、')
        return query
    except Exception as e:
        print(f"大模型API调用失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate search query: {str(e)}")

def google_search(query: str) -> List[SearchResult]:
    """执行Google搜索并返回结果"""
    try:
        print(f"开始执行Google搜索，查询语句: {query}")
        print(f"使用的API密钥: {GOOGLE_API_KEY[:5]}...")
        
        if not GOOGLE_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
            raise ValueError("Google API密钥或搜索引擎ID未配置")
        
        # 处理查询字符串，移除所有引号、特殊字符并限制长度
        cleaned_query = query.replace('"', '').replace('\'', '').strip()
        # 限制查询长度，避免过长的查询
        words = cleaned_query.split()
        cleaned_query = ' '.join(words[:5])  # 限制最多5个关键词
        
        # 如果搜索结果为空，尝试使用更宽泛的搜索词
        max_retries = 2
        for attempt in range(max_retries):
            service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
            print(f"尝试第{attempt + 1}次搜索，查询语句: {cleaned_query}")
            
            result = service.cse().list(q=cleaned_query, cx=GOOGLE_SEARCH_ENGINE_ID, num=10).execute()
            print(f"Google API响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('items'):
                search_results = []
                for item in result['items']:
                    # 基本的内容过滤
                    title = item.get('title', '').lower()
                    snippet = item.get('snippet', '').lower()
                    if any(spam in title for spam in ['小姐', '资源']) or \
                       any(spam in snippet for spam in ['小姐', '资源']):
                        continue
                        
                    search_results.append(SearchResult(
                        title=item.get('title', '无标题'),
                        link=item.get('link', '无链接'),
                        snippet=item.get('snippet', '无摘要')
                    ))
                if search_results:
                    print(f"成功获取到{len(search_results)}条搜索结果")
                    return search_results
            
            # 如果没有结果且不是最后一次尝试，简化搜索词
            if attempt < max_retries - 1:
                words = cleaned_query.split()
                cleaned_query = ' '.join(words[:min(3, len(words))])  # 只保留前三个词或更少
                print(f"简化搜索词为: {cleaned_query}")
            
        print("所有搜索尝试均未返回结果")
        return []
        
    except Exception as e:
        print(f"Google搜索失败: {str(e)}")
        if hasattr(e, 'resp') and hasattr(e.resp, 'status'):
            print(f"Google API响应状态码: {e.resp.status}")
        raise HTTPException(status_code=500, detail=f"Google search failed: {str(e)}")

def analyze_results(query: str, results: List[SearchResult]) -> str:
    """使用大模型分析搜索结果并生成总结"""
    # 将搜索结果转换为文本格式
    results_text = "\n\n".join([f"标题：{r.title}\n内容：{r.snippet}" for r in results])
    
    prompt = f"请根据以下搜索结果，回答用户的问题：{query}\n\n搜索结果：\n{results_text}"
    
    try:
        completion = client.chat.completions.create(
            model="doubao-pro-32k-240615",
            messages=[
                {"role": "system", "content": "你是一个专业的研究助手，请根据搜索结果提供准确、全面的回答。"},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"分析结果时大模型API调用失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze results: {str(e)}")

@app.post("/search")
async def search(query: SearchQuery):
    """处理搜索请求的主要端点"""
    # 1. 使用大模型优化搜索查询
    optimized_query = generate_search_query(query.query)
    
    # 2. 执行Google搜索
    search_results = google_search(optimized_query)
    
    # 3. 使用大模型分析结果
    analysis = analyze_results(query.query, search_results)
    
    # 4. 生成Markdown格式的响应
    markdown_response = f"# 搜索结果分析\n\n{analysis}\n\n## 参考链接\n\n"
    for result in search_results:
        markdown_response += f"- [{result.title}]({result.link})\n"
    
    return {"response": markdown_response}

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8003)
    args = parser.parse_args()
    
    uvicorn.run(app, host="0.0.0.0", port=args.port)
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app, generate_search_query, google_search, analyze_results, SearchResult
from httpx import AsyncClient

@pytest.fixture
def client():
    return AsyncClient(app=app, base_url="http://test")

def test_generate_search_query():
    """测试搜索查询优化功能"""
    with patch('requests.post') as mock_post:
        # 模拟大模型API返回优化后的查询
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': '优化后的搜索查询'}}]
        }
        mock_post.return_value = mock_response
        
        result = generate_search_query('世界未解之谜有几个？分别是什么')
        assert result == '优化后的搜索查询'

def test_google_search():
    """测试Google搜索功能"""
    with patch('googleapiclient.discovery.build') as mock_build:
        # 模拟Google搜索API返回结果
        mock_service = MagicMock()
        mock_cse = MagicMock()
        mock_list = MagicMock()
        
        mock_build.return_value = mock_service
        mock_service.cse.return_value = mock_cse
        mock_cse.list.return_value = mock_list
        mock_list.execute.return_value = {
            'items': [
                {
                    'title': '测试标题',
                    'link': 'https://example.com',
                    'snippet': '测试摘要'
                }
            ]
        }
        
        results = google_search('测试查询')
        assert len(results) == 1
        assert results[0].title == '测试标题'
        assert results[0].link == 'https://example.com'
        assert results[0].snippet == '测试摘要'

def test_analyze_results():
    """测试搜索结果分析功能"""
    with patch('requests.post') as mock_post:
        # 模拟大模型API返回分析结果
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': '分析结果总结'}}]
        }
        mock_post.return_value = mock_response
        
        results = [
            SearchResult(
                title='测试标题',
                link='https://example.com',
                snippet='测试摘要'
            )
        ]
        
        analysis = analyze_results('测试查询', results)
        assert analysis == '分析结果总结'

@pytest.mark.asyncio
async def test_search_endpoint_integration(client):
    """测试搜索端点的集成功能"""
    with patch('main.generate_search_query') as mock_generate_query, \
         patch('main.google_search') as mock_google_search, \
         patch('main.analyze_results') as mock_analyze_results:
        
        # 模拟各个函数的返回值
        mock_generate_query.return_value = '优化后的查询'
        mock_google_search.return_value = [
            SearchResult(
                title='测试标题',
                link='https://example.com',
                snippet='测试摘要'
            )
        ]
        mock_analyze_results.return_value = '分析结果总结'
        
        # 发送测试请求
        response = await client.post('/search', json={'query': '测试查询'})
        
        # 验证响应
        assert response.status_code == 200
        assert '分析结果总结' in response.json()['response']
        assert '测试标题' in response.json()['response']
        assert 'https://example.com' in response.json()['response']

def test_error_handling():
    """测试错误处理功能"""
    # 测试搜索查询优化失败
    with patch('requests.post') as mock_post:
        mock_post.side_effect = Exception('API调用失败')
        with pytest.raises(HTTPException):
            generate_search_query('测试查询')
    
    # 测试Google搜索失败
    with patch('googleapiclient.discovery.build') as mock_build:
        mock_build.side_effect = Exception('搜索失败')
        with pytest.raises(HTTPException):
            google_search('测试查询')
    
    # 测试结果分析失败
    with patch('requests.post') as mock_post:
        mock_post.side_effect = Exception('分析失败')
        with pytest.raises(HTTPException):
            analyze_results('测试查询', [])
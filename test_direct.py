from main import generate_search_query, google_search, analyze_results, SearchResult

def test_search_flow():
    # 测试用户输入
    user_query = "世界未解之谜有几个？分别是什么"
    print(f"\n用户输入: {user_query}")

    # 1. 测试查询优化
    print("\n1. 正在优化搜索查询...")
    optimized_query = generate_search_query(user_query)
    print(f"优化后的查询: {optimized_query}")

    # 2. 测试Google搜索
    print("\n2. 正在执行Google搜索...")
    search_results = google_search(optimized_query)
    print("搜索结果:")
    for i, result in enumerate(search_results, 1):
        print(f"\n结果 {i}:")
        print(f"标题: {result.title}")
        print(f"链接: {result.link}")
        print(f"摘要: {result.snippet}")

    # 3. 测试结果分析
    print("\n3. 正在分析搜索结果...")
    analysis = analyze_results(user_query, search_results)
    print("分析结果:")
    print(analysis)

    # 4. 生成Markdown格式响应
    print("\n4. 生成Markdown格式响应:")
    markdown_response = f"# 搜索结果分析\n\n{analysis}\n\n## 参考链接\n\n"
    for result in search_results:
        markdown_response += f"- [{result.title}]({result.link})\n"
    print(markdown_response)

if __name__ == "__main__":
    test_search_flow()
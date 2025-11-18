# -*- coding: utf-8 -*-
"""
@File    :   tavily_search.py
@Time    :   2025/10/29 18:00
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
from tavily import TavilyClient

from langchain.tools import tool
from app.agents.tools.search.search_postprocessor import SearchResultPostProcessor
from app.config import settings


@tool("web_search")
def searcher(query: str, ):
    """
    user for web search
    """
    client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    response = client.search(query, include_images=True , include_raw_content="markdown", include_image_descriptions=True, timeout=120)

    all_results = []

    # 添加页面结果
    for result in response.get("results", []):
        all_results.append({
            "type": "page",
            "url": result.get("url"),
            "title": result.get("title"),
            "content": result.get("content", ""),
            "raw_content": result.get("raw_content", ""),
            "score": result.get("score", 0.5)
        })

    # 添加图片结果
    for image in response.get("images", []):
        all_results.append({
            "type": "image",
            "image_url": image.get("url"),
            "title": image.get("title"),
            "image_description": image.get("description", "")
        })

    # 一次性清洗所有结果
    postprocessor = SearchResultPostProcessor(
        min_score_threshold=0.45,
        max_content_length_per_page=5000,
        enable_stats=True
    )
    cleaned_results = postprocessor.process_results(all_results)

    return cleaned_results


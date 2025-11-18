# -*- coding: utf-8 -*-
"""
@File    :   search_postprocessor.py
@Time    :   2025/10/29 20:24
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   文件描述
"""
import base64
import logging
import re
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from urllib.parse import urlparse
from loguru import logger


@dataclass
class ProcessingStats:
    """处理统计信息"""
    original_count: int = 0
    after_dedup: int = 0
    after_filter: int = 0
    after_clean: int = 0
    final_count: int = 0
    base64_removed_count: int = 0
    truncated_count: int = 0


class SearchResultPostProcessor:
    """Search result post-processor - 优化版"""

    # 编译正则表达式以提升性能
    BASE64_PATTERN = re.compile(r"data:image/[^;]+;base64,[a-zA-Z0-9+/=]+")

    # 默认配置
    DEFAULT_MIN_SCORE = 0.0
    DEFAULT_MAX_LENGTH = 5000
    CONTENT_REDUCTION_THRESHOLD = 0.8  # 内容减少超过 20% 时记录日志

    def __init__(
            self,
            min_score_threshold: Optional[float] = None,
            max_content_length_per_page: Optional[int] = None,
            enable_stats: bool = False
    ):
        """
        Initialize the post-processor

        Args:
            min_score_threshold: 最低相关性分数阈值（None 表示不过滤）
            max_content_length_per_page: 每页最大内容长度（None 表示不截断）
            enable_stats: 是否启用统计信息收集
        """
        self.min_score_threshold = min_score_threshold or self.DEFAULT_MIN_SCORE
        self.max_content_length_per_page = max_content_length_per_page or self.DEFAULT_MAX_LENGTH
        self.enable_stats = enable_stats
        self.stats = ProcessingStats() if enable_stats else None

    def process_results(self, results: List[Dict]) -> List[Dict]:
        """
        处理搜索结果

        Args:
            results: 原始搜索结果列表

        Returns:
            处理后的结果列表
        """
        if not results:
            return []

        if self.enable_stats:
            self.stats = ProcessingStats(original_count=len(results))

        cleaned_results = []
        seen_urls: Set[str] = set()

        for result in results:
            # 1. 去重
            if not self._should_keep_result(result, seen_urls):
                continue

            if self.enable_stats:
                self.stats.after_dedup += 1

            # 2. 质量过滤
            if not self._meets_quality_threshold(result):
                continue

            if self.enable_stats:
                self.stats.after_filter += 1

            # 3. 清洗内容
            cleaned_result = self._clean_result(result)
            if not cleaned_result:
                continue

            if self.enable_stats:
                self.stats.after_clean += 1

            # 4. 截断长内容
            if self.max_content_length_per_page:
                cleaned_result = self._truncate_content(cleaned_result)

            cleaned_results.append(cleaned_result)

        # 5. 排序
        sorted_results = self._sort_results(cleaned_results)

        if self.enable_stats:
            self.stats.final_count = len(sorted_results)

        logger.info(
            f"搜索结果后处理完成: {len(results)} -> {len(sorted_results)}"
            + (f" | 统计: {self._format_stats()}" if self.enable_stats else "")
        )

        return sorted_results

    def _should_keep_result(self, result: Dict, seen_urls: Set[str]) -> bool:
        """判断是否保留结果（去重）"""
        url = result.get("url") or result.get("image_url", "")

        if not url:
            return True  # 保留没有 URL 的结果

        if url in seen_urls:
            return False

        seen_urls.add(url)
        return True

    def _meets_quality_threshold(self, result: Dict) -> bool:
        """判断结果是否满足质量阈值"""
        if result.get("type") != "page":
            return True

        if not self.min_score_threshold or self.min_score_threshold <= 0:
            return True

        score = result.get("score", 0)
        return score >= self.min_score_threshold

    def _clean_result(self, result: Dict) -> Optional[Dict]:
        """清洗结果（移除 base64 图片等）"""
        result_type = result.get("type")

        if result_type == "page":
            return self._clean_page_result(result)
        elif result_type == "image":
            return self._clean_image_result(result)
        else:
            # 未知类型，返回副本
            return result.copy()

    def _clean_page_result(self, result: Dict) -> Dict:
        """清洗页面类型结果"""
        cleaned = result.copy()
        # logger.info(f"========{cleaned}========")
        # 清洗 content
        if "content" in cleaned:
            original = cleaned["content"]
            cleaned_content = self.BASE64_PATTERN.sub(" ", original)
            cleaned["content"] = cleaned_content

            if self._is_significant_reduction(original, cleaned_content):
                logger.debug(f"从内容中移除了大量 base64 图片: {result.get('url', 'unknown')}")
                if self.enable_stats:
                    self.stats.base64_removed_count += 1

        # 清洗 raw_content
        if "raw_content" in cleaned:

            original = cleaned.get("raw_content", "")
            if original:
                cleaned_raw = self.BASE64_PATTERN.sub(" ", original)
            else:
                cleaned_raw = ""
            cleaned["raw_content"] = cleaned_raw

            if self._is_significant_reduction(original, cleaned_raw):
                logger.debug(f"从 raw_content 中移除了大量 base64 图片: {result.get('url', 'unknown')}")

        return cleaned

    def _clean_image_result(self, result: Dict) -> Optional[Dict]:
        """清洗图片类型结果"""
        cleaned = result.copy()

        # 清洗 image_url
        if "image_url" in cleaned and isinstance(cleaned["image_url"], str):
            if "data:image" in cleaned["image_url"]:
                original_url = cleaned["image_url"]
                cleaned_url = self.BASE64_PATTERN.sub(" ", original_url).strip()

                # 如果清洗后为空或不是有效 URL，丢弃该结果
                if not cleaned_url or not cleaned_url.startswith("http"):
                    logger.debug(f"移除无效的 base64 图片 URL: {original_url[:100]}...")
                    return None

                cleaned["image_url"] = cleaned_url
                if self.enable_stats:
                    self.stats.base64_removed_count += 1

        # 截断过长的描述
        if "image_description" in cleaned and isinstance(cleaned["image_description"], str):
            desc = cleaned["image_description"]
            if self.max_content_length_per_page and len(desc) > self.max_content_length_per_page:
                cleaned["image_description"] = desc[:self.max_content_length_per_page] + "..."
                logger.debug(f"截断过长的图片描述: {result.get('image_url', 'unknown')}")
                if self.enable_stats:
                    self.stats.truncated_count += 1

        return cleaned

    def _truncate_content(self, result: Dict) -> Dict:
        """截断过长内容"""
        truncated = result.copy()

        # 截断 content
        if "content" in truncated:
            content = truncated["content"]
            if len(content) > self.max_content_length_per_page:
                truncated["content"] = content[:self.max_content_length_per_page] + "..."
                logger.debug(f"截断过长内容: {result.get('url', 'unknown')}")
                if self.enable_stats:
                    self.stats.truncated_count += 1

        # 截断 raw_content（允许稍长一些）
        if "raw_content" in truncated:
            raw = truncated["raw_content"]
            max_raw_length = self.max_content_length_per_page * 2
            if len(raw) > max_raw_length:
                truncated["raw_content"] = raw[:max_raw_length] + "..."
                logger.debug(f"截断过长 raw_content: {result.get('url', 'unknown')}")
                if self.enable_stats:
                    self.stats.truncated_count += 1  # ✅ 补上这行

        return truncated

    def _sort_results(self, results: List[Dict]) -> List[Dict]:
        """按相关性分数排序"""
        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)

    def _is_significant_reduction(self, original: str, cleaned: str) -> bool:
        """判断清洗后内容是否显著减少"""
        if not original:
            return False
        return len(cleaned) < len(original) * self.CONTENT_REDUCTION_THRESHOLD

    def _format_stats(self) -> str:
        """格式化统计信息"""
        if not self.stats:
            return ""

        return (
            f"原始={self.stats.original_count}, "
            f"去重后={self.stats.after_dedup}, "
            f"过滤后={self.stats.after_filter}, "
            f"清洗后={self.stats.after_clean}, "
            f"最终={self.stats.final_count}, "
            f"移除base64={self.stats.base64_removed_count}, "
            f"截断={self.stats.truncated_count}"
        )

    def get_stats(self) -> Optional[ProcessingStats]:
        """获取统计信息"""
        return self.stats
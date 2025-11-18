"""
Chapter Dispatcher - 并行分发章节任务
"""
from loguru import logger
from langgraph.types import Send, Command
from app.agents.core.publisher.writing.state import DocumentState


def chapter_dispatcher(state: DocumentState) -> Command:
    """
    章节分发节点

    职责：
    1. 从 DocumentState 提取章节配置
    2. 构建符合 ChapterState 的输入数据
    3. 使用 Send API 并行发送到 chapter_subgraph

    Args:
        state: DocumentState

    Returns:
        Command 对象，包含 Send 列表
    """
    logger.info("\n🚀 [Chapter Dispatcher] 开始分发章节任务...")

    # ✅ 使用 main_document_outline 字段
    document_outline = state["main_document_outline"]
    total_chapters = len(document_outline.sections)

    logger.info(f"  ↳ 共 {total_chapters} 个章节")

    # === 构建 ChapterState 输入数据 ===
    send_list = []

    for idx, section in enumerate(document_outline.sections, start=1):
        # 计算章节目标字数
        if section.subsections:
            target_word_count = sum(sub.estimated_word_count for sub in section.subsections)
        else:
            target_word_count = section.estimated_words

        # 构建符合 ChapterState 的数据
        chapter_input = {
            "chapter_id": idx,
            "document_outline": document_outline,  # ✅ 传递给 subgraph 时用 document_outline
            "chapter_outline": section,  # ✅ 传递 Section 对象
            "target_word_count": target_word_count,
        }

        send_list.append(Send("chapter_subgraph", chapter_input))

    logger.info(f"  ✓ 分发完成，等待 Subgraph 执行...")
    logger.debug(f"  🔍 [DEBUG] Send 列表长度: {len(send_list)}")
    logger.debug(f"  🔍 [DEBUG] Send 目标: chapter_subgraph\n")

    # 返回 Command 对象
    return Command(goto=send_list)

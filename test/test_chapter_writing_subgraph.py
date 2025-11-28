# -*- coding: utf-8 -*-
"""
@File    :   test_chapter_writing_subgraph.py
@Time    :   2025/11/17
@Author  :   pygao
@Version :   1.0
@Contact :   pygao.1@outlook.com
@License :   (C)Copyright 2025, GienTech Technology Co.,Ltd. All rights reserved.
@Desc    :   Chapter Writing Subgraph 测试案例
"""

import asyncio
from datetime import datetime
from loguru import logger
from app.agents.core.publisher.subgraphs.section_writer.agent import create_chapter_subgraph
from app.agents.schemas.document_outline_schema import DocumentOutline, Section, SubSection
from dotenv import load_dotenv

load_dotenv()

def create_test_state():
    """
    创建测试用的初始状态
    """
    # 创建文档大纲
    document_outline = DocumentOutline(
        title="人工智能技术发展报告",
        language="zh",
        target_audience="技术管理者、AI研究人员、投资决策者",
        writing_style="business",
        writing_tone="authoritative",
        writing_purpose="为读者提供AI技术发展的全面视角，包括技术趋势、应用案例和未来展望",
        key_themes=[
            "大模型技术演进",
            "AI商业应用实践",
            "技术伦理与监管",
            "未来发展趋势"
        ],
        estimated_total_words=8000,
        sections=[
            Section(
                title="第一章 大模型技术现状",
                description="分析当前大语言模型的技术发展现状、核心突破和主流架构",
                writing_guidance="采用技术演进的时间线视角，从架构创新到模型对比到训练技术，层层递进。本章采用纯文字叙述方式，通过清晰的逻辑层次和数据对比来展现技术发展脉络，不使用图表。注重技术术语的准确性，同时配以通俗解释确保技术管理者能够理解",
                content_requirements="需要包含：1) Transformer架构演进脉络 2) 主流模型的参数规模和性能对比数据 3) 开源vs闭源生态分析 4) 训练技术的效率优化方法",
                visual_elements=False,
                estimated_words=1800,
                writing_priority="high",
                subsections=[
                    SubSection(
                        sub_section_title="Transformer架构演进",
                        description="追溯Transformer从诞生到现在的技术演进路径，包括attention机制的优化、位置编码的改进等",
                        writing_guidance="""
                        【段落1 - 起源与突破】(150-200字)
                        - 从2017年原始论文切入，说明Transformer的革命性意义
                        - 简述其替代RNN/LSTM成为主流架构的核心原因
                        - 点明自注意力机制(Self-Attention)解决的关键问题
                        - 采用"问题-解决方案-影响"的叙述逻辑

                        【段落2 - 核心机制解析】(250-300字)
                        - 详细解释Multi-Head Attention的工作原理和价值
                        - 说明位置编码(Positional Encoding)在序列建模中的作用
                        - 介绍Feed-Forward Network和残差连接的设计考量
                        - 解释并行化计算相比RNN的优势
                        - 写作要求：使用准确的技术术语，但每个术语后跟一句通俗解释
                        - 面向技术管理者，避免过深的数学公式，重点讲清楚"是什么"和"为什么重要"

                        【段落3 - 关键优化演进】(200-250字)
                        - 按时间线梳理主要改进方向：计算效率优化(Sparse Attention、Flash Attention)、扩展性改进(Multi-Query Attention、Grouped-Query Attention)
                        - 每项改进说明：技术原理、解决的问题、性能提升幅度
                        - 采用"技术名称 + 提出年份 + 核心创新点 + 量化效果"的标准格式
                        - 用对比的方式体现技术进步(如"训练速度提升X倍"、"显存占用降低X%")
                        - 结尾总结：这些优化使得超大规模模型训练成为可能
                        """,
                        estimated_word_count=650
                    ),
                    SubSection(
                        sub_section_title="主流模型性能对比",
                        description="对比GPT系列、Claude、LLaMA等主流模型在各种基准测试上的表现",
                        writing_guidance="""
                        【段落1 - 模型概览与分类】(200-250字)
                        - 列举当前市场主流大模型，按闭源/开源分类
                        - 按参数规模分层：超大规模(>1T)、大规模(100B-1T)、中等规模(10B-100B)、小规模(<10B)
                        - 每个规模段举2-3个代表性模型
                        - 采用"模型名称 | 开发机构 | 参数规模 | 发布时间 | 主要定位"的格式
                        - 为后续性能对比建立清晰的参照框架

                        【段落2 - 综合能力基准测试】(350-400字)
                        - 介绍MMLU(多任务语言理解)作为最权威的综合评测基准
                        - 列举top模型在MMLU上的得分，展现性能梯队
                        - 拆解评测维度：数学推理、代码生成、常识推理、多语言能力等
                        - 每个维度对比主流模型的表现，说明差距和原因
                        - 分析性能差异的技术根源：训练数据质量、训练方法(如RLHF)、模型规模等
                        - 指出闭源与开源模型的性能差距及其变化趋势
                        - 数据呈现方式：用文字描述排名和具体得分，采用"模型A达到X%，领先模型B约Y个百分点"的格式
                        - 结尾总结：当前性能格局和演进趋势

                        【段落3 - 专项能力深度对比】(300-350字)
                        - 选择3-4个关键专项能力进行深入对比：代码能力、数学推理、多语言能力等
                        - 每个专项说明：
                          * 使用的评测基准(如代码用HumanEval、数学用GSM8K)
                          * 主流模型在该基准上的表现排名
                          * 闭源与开源模型的差距
                          * 差距背后的技术原因分析
                        - 代码能力：强调逻辑推理的精确性要求
                        - 数学推理：指出复杂多步推理是当前共同短板
                        - 多语言能力：说明语言资源不均导致的性能差异
                        - 结论性判断：闭源模型的优势领域、开源模型的追赶进展、未来趋势预测
                        - 采用对比分析法，突出差异和原因
                        """,
                        estimated_word_count=900
                    ),
                    SubSection(
                        sub_section_title="开源vs闭源模型生态",
                        description="分析开源模型和闭源模型各自的发展路径、优劣势和生态建设",
                        writing_guidance="""
                        【段落1 - 生态格局概述】(150-200字)
                        - 定义开源与闭源模型的本质区别(代码、权重、使用方式)
                        - 列举代表性开源模型家族和闭源模型产品
                        - 说明两种路径各自的市场定位和用户群体
                        - 给出市场占有率或使用趋势的宏观数据
                        - 点明这不是非此即彼的竞争，而是互补共存的关系

                        【段落2 - 多维度对比分析】(350-400字)
                        - 从技术、成本、可控性三个核心维度展开对比
                        - 技术维度：
                          * 性能差距的量化描述(在主要基准上的差距)
                          * 创新速度对比(闭源的快速迭代 vs 开源的社区创新)
                          * 技术透明度差异及其影响
                        - 成本维度：
                          * 使用成本：API调用费用 vs 自部署硬件成本
                          * 初始投入：零成本接入 vs 一次性硬件投资
                          * 长期运维成本对比
                          * 给出典型场景的成本测算示例
                        - 可控性维度：
                          * 数据安全：本地部署vs云端API
                          * 定制化能力：微调灵活度、行为控制
                          * 部署灵活性：适应不同基础设施需求
                        - 采用"对比表述"而非简单列举，如"在X方面，闭源模型具有Y优势，但开源模型提供Z灵活性"

                        【段落3 - 应用场景建议】(200-250字)
                        - 给出选型决策框架
                        - 闭源模型适用场景：追求极致性能、快速上线、缺乏技术团队、成本不敏感
                        - 开源模型适用场景：数据敏感型行业、深度定制需求、成本敏感、有技术能力
                        - 混合方案：通用任务用闭源API + 核心业务用开源自部署
                        - 未来趋势预测：两者将长期共存，开源性能差距持续缩小，企业选择更加多元化
                        - 给出决策树式的建议逻辑，帮助读者根据自身情况选择
                        """,
                        estimated_word_count=750
                    ),
                    SubSection(
                        sub_section_title="训练技术与效率优化",
                        description="介绍大模型训练中的关键技术，包括分布式训练、混合精度、参数高效微调等",
                        writing_guidance="""
                        【段落1 - 分布式训练技术】(200-250字)
                        - 开篇说明为何需要分布式训练(单卡显存无法容纳超大模型)
                        - 介绍三种主要并行策略：数据并行、模型并行、流水线并行
                        - 每种策略说明：工作原理、适用场景、优缺点
                        - 以某个超大规模模型训练为例，说明所需GPU数量、训练时间、成本量级
                        - 提及主流分布式训练框架(如DeepSpeed、Megatron)的贡献
                        - 强调分布式训练是超大模型成为可能的基础设施

                        【段落2 - 效率优化技术】(250-300字)
                        - 介绍4-5种关键的效率优化技术
                        - 混合精度训练：原理(FP16/BF16替代FP32)、收益(显存和速度)
                        - 梯度累积：如何在小batch下模拟大batch效果
                        - 梯度检查点(Gradient Checkpointing)：以计算换显存的权衡
                        - Flash Attention等算子优化：针对attention计算的加速
                        - 每项技术说明：技术原理、性能提升量化、引入的代价或限制
                        - 采用"技术名称 + 核心思想 + 量化收益 + 适用场景"的格式
                        - 总结：这些优化使训练成本大幅降低，加速了大模型的普及

                        【段落3 - 参数高效微调】(180-220字)
                        - 介绍LoRA、QLoRA、Adapter等轻量化微调方法
                        - 说明核心思想：仅训练少量参数而非全量参数
                        - 量化收益：训练参数量减少到百分之几、显存需求降低倍数
                        - 实际价值：使中小企业也能负担模型定制
                        - 指出这是开源模型生态繁荣的重要推动力
                        - 提及这些技术的局限性(适用场景、性能损失)
                        - 结尾：参数高效方法正成为模型定制的主流范式
                        """,
                        estimated_word_count=650
                    )
                ]
            ),

            Section(
                title="第二章 AI商业应用实践",
                description="深入分析AI技术在各行业的落地应用案例、实施路径和ROI评估",
                writing_guidance="以实际案例为主导，采用'行业背景-痛点分析-解决方案-效果评估'的四段式结构。强调可量化的业务价值和实施经验，每个案例都要有投入产出数据。配合流程图和效果对比图表展示实施路径和成果",
                content_requirements="需要包含：1) 5个不同行业的深度案例 2) 每个案例的ROI数据和实施周期 3) 实施中的挑战和解决方案 4) 可复制的实施经验总结",
                visual_elements=True,
                estimated_words=2200,
                writing_priority="high",
                subsections=[
                    SubSection(
                        sub_section_title="金融行业：智能风控与客服",
                        description="分析AI在银行、保险等金融机构的风控系统和客户服务中的应用",
                        writing_guidance="""
                        【段落1 - 行业背景与痛点】(150-180字)
                        - 描述金融行业面临的核心挑战：欺诈检测、客服成本、审批效率
                        - 传统规则引擎的局限性：无法适应新型欺诈手段、误报率高
                        - 人工客服的成本压力和客户满意度问题
                        - 给出行业级的成本数据或痛点量化指标
                        - 引出AI技术作为解决方案的必然性

                        【段落2 - AI解决方案】(280-320字)
                        - 分两个应用场景展开：风控应用和智能客服
                        - 风控应用：
                          * 技术方案：机器学习模型分析交易行为、设备指纹、社交网络
                          * 具体案例：某类型金融机构的部署效果(检测准确率提升、误报率下降)
                          * 技术实现：图神经网络、时序异常检测等算法的应用
                        - 智能客服：
                          * 技术方案：基于大模型的对话系统
                          * 具体案例：某机构的上线效果(自动化处理比例、成本下降幅度)
                          * 处理场景：保单查询、理赔进度、产品推荐等
                        - 每个方案都要说明技术选型理由和实际效果

                        【段落3 - 实施经验与ROI】(200-250字)
                        - 实施路径：POC验证阶段、小范围试点、全面推广的时间周期
                        - 投入成本拆解：系统开发成本、硬件投入、年度运维成本
                        - 回报分析：成本节省、效率提升、风险降低的量化数据
                        - 给出盈亏平衡时间和中长期收益预测
                        - 关键成功因素：数据质量、系统集成、持续优化等
                        - 实施风险点：数据隐私合规、模型可解释性、系统稳定性要求
                        - 提供可复制的经验总结
                        """,
                        estimated_word_count=650
                    ),
                    SubSection(
                        sub_section_title="医疗健康：辅助诊断与药物研发",
                        description="探讨AI在医学影像诊断、病历分析和新药研发中的突破性应用",
                        writing_guidance="""
                        【段落1 - 医学影像诊断】(250-300字)
                        - 应用场景：肺部CT筛查、眼底病变检测、皮肤病识别等
                        - 技术方案：深度学习模型(CNN、Vision Transformer)进行图像分类和分割
                        - 性能水平：AI系统的敏感性、特异性指标,与医生水平的对比
                        - 实际价值：诊断时间缩短、基层医院能力提升、漏诊率降低
                        - 具体案例：某类型AI筛查系统的部署效果
                        - 监管挑战：医疗器械认证要求、审批周期、临床验证标准
                        - 说明医疗AI的特殊性：安全性要求高、审批严格、应用谨慎

                        【段落2 - 药物研发加速】(250-300字)
                        - 开篇说明传统药物研发的痛点：周期长、成本高、成功率低
                        - AI切入点：靶点发现、分子设计、临床试验优化
                        - 靶点发现案例：蛋白结构预测(如AlphaFold)的突破和应用
                        - 分子生成案例：AI辅助的候选化合物设计效率
                        - 实际成效：已进入临床阶段的AI辅助药物数量、预期研发周期缩短幅度
                        - 强调这是前沿应用，成果仍需长期临床验证
                        - 展望AI对药物研发范式的深远影响

                        【段落3 - 挑战与展望】(150-200字)
                        - 数据挑战：医疗数据分散、标注成本高、隐私保护严格
                        - 验证要求：需要大规模临床研究证明有效性和安全性
                        - 医生接受度：AI是辅助工具而非替代，需要工作流程调整
                        - 未来方向：多模态诊断融合、个性化医疗方案推荐
                        - 总结：医疗AI潜力巨大但路径漫长，需要技术与临床的深度结合
                        """,
                        estimated_word_count=700
                    ),
                    SubSection(
                        sub_section_title="制造业：智能质检与预测性维护",
                        description="展示AI在生产质量控制和设备管理中的应用价值",
                        writing_guidance="""
                        【段落1 - 视觉质检应用】(200-250字)
                        - 传统质检的局限：人工疲劳、主观性强、速度慢、微小缺陷难发现
                        - AI视觉质检方案：计算机视觉检测表面缺陷、尺寸偏差、装配错误
                        - 技术实现：高分辨率工业相机 + 目标检测算法,检测精度级别
                        - 具体案例：某制造企业部署后的效果(检测速度、漏检率、准确率的改善)
                        - ROI分析：系统投入成本 vs 节省的人工成本和质量成本
                        - 量化不良品流出率的下降幅度

                        【段落2 - 预测性维护】(250-300字)
                        - 维护模式演进：事后维护 → 定期维护 → 预测性维护
                        - AI预测性维护的价值：提前预警故障、优化维修计划
                        - 数据采集：通过IoT传感器(振动、温度、电流等)收集设备运行数据
                        - 技术实现：时序异常检测模型、故障模式识别
                        - 具体案例：某工厂设备维护系统的效果(非计划停机时间、设备利用率的改善)
                        - 成本效益分析：维护成本下降、生产损失减少的量化数据
                        - 提前预警时间窗口的价值

                        【段落3 - 实施建议】(150-200字)
                        - 数据基础建设：先完善传感器网络和数据采集体系
                        - 切入策略：从高价值、高频次的质检和维护问题入手
                        - 人机协同：AI提供建议，人工做最终决策和干预
                        - 持续优化：根据实际反馈迭代模型
                        - 投入规划：中型制造企业的初期投入规模、规模化推广路径
                        - 提供分阶段实施的路线图建议
                        """,
                        estimated_word_count=650
                    ),
                    SubSection(
                        sub_section_title="零售电商：个性化推荐与智能营销",
                        description="分析AI驱动的精准营销和用户体验优化",
                        writing_guidance="""
                        【段落1 - 推荐系统升级】(180-220字)
                        - 从协同过滤到深度学习：传统推荐的冷启动和稀疏性问题
                        - 大模型带来的新能力：语义理解、用户意图建模、跨域推荐
                        - 具体案例：某电商平台引入大模型推荐系统的效果(点击率、转化率提升)
                        - 技术创新点：多模态理解(图片+文本+行为)、实时个性化、对话式推荐
                        - 说明大模型相比传统方法的优势所在

                        【段落2 - 智能营销自动化】(200-250字)
                        - 内容生成：自动创作商品详情、营销文案、短视频脚本
                        - 具体案例：某品牌使用AI内容生成的效果(创作效率、用户互动率)
                        - 精准投放：AI分析用户画像优化广告投放策略
                        - 具体案例：某企业AI优化投放后的ROI改善
                        - 智能客服：售前咨询自动化处理,转化率提升
                        - 说明AI在营销全链路的价值

                        【段落3 - 数据驱动的选品与定价】(180-220字)
                        - 市场趋势分析：AI分析社交媒体、搜索趋势预测爆款
                        - 动态定价：根据供需、竞品、库存实时调价
                        - 具体案例：某平台动态定价的效果(毛利率、库存周转率改善)
                        - 实施建议：需要完善数据中台,分阶段实施路径(先推荐-后营销-再定价)
                        - 强调数据资产和技术能力的重要性
                        """,
                        estimated_word_count=600
                    ),
                    SubSection(
                        sub_section_title="企业服务：办公自动化与知识管理",
                        description="介绍AI在企业内部效率提升和知识沉淀中的应用",
                        writing_guidance="""
                        【段落1 - 文档智能处理】(150-180字)
                        - 应用场景：合同审阅、财务票据识别、会议纪要生成
                        - 具体案例：某类型企业使用AI处理文档的效果(处理时间、准确率)
                        - 技术方案：OCR + NLP + 知识图谱实现文档理解和风险识别
                        - 价值：释放知识工作者时间,聚焦高价值工作

                        【段落2 - 企业知识库】(180-220字)
                        - 痛点：知识分散在各个系统、检索困难、经验难以传承
                        - AI解决方案：基于大模型的智能问答系统
                        - 具体案例：某企业搭建知识助手的效果(查询解决时间、新员工培训周期)
                        - 功能：自动索引文档、精准答案检索、相关内容推荐
                        - 持续学习：根据反馈优化知识库质量

                        【段落3 - 实施框架】(120-150字)
                        - 分阶段实施路径：试点场景选择 → 数据积累优化 → 全面推广
                        - 每个阶段的关键任务和里程碑
                        - 投入规模：中型企业的初期投入和持续运营成本
                        - 提供可操作的实施时间表建议
                        """,
                        estimated_word_count=500
                    )
                ]
            ),

            Section(
                title="第三章 技术伦理与监管挑战",
                description="探讨AI发展中的伦理问题、安全风险和全球监管态势",
                writing_guidance="采用问题导向的写作方式，客观呈现争议性话题的多方观点。避免简单的价值判断，而是分析问题的复杂性、不同利益相关方的诉求、可能的解决路径。引用权威机构的研究和政策文件增强可信度。配合风险矩阵图和各国监管政策对比表",
                content_requirements="需要包含：1) 主要伦理问题的分类和典型案例 2) 技术解决方案和局限性 3) 各国监管政策的核心差异 4) 企业合规建议",
                visual_elements=True,
                estimated_words=1600,
                writing_priority="medium",
                subsections=[
                    SubSection(
                        sub_section_title="数据隐私与安全",
                        description="分析AI系统中的数据收集、使用和保护问题",
                        writing_guidance="""
                        【段落1 - 数据隐私风险】(180-220字)
                        - 核心问题：训练数据可能包含敏感信息、模型可能记忆训练数据
                        - 具体风险：通过模型逆向工程提取隐私信息的可能性
                        - 典型案例：某AI公司因数据使用不当被罚款的案例
                        - 提出关键问题：如何平衡模型性能和隐私保护？用户是否充分理解数据使用方式？
                        - 说明问题的复杂性：不是简单的技术问题，涉及法律、伦理、商业多重考量

                        【段落2 - 技术解决方案】(200-250字)
                        - 介绍主流隐私保护技术：差分隐私、联邦学习、数据脱敏
                        - 每种技术说明：核心原理、隐私保护程度、性能代价
                        - 差分隐私：添加噪声防止单点识别，可能降低精度
                        - 联邦学习：数据本地化训练，但增加通信开销
                        - 数据脱敏：删除敏感标识，但可能影响模型效果
                        - 具体案例：某行业应用隐私保护技术的实践
                        - 坦承技术局限：完全的隐私保护与高性能难以兼得，需要权衡

                        【段落3 - 合规要求】(180-220字)
                        - 梳理主要法规：GDPR、《个人信息保护法》、CPRA等
                        - 核心要求：用户知情同意、数据最小化原则、删除权、可解释性
                        - 企业合规实践：数据分类分级、生命周期管理、隐私影响评估
                        - 合规成本：大型企业需要的团队规模和年度投入
                        - 给出合规建议：建立数据治理体系、定期审计、培训意识
                        """,
                        estimated_word_count=600
                    ),
                    SubSection(
                        sub_section_title="算法偏见与公平性",
                        description="讨论AI系统中的歧视性问题及其社会影响",
                        writing_guidance="""
                        【段落1 - 偏见来源与表现】(200-250字)
                        - 分析偏见产生的根源：数据偏见、算法偏见、反馈循环
                        - 数据偏见：训练数据不平衡，反映历史或社会歧视
                        - 典型案例：招聘AI系统对性别的偏见案例
                        - 算法偏见：模型设计和优化目标可能强化不公平
                        - 典型案例：信贷评分对族裔的系统性偏见
                        - 反馈循环：偏见决策进一步污染数据，形成恶性循环
                        - 说明问题的社会危害：加剧不平等、损害特定群体利益

                        【段落2 - 检测与缓解】(220-270字)
                        - 公平性评估方法：统计性公平(群体层面)、个体公平(个体层面)
                        - 技术缓解手段：数据重采样、对抗去偏、公平性约束优化
                        - 每种方法的原理和效果
                        - 具体案例：某公司的公平性检测和改进实践
                        - 权衡问题：完全公平可能导致整体性能下降，需要在公平与效率间平衡
                        - 不同公平性定义可能相互冲突的困境
                        - 组织措施：多元化团队、独立审计、持续监控

                        【段落3 - 政策与标准】(150-200字)
                        - 监管动态：欧盟AI法案对高风险系统的偏见评估要求
                        - 行业标准：IEEE、ISO等组织制定的公平性规范
                        - 企业责任：建立AI伦理委员会、发布透明度报告
                        - 未来趋势：公平性将成为AI产品的必备特性
                        - 争议点：对"公平"的定义存在分歧，需要社会共识
                        """,
                        estimated_word_count=620
                    ),
                    SubSection(
                        sub_section_title="模型安全与对抗攻击",
                        description="分析AI系统面临的安全威胁和防御措施",
                        writing_guidance="""
                        【段落1 - 攻击类型】(200-250字)
                        - 介绍主要攻击类型：对抗样本、模型窃取、数据投毒、提示注入
                        - 对抗样本：微小扰动导致误判，举自动驾驶的危险案例
                        - 模型窃取：通过查询接口逆向重建模型
                        - 数据投毒：在训练数据中植入恶意样本
                        - 提示注入：诱导大模型输出有害内容,举绕过安全过滤的案例
                        - 说明每种攻击的危害和现实风险

                        【段落2 - 防御策略】(200-250字)
                        - 主要防御技术：对抗训练、输入验证、模型水印、输出审查
                        - 每种技术的原理和防御效果
                        - 对抗训练：用对抗样本增强鲁棒性
                        - 多层防御架构：输入检测、实时监控、输出过滤
                        - 具体案例：某大模型服务商的安全防护体系和拦截效果
                        - 坦承局限：防御措施增加延迟和成本,攻防是持续对抗过程

                        【段落3 - 安全实践】(150-200字)
                        - 企业安全实践：红队测试、漏洞赏金计划、分层部署、应急响应
                        - 每种实践的目的和实施方法
                        - 投入建议：安全投入应占AI项目预算的合理比例
                        - 未来方向：可验证AI、形式化验证、零信任架构
                        - 强调安全是持续过程，不是一次性工作
                        """,
                        estimated_word_count=600
                    ),
                    SubSection(
                        sub_section_title="全球监管政策比较",
                        description="对比主要国家和地区的AI监管框架",
                        writing_guidance="""
                        【段落1 - 欧盟：风险分级监管】(180-220字)
                        - 介绍《人工智能法案》的核心思想：按风险等级分类管理
                        - 四个风险等级：不可接受、高风险、有限风险、最小风险
                        - 高风险领域举例：关键基础设施、教育、招聘、执法、生物识别
                        - 合规要求：风险评估、数据治理、技术文档、人类监督、透明度
                        - 违规处罚：罚款额度的量级
                        - 总结欧盟模式：监管严格、注重风险防范

                        【段落2 - 美国：行业自律为主】(160-200字)
                        - 联邦层面：AI权利法案蓝图，强调自愿性原则
                        - 行业主导：科技公司自我监管，行业联盟制定标准
                        - 州级立法：部分州出台更严格的要求
                        - 监管重点：反垄断、数据隐私、关键基础设施安全
                        - 总结美国模式：创新优先,缺乏统一联邦框架

                        【段落3 - 中国：分类分级+安全审查】(200-250字)
                        - 法规体系：《生成式人工智能管理办法》《算法推荐管理规定》等
                        - 监管原则：促进发展与防范风险并重
                        - 核心要求：算法备案、安全评估、内容审核、数据合规
                        - 行业实践：提供服务需通过审批,审批周期
                        - 国际对比：相比欧盟更强调内容安全,相比美国更强调政府监管
                        - 对企业影响：合规成本较高但规则相对明确
                        - 总结三种模式的差异和各自逻辑
                        """,
                        estimated_word_count=580
                    )
                ]
            ),

            Section(
                title="第四章 未来发展趋势",
                description="预测AI技术的演进方向和可能带来的深远影响",
                writing_guidance="基于当前技术轨迹和产业动态进行理性的趋势分析。避免科幻式的臆想，而是从技术演进的内在逻辑、产业需求、资源约束等角度推演未来。区分近期(2-3年)、中期(5-8年)、远期(10年+)的不同发展阶段。引用权威研究机构的预测数据和产业报告。配合技术路线图和市场规模预测图",
                content_requirements="需要包含：1) 技术演进的关键里程碑 2) 新兴应用场景及其影响 3) 产业格局可能的变化 4) 投资机会分析",
                visual_elements=True,
                estimated_words=1800,
                writing_priority="high",
                subsections=[
                    SubSection(
                        sub_section_title="从大模型到超级智能",
                        description="分析通用人工智能(AGI)的发展路径和技术突破方向",
                        writing_guidance="""
                        【段落1 - 当前模型的局限】(180-220字)
                        - 分析当前大模型的能力边界：推理、规划、持续学习等方面的不足
                        - 具体表现：在复杂推理任务上的准确率水平、多步规划的不稳定性
                        - 幻觉问题：生成虚假信息的现象和原因
                        - 泛化能力：分布外任务的性能下降
                        - 资源消耗：超大模型训练成本，难以持续规模扩张
                        - 说明这些局限阻碍了向AGI的演进

                        【段落2 - 技术演进方向】(300-350字)
                        - 分析未来可能的技术突破方向
                        - 多模态融合：视觉、听觉、文本统一建模的进展和挑战
                        - 推理增强：结合符号推理提升逻辑能力,介绍思维链等方法
                        - 持续学习：模型从交互中进化，如何避免灾难性遗忘
                        - 具身智能：与物理世界交互的AI(机器人、自动驾驶)
                        - 计算效率：新架构探索突破Transformer的局限
                        - 每个方向说明：当前进展、主要挑战、预期突破时间
                        - 强调这些是方向而非确定路径，存在不确定性

                        【段落3 - AGI时间线预测】(200-250字)
                        - 业界观点梳理：乐观派和保守派的不同预测及其理由
                        - 分阶段里程碑：
                          * 近期(2-3年)：多模态成为标配，推理能力提升
                          * 中期(5-8年)：基本的自主学习和任务规划能力
                          * 远期(10年+)：接近人类水平的通用智能？
                        - 不确定性分析：可能需要架构创新突破,而非单纯扩大规模
                        - 伴随风险：可控性和安全性技术需要同步发展
                        - 理性态度：既不过度乐观也不盲目悲观,持续关注技术进展
                        """,
                        estimated_word_count=730
                    ),
                    SubSection(
                        sub_section_title="AI Agent与自动化浪潮",
                        description="探讨AI智能体在各领域替代人类工作的可能性",
                        writing_guidance="""
                        【段落1 - AI Agent的能力跃迁】(200-250字)
                        - 从工具到Agent的转变：从被动响应到主动执行任务
                        - 关键能力：任务规划、工具使用、反思纠错、多轮协作
                        - 现有产品举例：AutoGPT、GPT-4 Code Interpreter等
                        - 能力水平：目前能独立完成的任务类型和比例
                        - 技术瓶颈：长期规划不足、错误恢复困难、缺乏常识
                        - 预测未来1-2年Agent能力的提升方向

                        【段落2 - 职业影响分析】(280-330字)
                        - 按影响程度分类分析不同职业
                        - 高影响职业：数据分析、客服、初级编程、内容创作、财务核算
                          * 引用权威机构(如麦肯锡)的预测数据
                        - 中度影响：需要人类判断但流程化的工作(法务助理、初级设计)
                        - 低影响：高度依赖人际互动、创造性、伦理判断的工作
                        - 新职业诞生：AI训练师、提示工程师、系统审计员、人机协作专家
                        - 能力转型：从执行任务转向监督AI、处理异常、战略决策
                        - 强调这是渐进过程，不是突然的大规模失业

                        【段落3 - 社会适应挑战】(220-270字)
                        - 就业结构变化：短期失业增加 vs 长期创造新岗位
                        - 教育体系调整：更注重批判性思维、创造力、情商等AI难以替代的能力
                        - 收入分配问题：AI带来的生产力提升收益如何分配
                        - 政策应对：全民基本收入、终身学习体系、灵活就业保障等讨论
                        - 企业责任：负责任的自动化、员工再培训支持
                        - 时间尺度：变化将在10-20年逐步展开
                        - 结论：需要社会各方协同应对，不能仅靠技术或市场
                        """,
                        estimated_word_count=750
                    ),
                    SubSection(
                        sub_section_title="边缘AI与端侧部署",
                        description="分析AI从云端走向终端设备的趋势",
                        writing_guidance="""
                        【段落1 - 端侧AI的驱动力】(150-200字)
                        - 为什么需要端侧AI：隐私保护、低延迟、成本节约、离线可用
                        - 每个驱动力的具体场景说明
                        - 当前进展：智能手机集成AI芯片的能力水平
                        - 应用案例：本地语音识别、图像处理、实时翻译等

                        【段落2 - 技术实现路径】(220-270字)
                        - 模型压缩技术：剪枝、量化、知识蒸馏
                        - 压缩效果：将大模型压缩到可在端侧运行的规模
                        - 专用硬件：NPU、TPU、神经网络加速器的发展
                        - 硬件能力：主流芯片的算力水平
                        - 云边协同：简单任务本地,复杂任务云端的混合模式
                        - 进展案例：小参数量模型在端侧的实用级表现
                        - 预测未来2-3年的技术进展

                        【段落3 - 应用前景】(180-220字)
                        - 主要应用领域：智能家居、可穿戴设备、工业IoT、自动驾驶
                        - 每个领域的价值和进展
                        - 智能家居：本地处理保护隐私
                        - 可穿戴：实时健康监测
                        - 工业IoT：设备自主决策
                        - 自动驾驶：车载AI确保安全
                        - 市场预测：边缘AI市场规模的增长预期(引用权威数据)
                        """,
                        estimated_word_count=620
                    ),
                    SubSection(
                        sub_section_title="产业格局与投资机会",
                        description="分析AI产业链各环节的发展机会和投资价值",
                        writing_guidance="""
                        【段落1 - 产业链分层】(200-250字)
                        - 将AI产业链分为基础层、模型层、应用层
                        - 基础层：芯片、云计算、数据中心
                          * 代表企业和市场格局
                          * 投资逻辑：算力需求的确定性增长
                        - 模型层：基础模型开发、模型优化工具
                          * 头部玩家和竞争格局
                          * 投资逻辑：大厂主导,创业公司聚焦垂直
                        - 应用层：行业解决方案、AI工具软件
                          * 机会最多但竞争激烈
                        - 产业链价值分布分析

                        【段落2 - 热点投资赛道】(280-330字)
                        - AI基础设施：GPU服务器、AI芯片、液冷技术、数据标注
                          * 投资确定性分析：为什么这是最确定的受益环节
                          * 头部企业的市场表现
                        - 企业服务AI：RPA+AI、智能客服、AI辅助开发
                          * 高增长逻辑：企业数字化转型需求
                          * 成功案例的收入规模
                        - 垂直行业AI：医疗、金融、工业AI
                          * 高壁垒：需要深厚行业know-how
                        - AI安全与治理：新兴赛道，监管驱动需求
                        - 每个赛道说明：市场规模、增长预期、关键成功因素

                        【段落3 - 投资风险与策略】(200-250字)
                        - 主要风险：技术迭代、估值泡沫、监管不确定性、竞争格局
                        - 每种风险的具体表现和应对
                        - 估值泡沫：当前AI公司估值水平,需警惕调整
                        - 竞争风险：大厂可能快速复制创业公司创新
                        - 投资策略建议：
                          * 保守型：基础设施和芯片龙头
                          * 成长型：有清晰商业模式的应用层公司
                          * 激进型：前沿技术布局,但控制比例
                        - 风险控制：分散投资、阶段性评估、关注基本面
                        """,
                        estimated_word_count=730
                    )
                ]
            ),

            Section(
                title="总结与展望",
                description="回顾全文核心观点，提出行动建议",
                writing_guidance="简明扼要地总结各章节要点，不重复具体内容和数据。提炼核心洞察和结论。针对不同读者群体(技术管理者、研究人员、投资者)提供可操作的建议。展望未来3-5年AI发展的关键节点和观察指标。结语要有前瞻性和启发性",
                content_requirements="需要包含：1) 核心结论提炼 2) 对不同角色的差异化建议 3) 未来关键观察指标 4) 结语",
                visual_elements=False,
                estimated_words=600,
                writing_priority="high",
                subsections=[]
            )
        ]
    )
    # 创建章节大纲（从 sections 中取第一个）
    chapter_outline = document_outline.sections[0]

    # 创建初始状态
    initial_state = {
        "chapter_id": 1,
        "document_outline": document_outline,
        "chapter_outline": chapter_outline,
        # Writer 角色相关字段
        "writer_role": "技术分析师",
        "writer_profile": "资深AI技术分析师，拥有10年以上技术研究和报告撰写经验，擅长将复杂技术概念转化为易懂的商业洞察",
        "writing_principles": [
            "保持客观中立的分析立场",
            "数据驱动，论点有据可查",
            "技术术语配以通俗解释",
            "结构清晰，层次分明",
            "注重实用性和可操作性"
        ],
        # 可选字段
        # "output_dir": "./test_output",  # 如果需要保存文件可以启用
    }

    return initial_state


async def test_chapter_writing_subgraph():
    """
    测试 Chapter Writing Subgraph 的完整流程
    """
    logger.info("=" * 70)
    logger.info("🧪 开始测试 Chapter Writing Subgraph")
    logger.info(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70 + "\n")

    # 1. 创建测试状态
    logger.info("📝 步骤 1/3: 创建测试状态...")
    initial_state = create_test_state()
    logger.info(f"   ✓ 章节ID: {initial_state['chapter_id']}")
    logger.info(f"   ✓ 章节标题: {initial_state['chapter_outline'].title}")
    logger.info(f"   ✓ 子章节数: {len(initial_state['chapter_outline'].subsections)}\n")

    # 2. 创建 Subgraph
    logger.info("🏗️  步骤 2/3: 构建 Chapter Writing Subgraph...")
    try:
        chapter_graph = create_chapter_subgraph()
        logger.info("   ✓ Subgraph 构建成功\n")
    except Exception as e:
        logger.error(f"   ✗ Subgraph 构建失败: {e}")
        raise

    # 3. 执行 Subgraph
    logger.info("🚀 步骤 3/3: 执行 Chapter Writing 流程...")
    logger.info("   节点执行顺序: researcher → writer → reviewer → [decision] → reviser/finalizer\n")

    try:
        # 异步调用
        result = await chapter_graph.ainvoke(initial_state)

        logger.info("\n" + "=" * 70)
        logger.info("✅ Chapter Writing Subgraph 执行完成!")
        logger.info("=" * 70 + "\n")

        # 4. 验证结果
        logger.info("📊 执行结果验证:")

        # 检查必须的字段（基于新的 ChapterState 结构）
        assert "final_chapter_output" in result, "缺少 final_chapter_output 字段"
        assert "draft" in result, "缺少 draft 字段"
        assert "latest_review" in result, "缺少 latest_review 字段"

        # 获取关键数据
        final_content = result["final_chapter_output"]
        latest_review = result["latest_review"]
        revision_count = result.get("revision_count", 0)

        # 打印关键指标
        logger.info(f"   ✓ 章节ID: {result['chapter_id']}")
        logger.info(f"   ✓ 最终字数: {len(final_content)}")
        logger.info(f"   ✓ 质量评分: {latest_review.score}/100")
        logger.info(f"   ✓ 审查状态: {latest_review.status}")
        logger.info(f"   ✓ 修订次数: {revision_count}")

        # 打印内容预览
        content_preview = final_content[:200].replace('\n', ' ') if final_content else "无内容"
        logger.info(f"   ✓ 内容预览: {content_preview}...")

        # 打印审查反馈
        logger.info(f"   ✓ 审查反馈: {latest_review.general_feedback[:100]}...")
        if latest_review.actionable_suggestions:
            logger.info(f"   ✓ 修改建议数: {len(latest_review.actionable_suggestions)}")

        logger.info("\n" + "=" * 70)
        logger.success("🎉 所有测试通过！Chapter Writing Subgraph 运行正常")
        logger.info("=" * 70)

        return result

    except Exception as e:
        logger.error("\n" + "=" * 70)
        logger.error(f"❌ 测试失败: {str(e)}")
        logger.error("=" * 70)
        import traceback
        traceback.print_exc()
        raise


async def test_individual_nodes():
    """
    测试各个节点的独立功能（可选）
    """
    logger.info("\n" + "=" * 70)
    logger.info("🔍 节点独立测试（可选）")
    logger.info("=" * 70 + "\n")

    from app.agents.core.publisher.subgraphs.section_writer.nodes import (
        chapter_researcher,
        chapter_content_writer,
        review_draft,
        chapter_finalizer,
        revise_draft
    )
    from app.agents.schemas.review_schema import ReviewResult

    initial_state = create_test_state()

    # 测试 1: Researcher
    logger.info("1️⃣ 测试 chapter_researcher...")
    try:
        researcher_result = await chapter_researcher(initial_state)
        assert "research_data" in researcher_result or "research_queries" in researcher_result
        logger.success(f"   ✓ Researcher 测试通过")
    except Exception as e:
        logger.error(f"   ✗ Researcher 测试失败: {e}")

    # 测试 2: Writer（需要 researcher 的输出）
    logger.info("2️⃣ 测试 chapter_content_writer...")
    try:
        # 模拟 researcher 输出
        writer_state = {**initial_state, "research_data": "测试研究素材内容"}
        writer_result = await chapter_content_writer(writer_state)
        assert "draft" in writer_result or "draft_content" in writer_result
        logger.success(f"   ✓ Writer 测试通过")
    except Exception as e:
        logger.error(f"   ✗ Writer 测试失败: {e}")

    # 测试 3: Reviewer（需要 writer 的输出）
    logger.info("3️⃣ 测试 review_draft...")
    try:
        # 模拟 writer 输出
        reviewer_state = {
            **initial_state,
            "draft": "# 测试章节\n\n这是一段测试内容。" * 100,
            "revision_count": 0
        }
        reviewer_result = await review_draft(reviewer_state)
        assert "latest_review" in reviewer_result
        assert "revision_count" in reviewer_result
        logger.success(f"   ✓ Reviewer 测试通过 (评分: {reviewer_result['latest_review'].score})")
    except Exception as e:
        logger.error(f"   ✗ Reviewer 测试失败: {e}")

    # 测试 4: Reviser（需要 reviewer 的输出）
    logger.info("4️⃣ 测试 revise_draft...")
    try:
        # 模拟需要修订的状态
        reviser_state = {
            **initial_state,
            "draft": "# 测试章节\n\n这是一段需要修订的内容。",
            "revision_count": 1,
            "latest_review": ReviewResult(
                status="revise",
                score=70,
                general_feedback="内容需要补充更多细节",
                actionable_suggestions=[
                    "补充关于技术细节的描述",
                    "增加具体案例说明"
                ]
            )
        }
        reviser_result = await revise_draft(reviser_state)
        assert "draft" in reviser_result
        logger.success(f"   ✓ Reviser 测试通过 (修订后字数: {len(reviser_result['draft'])})")
    except Exception as e:
        logger.error(f"   ✗ Reviser 测试失败: {e}")

    # 测试 5: Finalizer（需要完整的状态）
    logger.info("5️⃣ 测试 chapter_finalizer...")
    try:
        # 模拟完整状态
        finalizer_state = {
            **initial_state,
            "draft": "# 测试章节\n\n这是最终内容。",
            "revision_count": 1,
            "latest_review": ReviewResult(
                status="pass",
                score=88,
                general_feedback="内容质量良好，符合要求",
                actionable_suggestions=[]
            )
        }
        finalizer_result = await chapter_finalizer(finalizer_state)
        assert "final_chapter_output" in finalizer_result
        logger.success("   ✓ Finalizer 测试通过")
    except Exception as e:
        logger.error(f"   ✗ Finalizer 测试失败: {e}")

    logger.info("\n" + "=" * 70)
    logger.info("节点独立测试完成")
    logger.info("=" * 70)


if __name__ == "__main__":
    # 运行完整流程测试
    result = asyncio.run(test_chapter_writing_subgraph())

    # 可选：运行节点独立测试
    # asyncio.run(test_individual_nodes())

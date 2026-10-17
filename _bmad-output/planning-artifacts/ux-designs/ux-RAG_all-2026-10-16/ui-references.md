# RAG UI 参考与本项目取舍

日期：2026-10-16。状态：已完成的参考输入；最终视觉由本轮用户委托下两位 Sally 的 DESIGN 交付决定确定。用户已说明暂无既定视觉偏好，允许找几个 RAG UI 参考。本文件通过官方文档与官方仓库截图研究公开界面，未登录产品、未运行其服务；截图所示版本不代表所有部署的当前外观。

## 参考对照

| 参考 | 实际观察或官方说明 | 对本项目的设计启发 | 本轮保留的边界 |
| --- | --- | --- | --- |
| [RAGFlow 会话界面](https://ragflow.io/docs/using_chat_conversations) | 官方截图是左侧会话、中央消息、底部输入；文档说明会话独立保存上下文 | 问答主区保持连续阅读，会话切换与输入分层；当前空间和本次目标范围需要持续可见 | 本项目按非流式完整返回设计；不照搬语音、联网搜索、Agent 等入口 |
| [MaxKB 官方 UI 展示](https://github.com/1Panel-dev/MaxKB/blob/v2/README_CN.md#ui-展示) | 已查看 Demo3 的目录与内容并排，以及 Demo4 的会话／答案／知识来源三栏 | 来源查看器靠近答案；资料校核以定位目录和原件／提取对照为中心 | 分数只表示检索信号，不能当事实置信度；本项目引用按不可变版本与授权解析 |
| [Dify 检索测试](https://docs.dify.ai/en/cloud/use-dify/knowledge/test-retrieval)与[知识流水线界面](https://www.dify.ai/rag) | 文档将检索测试放在知识库独立入口，测试参数临时生效；官方图展示独立处理阶段与操作区 | 管理侧将“处理结果与来源校核”和业务问答分开；可区分所选配置与正在生效的版本 | 不引入可视工作流画布、节点编排或额外测试产品；本轮不据此扩充既定范围 |

以上“设计启发”是 Sally 根据公开证据的推导，不是这些产品替本项目证明权限、质量或恢复能力。既有 WeKnora／MaxKB 技术参考继续保留；本轮补充 RAGFlow 和 Dify 作为界面观察样本，不重新选择技术栈。

## 看到的界面

### RAGFlow：会话与输入的稳定位置

![RAGFlow 官方会话界面，左侧会话列表、中央内容及底部输入区](https://raw.githubusercontent.com/infiniflow/ragflow-docs/main/images/create_and_manage_sessions.jpg)

来源：[官方会话文档](https://ragflow.io/docs/using_chat_conversations)。图中红色箭头为官方教学标注。

### MaxKB：答案旁展开知识来源

![MaxKB 官方问答截图，左侧会话、中央答案、右侧知识来源](https://github.com/user-attachments/assets/e6268996-a46d-4e58-9f30-31139df78ad2)

来源：[官方 README UI 展示](https://github.com/1Panel-dev/MaxKB/blob/v2/README_CN.md#ui-展示)。右侧来源列表的层次可参考，图中的相似度数值不能直接转换成本项目“回答正确率”。

### MaxKB：目录与资料内容并排

![MaxKB 官方资料截图，左侧段落目录与右侧内容](https://github.com/user-attachments/assets/c927474a-9a23-4830-822f-5db26025c9b2)

来源：[官方 README UI 展示](https://github.com/1Panel-dev/MaxKB/blob/v2/README_CN.md#ui-展示)。本项目进一步区分原件与提取内容，避免将解析片段呈现成原件。

### Dify：处理阶段独立可见

![Dify 官方知识流水线界面，仅供阶段层次与操作分区参考](https://www.dify.ai/_astro/observable.DRW0Q7D-_2pc7Q5.png)

来源：[官方 Knowledge Pipeline 页面](https://www.dify.ai/rag)。这里只借鉴阶段与操作区的分离；流水线画布不进入本项目 IA。

## 本轮交付组合

**[Sally 交付决定]** 用既定 Element Plus 构建业务工作台：左侧稳定导航，顶部持续显示当前空间，中央完成问答／对比／资料任务；来源按需在右侧展开。问答借鉴 RAGFlow 的会话连续性，证据回看借鉴 MaxKB 的近邻来源，资料处理借鉴 Dify 的阶段区分。多文档核验使用本项目已定四态矩阵；三个参考均不替代本项目的比较语义。

**[本轮委托决定]** 采用桌面优先的响应式 Web、浅色、系统字体与深蓝操作色；精确断点、尺寸、状态色与其他增量按 DESIGN。两位 Sally 已在用户要求的交付深度内闭合，不再等实施者猜测或选风格；不冒称用户逐项确认，也不增加原生移动端或主题切换功能。

设计推导落入[视觉契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/DESIGN.md)与[体验契约](/E:/aaa-project/rag/_bmad-output/planning-artifacts/ux-designs/ux-RAG_all-2026-10-16/EXPERIENCE.md)。两份契约是后续交互与视觉的主文档；参考截图是解释材料。

## 未借鉴的功能与原因

本轮没有引入参考产品的 Agent、联网搜索、语音、工作流、自动同步、文段在线编辑、知识图谱、公开分享或额外结果导出。这些观察不构成上游范围变更；本项目继续以现行 PRD 与实施契约为准。

# 技术证据摘要，2026-10-15

方法：本轮官方只读检索和固定SHA文本重读；一个研究者、无fanout。项目PRD/契约仅作需求框定。

| claim | source | publisher | pub_date | accessed | confidence | class |
|---|---|---|---|---|---|---|
| 精准云API的上传链接24h，PUT完成自动触发解析；data_id说明不构成幂等承诺 | [MinerU精准API](https://mineru.net/doc/docs/) | MinerU | 未标 | 2026-10-15 | 中、unverified | api-protocol |
| 行锁和SKIP LOCKED提供DB内部队列/竞争工具 | [SELECT](https://www.postgresql.org/docs/18/sql-select.html#SQL-FOR-UPDATE-SHARE)、[锁](https://www.postgresql.org/docs/18/explicit-locking.html#LOCKING-ROWS) | PostgreSQL | 18文档，未标 | 2026-10-15 | 中、unverified | patterns |
| Popen超时不自动终止子进程，需明确终止及等待 | [subprocess](https://docs.python.org/3.12/library/subprocess.html#subprocess.Popen.communicate) | Python | 更新2026-10-01 | 2026-10-15 | 中、unverified | patterns |
| flock为协作锁且关联全部相关FD，不能模拟强制权限隔离；unlink不证明空间已释放 | [flock](https://man7.org/linux/man-pages/man2/flock.2.html)、[unlink](https://man7.org/linux/man-pages/man2/unlink.2.html) | Linux man-pages | flock页2026-02-08；unlink未摘日期 | 2026-10-15 | 中、unverified | patterns |
| WeKnora已读上传是先文件后DB再任务；任务有入口代次与删除检查，删除先标deleting；span存在但不证明硬计费门 | 固定a37a1bc：见[evidence](/E:/aaa-project/rag/_bmad-output/planning-artifacts/prds/prd-RAG_all-2026-10-15/ir-review-2026-10-15-round2/mary-r2-m1/evidence.md:24)与manifest；create165–245、local48–96/137–154、process3651–3715、delete483–630、span422–490 | Tencent/WeKnora | 固定提交，日期未查 | 2026-10-15 | 中、unverified | fixed-source |
| MaxKB所读原件路径压缩保存PG large object；QueueOnce是document_id去重；模型调用之后计算token写context，流式估计失败存在设0分支 | 固定0fa9a0d：document1255–1284/818–877、knowledge367–434、embedding61–92、base_chat_step151–162/696/725–753；详见evidence及manifest | 1Panel-dev/MaxKB | 固定提交，日期未查 | 2026-10-15 | 中、unverified | fixed-source |

未找到/未证明：MinerU按data_id找回或去重、取消/删除协议；全仓所有外发硬门；全局物理停写证明；千问最终型号的SDK重试和真实usage。S0/P0需要执行验证，本轮不补猜测。

停止：已覆盖本决策关键边界，继续扩大源码范围不会替代本机回收实测，按授权focused run结束TR。静态反例只能证明原稿机制描述不足，不能证明两参考项目运行故障。

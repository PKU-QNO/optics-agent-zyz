# 分文档 05：COMSOL 交叉验证路径

> [⬆ 返回主文档](PROJECT-SYNC-2026-08-11.md)

## 总览

```
官方 MPH (B16) → Java builder (B17) → Magnus batch_mph/Java → Fig.3 G4 truth
```

## 路径状态

| 步骤 | 状态 | 阻塞 | 证据 |
|------|------|------|------|
| 官方 6.3 rib MPH 下载校验 | ✅ | — | SHA 74468981，COMSOL 6.3.0.71，ModeAnalysis study |
| 本地嵌入解看图 | ✅ | — | 10 个 neff（最高 3.188 vs core 3.48），场型非零合理 |
| Java builder（双金盘频域散射） | ✅ 写出 + 编译 PASS | 曾缺 libpskernel.so | 310 行；Magnus comsol compile 返回 0 |
| libpskernel.so（Parasolid 内核） | ✅ 已找到 + scp 集群 | — | COMSOL 6.2 官方 ISO 提取，87MB，SHA 271a36bd → /data/public/.../libs/ |
| Java 3-D（ED/MD/EQ/MQ） | ✅ 9 点谱 PASS | 曾缺库/mesh/材料/背景场（B24-B29 逐层解决） | ED 主导 + MD/EQ x=0.36 磁共振 |
| Fig.3 正式晋级 | 📋 | 缺网格收敛/远场闭合/vector trace/human gate | PARTIAL_PASS（B31 裁决） |
| SSH 直放挂载路径 | ✅ 打通 | — | 探针 61e1efe0 PASS；/data/public 被 job 读取 |
| Magnus batch_mph | ⚠️ ENOSPC | 临时盘声明不足（SLURM 需显式） | solver 50% 扫描 No space left |
| Fig.3 G4 truth | ❌ 未完成 | ENOSPC + 缺库 | B22 save→launch 重跑中 |

## 提交方式（三种，重要区分）
1. **空白任务提交** ❌——CLI 忽略资源参数，记录成默认 A2 未启动（B20 探针实证）
2. **提交 blueprint** = 保存定义（非跑 job）
3. **通过 blueprint 提交 job** ✅ = save → wait 2s → launch（args 显式资源）→ monitor
   - 参考：`C:/Users/27370/Desktop/project/PHY-LLM-Basic-Algorithm/train_zyz/submit_sft.py`
   - 资源显式：gpu_count/gpu_type/cpu_count/memory_demand/ephemeral_storage/priority

## 三家调研共识（IND1/2/3，防幻觉）
- 莫子涵 112 job 全 Python 量子光学（非 COMSOL）；她的 FileSecret receive 在 prbench 镜像可用
- 但 comsol-runtime 镜像 baked 旧 SDK 与平台新 SDK 冲突 → magnus receive 不可用（aa5b712 对照实证）
- 平台上 32 个成功 COMSOL job 全走挂载路径（/data/public/... 绝对路径输入 + license 挂载）

## 关键结论

- B16：官方 MPH 是可靠 oracle（本地验证），但 Magnus 重跑阻塞于 blueprint 配置
- B17：Java builder 物理设置已全部明确（双金盘 + JC 色散 + SBC/PML + 场导出 + 多极矩节点），只差编译环境
- B19：B16（rib 导波）与 B7（双盘散射）几何/物理不同，**不能数值对齐**，只能方法学印证；FIG3-G5 INACTIVE

## G4 阻塞的确切缺口（B16/B17 结论）

1. **本地**：装 COMSOL 6.3 Java API（含 comsol.jar）
2. **Magnus**：管理员更新 live blueprint，把 case_bundle_secret 注册为 FileSecret 并暴露 hash/format 参数；或把 MPH/Java 通过已验证持久 /home/magnus/data/... staging 放置

## 下一步（任一激活 G4）

- A. 本地装 COMSOL Java API
- B. 管理员更新 Magnus blueprint
- C. 搁置（surrogate_fallback 收尾）

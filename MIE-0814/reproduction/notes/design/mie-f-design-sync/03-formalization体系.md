# 分文档 03：Formalization spec 体系

> [⬆ 返回主文档](PROJECT-SYNC-2026-08-11.md)

## 总览

```
formalization/*.yaml (4 份) → SEPR-9 语义 → code 唯一物理输入源
```

SEPR-9 = method/observable/parameters/physics/path/numerics/validation/gates/result_class 九字段语义集合（各 spec 因历史版本有 9/12/13 顶层区段差异，Fig.3 是 exact-9 校验，见 `notes/sepr-schema-contract.md`）。

## 四份 spec

| spec | 顶层 | 状态 | 关键内容 |
|------|------|------|----------|
| alaee2018-fig1.yaml | 13 | ✅ yaml OK | 复矩口径（B13）；s075_gate ED>100% MD>100% |
| alaee2018-fig2.yaml | 12 | ✅ yaml OK | ε_r=6.25 + 金球 JC；partial_physical_match |
| alaee2018-fig3.yaml | 9 | ✅ APPROVED_AS_PATH_CANDIDATE | 四通道 Table1/2 + FIG3-G0~G6 |
| grahn.yaml | 12 | ✅ yaml OK + validator PASS | v4；M2 四对象/双路径/逐 m 目标 |

## Fig.3 spec 演进（重点）

```
A4 草案 (out/) → B11 修订稿 (20KB) → B12 审查 (批2调5拒1+Eq1风险) → 晋升 (APPROVED_AS_PATH_CANDIDATE)
```

- 主 observable 纠偏：Fig.3 = 四通道 Table1/2 散射贡献 + 相对误差（非 Fano 谱）
- Fano 降级：默认关闭、默认不 gate、不提升主结果等级
- Mie 上限：surrogate_fallback（非双盘真解）
- COMSOL：频域散射（非 mode analysis），neff 不适用
- FIG3-G0~G6 专属 gate：G0 scope / G1 inputs / G2 equations / G3 surrogate / G4 COMSOL truth / G5 crosspath / G6 paper
- 当前：G0/G2/G3 可批，G1/G4/G5/G6 blocked（等 COMSOL）

## 一致性

- 跨 spec 共同口径：x_mie=π(2a/λ)、ED/MD/EQ/MQ 映射、host=air、ε_r=6.25 无冲突
- B14 审查：Fig.1 复矩口径与实现/测试/报告一致；C 分项只作诊断
- B15 后：四 spec yaml.safe_load 全 OK

# SEPR spec schema 合同说明

## 结论

本项目中的“SEPR-9”是九类语义集合，不是要求所有历史 spec 都具有完全相同的九个顶层键。四份 spec 的顶层区段数量因演进历史不同：Fig.1 为 13、Fig.2 为 12、Grahn 为 12、Fig.3 为 9。区段数量差异本身不改变已冻结的物理参数、公式口径或 gate 状态。

## 两种校验模式

- `formalization/alaee2018-fig3.yaml` 使用 exact-9 合同；其 `validation.schema.require_exact_top_level_fields` 明确列出 `method`、`observable`、`parameters`、`physics`、`path`、`numerics`、`validation`、`gates`、`result_class`，不得增删顶层键。
- `formalization/alaee2018-fig1.yaml`、`formalization/alaee2018-fig2.yaml` 与 `formalization/grahn.yaml` 使用语义 SEPR-9 合同。历史结构把同一语义拆成 `meta`、`geometry`、`materials`、`equations`、`boundary_conditions`、`sources`、`solver`、`observables`、`verification`、`assumptions`、`missing_fields`、`provenance` 等区段；校验应检查语义覆盖与各自 schema，不应要求 exact-9 顶层键相等。

## 维护规则

1. 不为追求顶层键数量一致而重排现有 spec；这种结构迁移会无谓扰动冻结内容与历史收据。
2. 新增校验须先声明采用 `exact-9` 还是“语义 SEPR-9 + spec 专属 schema”。
3. result class、gate 状态和数值参数由各 spec 的明确字段及收据决定，不能从顶层区段数量推断。

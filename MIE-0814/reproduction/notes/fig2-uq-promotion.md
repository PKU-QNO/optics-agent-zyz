# Fig.2 Layer3 UQ 晋级轮

## 执行结论

恢复执行时发现原 B3 指定的 A5 预注册之后，`A5-v2/preregister/SPEC.md` 已冻结并明确
supersede 旧试运行的统计语义。故下表保留旧 4000 点、401×401 平移、$0.5Mh^2$ 数值作为
`diagnostic_only`，正式 `layer3_uq_status` 按最新 spec fail-closed：全部 `UNRESOLVED`。

| panel | channel | legacy RMSE interval | state | legacy p95 interval | state | peak-x interval | state | legacy composite | latest theorem RMSE proxy | latest theorem p95 proxy | pre-override diagnostic | latest layer3 UQ |
|---|---|---:|---|---:|---|---:|---|---|---:|---:|---|---|
| a | ED | [0.0058829861, 0.028228128] | UNRESOLVED | [0.011186587, 0.056178417] | UNRESOLVED | [0, 0.0077045567] | PASS | UNRESOLVED | [0.0063463295, 0.018428479] | [0.011822274, 0.046438279] | PASS | UNRESOLVED |
| a | MD | [0.0052408436, 0.02790725] | UNRESOLVED | [0.010703016, 0.060395272] | UNRESOLVED | [0, 0.0034612227] | PASS | UNRESOLVED | [0.0062060355, 0.020578775] | [0.012170842, 0.042788355] | UNRESOLVED | UNRESOLVED |
| a | EQ | [0.0073183604, 0.026631463] | UNRESOLVED | [0.014774578, 0.061105055] | UNRESOLVED | [0, 0.001618278] | PASS | UNRESOLVED | [0.0081221602, 0.021214302] | [0.016129144, 0.046066124] | UNRESOLVED | UNRESOLVED |
| a | MQ | [0.0099772835, 0.053615108] | UNRESOLVED | [0.016635575, 0.11904346] | UNRESOLVED | [0, 0.0015662826] | PASS | UNRESOLVED | [0.012396219, 0.041005741] | [0.025462328, 0.087346796] | UNRESOLVED | UNRESOLVED |
| b | ED | [0.0037200562, 0.014903528] | PASS | [0.0079683946, 0.024253927] | PASS | [0, 0.0060275284] | PASS | PASS | [0.0046690866, 0.013903405] | [0.0091813776, 0.023168922] | PASS | UNRESOLVED |
| b | MD | [0.0041256455, 0.036873706] | UNRESOLVED | [0.0083145497, 0.036607437] | PASS | [0, 0.024388457] | UNRESOLVED | UNRESOLVED | [0.0042737098, 0.092007909] | [0.0081916747, 0.37944234] | UNRESOLVED | UNRESOLVED |
| b | EQ | [0.0037653302, 0.02857776] | UNRESOLVED | [0.0083450853, 0.028297772] | PASS | [0, 0.010798568] | UNRESOLVED | UNRESOLVED | [0.0049722018, 0.032561171] | [0.010416209, 0.048642918] | UNRESOLVED | UNRESOLVED |
| b | MQ | [0.0040840714, 0.010953763] | PASS | [0.0078359814, 0.018753721] | PASS | [0, 0.005366831] | PASS | PASS | [0.0043361032, 0.010855232] | [0.0081113352, 0.018989494] | PASS | UNRESOLVED |

历史 strict 门槛 0.02 / 0.05 / 0.01 仍原样保留，但 A5-v2 禁止把它们继承为 dense UQ
门槛。当前轴项仍标为 sensitivity proxy，插值 coverage 未被校准为未知论文曲线 coverage，
physics receipt 也没有独立 uncertainty bound；因此 `uq_model_validity=false`。
最新 theorem proxy 区间已逐通道列出，但其阈值来源为 `none_by_A5_v2_spec`，不能裁决。

## 晋级裁决

- method gate: `PASS`
- required-domain coverage: `MATERIAL_DOMAIN_LIMITED`
- layer3 UQ: `UNRESOLVED`
- promotion: `DENIED`
- result_class: `partial_physical_match`

金球 panel-b 的 JC 域外缺口仍为独立 blocker；UQ 不得隐藏该缺口。既有第 2 轮 strict
receipt 未被改写。

## 复现

```powershell
python "code/run_fig2_uq.py"
$env:PYTHONPATH = (Resolve-Path 'codex-prompts/out/A3-file-secret-hardening/optics_agent/comsol/runtime').Path
python -m pytest -q
```

逐点输入、曲率、相邻间距和两种插值带见 `data/fig2_uq_pointwise.csv`；212/1000/4000/
16000/equal-segment 五种权重敏感性见 `data/fig2_uq_weighting_sensitivity.csv`；逐通道平移
网格极值参数与 input SHA-256 见 `data/fig2_uq_summary.json`。

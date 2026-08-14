---
name: comsol-scattering
description: COMSOL Multiphysics 电磁散射建模（Java API）——频域有限元 `ElectromagneticWavesFrequencyDomain`（ewfd）与边界元 `ElectromagneticWavesBoundaryElements`（embe），覆盖散射场公式、SBC/PML、色散材料（Johnson-Christy 插值）、多极矩（ED/MD/EQ/MQ）体积分后处理、网格收敛 + Richardson 外推、远场导出（FarFieldCalculation）。Use when 要写或调试一个 COMSOL Java 散射模型（纳米光子/等离激元结构、Mie 球、双金盘等），或要选数值方法（FEM vs BEM vs FDTD vs 解析 Mie）、要查 FEM/BEM 接口 API 细节、要排障（网格 0 单元/远场全 0/文件写被沙箱拦/OOM）。
---

# COMSOL Scattering — 电磁散射建模（Java API）

> 从 zotero mie-f 双金盘散射（Fig.3）FEM 900G + BEM 128G 两套求解器落地沉淀。
> 完整 BEM 工作模板见 `assets/Alaee2018Fig3ComsolScatteringBEM.java`（338 行，可直接复制改）。

## 1. 方法选型（先判用哪个）

| 结构 | 首选 | 理由 |
|------|------|------|
| 球体/规则形状 | **Mie 解析解**（Python 级数求和） | 有解析解永不碰数值，秒级 |
| 非球形、只要截面谱 | **FDTD**（Lumerical/Meep） | 内存线性几十 GB，时域→FFT 一次出全谱 |
| 非球形、要精确多极分解 | **BEM**（scuff-em / COMSOL embe） | 只离散表面，DOF 少，天然适合金属 |
| 通用/论文对齐 COMSOL | **FEM 频域**（ewfd）+ 直接求解器 | 现成工具链，但内存 O(DOF^1.5) 重 |

**COMSOL 内部 FEM vs BEM**：FEM 离散整个体积（四面体 FreeTet），内存随体积膨胀；BEM 只离散表面（三角形 FreeTri），内存省一个量级（同一双金盘：FEM 900G vs BEM 128G）。

## 2. FEM 频域建模（ewfd）关键设置

- **散射场公式**：`SolveFor=scatteredField` + 背景场 `Eb = E0*exp(-i*k0*z)`（+z 平面波，x 偏振）。解析写入入射场，只数值解散射场（集中在散射体附近、向外衰减）。
- **外边界**：SBC（散射边界条件，一阶辐射条件 `n×∇×E_scat + ik E_scat ≈ 0`，近似 Sommerfeld）或 PML（完美匹配层，理论零反射但加人工介质）。外域够大时 SBC 够用（验证 3000→4000 nm <1%）。
- **多极矩后处理**：COMSOL 只解出场 E，ED/MD/EQ/MQ 用 Alaee 2018 Table 2 精确公式对场做**体积积分**（`p=∫P dV`，`m=(iω/2)∫r×P dV`，四极含高阶矩）。精确多极矩对表面场梯度敏感 → MD/EQ 网格收敛慢的根因。
- **网格收敛 h-refinement**：mesh scale 1.0→0.7→0.5→0.3 缩小四面体 h，误差 ∝ C·h^p。ED/MQ 易收敛（<0.3%）；MD/EQ 在磁共振峰表面场奇异 → p≈1.3 一阶收敛，h 减半误差只减 40%。**与其无脑加密到 0.2（2TB 内存），不如 p-refinement（高阶基函数）**。
- **直接 vs 迭代**：频域默认直接求解器（MUMPS/PARDISO 稀疏 LU），内存 O(DOF^1.5)。0.5 网格 14.7M DOF→99GB，0.3 网格 68.2M DOF→900GB。迭代（GMRES）内存 O(DOF) 线性但高频电磁收敛差。

## 3. BEM 建模（embe）关键设置

- 接口：`ElectromagneticWavesBoundaryElements`（tag `embe`），**无空气盒/SBC/PML**——无限域由 COMSOL 的 infinite void 表示，只有散射体表面被三角化。
- **只支持两类散射体**：金属 PEC 与**常介电常数**介质。**色散金属材料域（如 Johnson-Christy 金）BEM 不支持**（WaveEquationElectric 需常数材料参数）——色散金属域会让表面不被选中 → surface_elements=0。PEC 近似是 IBC（有限表面阻抗）的 Zs→0 极限。
- **远场**：`embe.relEx` 是 FEM 变量，BEM 远场必须建 `FarFieldCalculation`（feature `ffc1`，维度 2），`FarName=Efar` 生成方向函数 `Efarx(dx,dy,dz)/Efary/Efarz`（**未加前缀**，直接 `Efarx(...)` 调，不是 `embe.Efarx`）。用它做 Stratton-Chu 远场算散射截面。
- **PEC 近似代价**：理想导体丢失金的磁共振 → MD/EQ 被抑制（ED/MQ 同数量级）。要恢复磁响应需 IBC 加有限表面阻抗损耗（后续工作）。

## 4. Java API 关键模式

见 `assets/Alaee2018Fig3ComsolScatteringBEM.java`。核心骨架：

```java
Model model = ModelUtil.create("name");
model.component().create("comp1");
// 参数
model.param().set("a", "250[nm]"); ... model.param().set("lambda0", "2*a/x_alaee");
// 色散材料（Interpolation，禁外推）
model.func().create("nAu", "Interpolation"); model.func("nAu").set("table", toTable(JC_NK,1));
model.func("nAu").set("interp","linear"); model.func("nAu").set("extrap","none"); // argunit nm
model.component("comp1").variable().create("matvars");
model.component("comp1").variable("matvars").set("epsAu", "(nAu(lambda0)+i*kAu(lambda0))^2");
// 几何（Cylinder，selresultshow=bnd）
model.component("comp1").geom().create("geom1", 3); ... .feature("disk").set("selresultshow","bnd");
// 物理（BEM：先清默认选择再 allVoids；散射场 + 远场）
model.component("comp1").physics().create("embe","ElectromagneticWavesBoundaryElements","geom1");
model.physics("embe").selection().set(new int[]{});        // 清默认域选择
model.physics("embe").selection().allVoids();
model.physics("embe").prop("BackgroundField").set("SolveFor","scatteredField");
model.physics("embe").prop("BackgroundField").set("Eb", new String[]{"E0*exp(-i*k0*z)","0","0"});
model.physics("embe").create("ffc1","FarFieldCalculation",2);
model.physics("embe").feature("ffc1").selection().geom("geom1",2); ... .set("FarName","Efar");
// 表面网格（FreeTri 必须显式 selection 维度 2）
model.component("comp1").mesh().create("mesh1","geom1");
model.component("comp1").mesh("mesh1").feature().create("ftri1","FreeTri");
model.component("comp1").mesh("mesh1").feature("ftri1").selection().geom("geom1",2);
model.component("comp1").mesh("mesh1").feature("ftri1").selection().all();
// 求解 + 导出
model.study().create("std1"); model.study("std1").create("freq","Frequency"); ... set("plist","freq0");
model.sol().create("sol1"); model.sol("sol1").createAutoSequence("std1"); model.sol("sol1").runAll();
```

## 5. 关键坑（都踩过）

1. **`surface_elements=0` 是假警报**：`mesh.getNumElem()` 对 BEM 边界网格返回 0，实际 9648 单元正常。真根因是色散金属材料域 BEM 不支持 → 删 WaveEquationElectric + matGold → 表面回落到 PEC 边界才被网格化。
2. **FreeTri 在 3-D 选边界**：默认选择空，必须 `.selection().geom("geom1", 2)` 再 `.all()`，否则材料域圆柱不网格化。
3. **Cylinder 默认选域**：`.set("selresultshow","bnd")` 让它选中边界而非域。
4. **写文件被安全沙箱拦**：`PrintWriter` 写 CSV 失败 → `comsol.prefs` 设 `security.external.filepermission=full`。
5. **HOME 只读**：集群 `$HOME=/magnus` 只读 → `export HOME=/home/magnus`。
6. **远场全 0**：BEM 不能读 `embe.relEx`，必须走 `FarFieldCalculation` + `Efarx()` 方向函数。
7. **色散插值禁外推**：`extrap=none`，材料数据范围外会报错（Johnson-Christy 支持 1935 nm 内）。
8. **OOM**：BEM 稠密矩阵 95GB > 32G → 需 128G；FEM 0.3 网格需 900G。先估算 DOF 再申请资源。

## 6. references / assets

- `assets/Alaee2018Fig3ComsolScatteringBEM.java` — 完整可跑 BEM 模板（双金盘，含远场高斯-勒让德求积导出）
- `assets/Alaee2018Fig3ComsolScattering.java` — 完整 FEM 频域模板（ewfd，含空气盒/SBC/色散金）
- `references/fem-bem-selection.md` — FEM/BEM 方法选型 + 资源画像 + 网格收敛细节

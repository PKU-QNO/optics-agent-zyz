# 论文阅读与参数提取

## 目标
阅读指定论文 PDF，系统提取复现所需全部信息。

## 输入
- 论文 PDF 路径（由用户或工作流引擎指定）

## 输出
- `reproduction/private/<case_name>/params.yaml`
- `reproduction/private/<case_name>/paper_notes.md`

## 提取清单

### 1. 论文元数据
- 标题、作者、DOI、期刊、发表年份

### 2. 物理模型
- 控制方程（写出具体形式）
- 边界条件（PML/周期性/SC/PMC）
- 初始条件
- 维度（1D/2D/3D）、对称性

### 3. 几何结构
- 层结构、厚度、周期
- 材料分布图
- 关键尺寸参数

### 4. 材料参数
- 折射率 (n, k)
- 介电常数 (ε_r, ε_i)
- 磁导率 (μ_r)
- 色散模型（Drude/Lorentz/Sellmeier）
- 波长/频率范围

### 5. 数值方法
- FEM 参数（阶数、单元类型）
- 网格类型（自由三角形/四边形/映射）
- 求解器类型（特征值/频域/瞬态）
- 特征值移位（shift）
- 搜索范围

### 6. 目标输出
- 图号、坐标轴标签
- 预期物理现象
- 对比数据点

## 格式约定
- `params.yaml`：顶层键为参数类别，使用 snake_case
- `paper_notes.md`：包含公式（LaTeX）、图表引用、关键段落摘录

## 参考 skill
- `optics-paper-reproduction`：标准答案模板、missing-info 分析

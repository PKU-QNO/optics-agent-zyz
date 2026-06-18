# 数值程序生成

## 目标
生成 COMSOL Java 代码，配置 Magnus 提交，实现数值仿真。

## 输入
- `reproduction/private/<case_name>/params.yaml`
- `reproduction/private/<case_name>/theory_derivation.md`

## 输出
- `reproduction/private/<case_name>/model.java`
- `reproduction/private/<case_name>/magnus_job.yaml`

## 步骤

### 1. 蓝图检查
- 查找 `.magnus/.blueprints/` 中匹配的蓝图
- 如有：调用蓝图生成 Java 框架
- 如无：参考 `comsol-java-api` skill 手动编写

### 2. Java 代码必须包含
- `public static Model run()` 入口
- 无 inner class / anonymous class
- 无 `System.getenv`, 直接 Java 文件 IO
- 返回 `Model` 对象

### 3. 几何构建
- 参数化所有几何尺寸
- 从 params.yaml 读取参数

### 4. 材料定义
- 从 params.yaml 读取折射率/介电常数
- 使用 `model.material().create()` API

### 5. 物理场设置
- 根据论文选择模块（Wave Optics / RF）
- 设置端口/激励/边界条件

### 6. 网格
- 基于波长计算最大单元尺寸
- 建议：每波长至少 5-10 个单元

### 7. 研究设置
- 特征值：设置搜索范围和 shift
- 频域：设置频率范围和步长

### 8. Magnus 配置
- gpu_type=cpu, gpu_count=0
- cpu_count=8, memory_demand=32G
- LICENSE 挂载路径验证

## 参考 skill
- `comsol-java-api`：Java API 语法、模板
- `optics-comsol-batch`：批处理参数
- `optics-magnus-platform`：作业配置

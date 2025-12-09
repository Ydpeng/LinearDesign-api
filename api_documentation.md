# LinearDesign API 接口文档

## 接口基本信息
- **URL**: `/tools/linearDesign`
- **方法**: POST
- **Content-Type**: `multipart/form-data`
- **描述**: 将蛋白质序列转换为优化的mRNA序列

## 请求参数

### 表单参数 (Form Data)

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `sequence` | string | 可选 | null | 单个蛋白质序列字符串。与`file`参数二选一 |
| `file` | file | 可选 | null | FASTA格式的蛋白质序列文件。与`sequence`参数二选一 |
| `lambda_param` | float | 否 | 0.0 | 平衡MFE和CAI的超参数，取值范围建议0.0-10.0 |
| `codon_usage` | file | 否 | null | 自定义密码子使用频率表文件（CSV格式） |

### 参数约束
1. **sequence** 和 **file** 必须二选一，不能同时提供
2. **sequence** 格式: 蛋白质序列字符串，如 "MNDTEAI"
3. **file** 格式: FASTA格式文件，支持多序列
4. **codon_usage** 格式: CSV文件，参考现有密码子表格式

## 响应格式

### 成功响应 (200 OK)
```json
{
  "status": "success",
  "lambda_parameter": 0.0,
  "codon_usage_table": "codon_usage_freq_table_human.csv",
  "results": [
    {
      "sequence_name": "test_sequence_1",
      "mrna_sequence": "AUGAACGAUACGGAGGCGAUC",
      "mrna_structure": "......(((.((....)))))",
      "folding_free_energy": -1.1,
      "cai": 0.695
    }
  ]
}
```

### 响应字段说明

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `status` | string | 请求状态，"success" 或 "error" |
| `lambda_parameter` | float | 使用的lambda参数值 |
| `codon_usage_table` | string | 使用的密码子表文件名 |
| `results` | array | 结果数组，每个元素为一个序列的结果 |

#### results 数组中的对象结构

| 字段名 | 类型 | 描述 |
|--------|------|------|
| `sequence_name` | string | 序列名称（来自FASTA文件） |
| `mrna_sequence` | string | 优化的mRNA序列 |
| `mrna_structure` | string | mRNA的二级结构表示 |
| `folding_free_energy` | float | 折叠自由能（kcal/mol） |
| `cai` | float | 密码子适应指数 |

## 错误响应

### 400 Bad Request
```json
{
  "error": "必须提供sequence参数或file参数"
}
```

或
```json
{
  "error": "只能提供sequence参数或file参数中的一个"
}
```

### 500 Internal Server Error
```json
{
  "error": "LinearDesign执行失败",
  "stderr": "具体的错误信息"
}
```

或
```json
{
  "error": "处理请求时发生错误: 错误详情"
}
```

## 使用示例

### 示例1: 单个序列请求
```bash
curl -X POST http://localhost:8000/tools/linearDesign \
  -F "sequence=MNDTEAI" \
  -F "lambda_param=0.0"
```

### 示例2: 文件上传请求
```bash
curl -X POST http://localhost:8000/tools/linearDesign \
  -F "file=@test.fasta" \
  -F "lambda_param=3.0"
```

### 示例3: 自定义密码子表
```bash
curl -X POST http://localhost:8000/tools/linearDesign \
  -F "sequence=MNDTEAI" \
  -F "lambda_param=0.3" \
  -F "codon_usage=@custom_codon_table.csv"
```

## 输入文件格式

### FASTA文件格式
```fasta
>sequence_name_1
PROTEINSEQUENCE1
>sequence_name_2  
PROTEINSEQUENCE2
```

### 密码子表文件格式
参考 `codon_usage_freq_table_human.csv`:
```csv
Codon,AA,Frequency
GCA,A,0.23
GCC,A,0.40
GCG,A,0.11
GCT,A,0.26
...
```

## 注意事项

1. **参数互斥**: `sequence` 和 `file` 参数不能同时使用
2. **文件编码**: 所有文本文件应使用 UTF-8 编码
3. **性能考虑**: 大量序列处理可能需要较长时间
4. **内存使用**: 大文件处理时注意内存消耗
5. **默认配置**: 不提供 `codon_usage` 时使用人类密码子表

## 版本信息
- API版本: 1.0.0
- LinearDesign版本: 基于原始C++代码集成
- 最后更新: 2025-12-08
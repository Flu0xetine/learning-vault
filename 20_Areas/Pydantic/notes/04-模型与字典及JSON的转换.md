---
area: Pydantic
type: note
created: 2026-09-18
updated: 2026-09-19
related_daily:
  - "[[2026-09-19]]"
  - "[[2026-09-18]]"
---

# 04-模型与字典及JSON的转换

## 本篇概览

本篇用 `model_validate()`、`model_validate_json()` 将字典或 JSON 文本校验为模型实例，用 `model_dump()`、`model_dump_json()` 将实例导出为字典或 JSON 字符串。另以 `model_json_schema()` 区分类的结构规则与实例中的真实数据。操作前先确认对象类型：模型实例用属性访问，字典用键访问，JSON 文本需要解析；导出的是处理后的数据，不是原始输入的还原。

## 先判断对象是什么，再选择方法

```python
from pydantic import BaseModel

class SearchFilter(BaseModel):
    start_year: int
    end_year: int

data = {"start_year": "2020", "end_year": "2025"}     # dict
text = '{"start_year": "2020", "end_year": "2025"}'   # str
filters = SearchFilter.model_validate(data)             # SearchFilter 实例
```

这个例子只演示类型转换；若要检查年份顺序，使用 [[03-字段校验器与模型校验器]] 中带 `model_validator` 的定义。调用下表中的校验方法同样会执行模型上已注册的校验器。

| 方向 | 方法 | 返回类型 |
|---|---|---|
| 字典 → 模型 | `SearchFilter.model_validate(data)` | `SearchFilter` 实例 |
| JSON 字符串 → 模型 | `SearchFilter.model_validate_json(text)` | `SearchFilter` 实例 |
| 模型 → 字典 | `filters.model_dump()` | `dict` |
| 模型 → JSON 字符串 | `filters.model_dump_json()` | `str` |

输入校验在**模型类**上调用；导出已有数据在**模型实例**上调用。`SearchFilter(**data)` 在本例中也能校验字典展开后的参数。

## 学习中混淆过的访问方式

本轮回答曾判断：导出字典中的年份是整数，而且 `result.start_year` 可以使用。前半句正确，后半句已经纠正。

```python
filters = SearchFilter.model_validate(data)
result = filters.model_dump()

assert filters.start_year == 2020       # 模型实例使用属性
assert result["start_year"] == 2020    # 字典使用键
assert isinstance(result["start_year"], int)
# result.start_year  # 会抛出 AttributeError，dict 没有这个属性
```

为什么导出后仍是整数？因为导出的是模型保存的处理后数据，不是将原始输入原样退回。转换成字典改变了容器类型与访问方式，不会把整数自动还原成最初的数字字符串。

## JSON 

```python
filters = SearchFilter.model_validate_json(text)
output = filters.model_dump_json()

assert isinstance(output, str)
assert isinstance(SearchFilter.model_validate_json(output), SearchFilter)
```

即便 JSON 文本看起来像字典，仍不能拿 `output["start_year"]` 当字典键访问；需要先解析。已经得到 Pydantic 实例时也不应把它当作 JSON 文本再次解析。

补充边界：`model_dump()` 默认使用 Python 模式，日期等字段可能保留为 Python 对象；`model_dump(mode="json")` 返回适合 JSON 的字典数据，`model_dump_json()` 则返回编码好的 JSON 字符串。嵌套模型通过 `model_dump()` 会递归导出，普通 `dict(model)` 不等价于这一递归行为。[序列化文档](https://docs.pydantic.dev/latest/concepts/serialization/)

## model_json_schema 描述规则，不导出实例数据

```python
schema = SearchFilter.model_json_schema()

assert isinstance(schema, dict)
assert schema["properties"]["start_year"]["type"] == "integer"
```

它回答“这个类要求怎样的数据结构”，不回答“这一份请求的开始年份是多少”。因此不需要先创建 `filters`。本轮已明确这一点：类的结构说明不依赖真实值。

草稿中的“`model_validate()` 返回一个 BaseModel 的子类”也需要精确化：`SearchFilter` 才是子类；`model_validate()` 返回的是 **`SearchFilter` 的实例**。

## 复习自测

```python
text = '{"start_year": "2020", "end_year": "2025"}'
filters = SearchFilter.model_validate_json(text)
result = filters.model_dump()
```

**问：`result` 是什么，如何取年份？** 答：字典，用 `result["start_year"]`，得到整数 2020。

**问：`model_dump_json()` 与 `model_json_schema()` 可以互换吗？** 答：不可以。前者导出实例数据的 JSON 文本，后者生成模型结构规则的字典。

相关：[[05-外部字段映射与额外字段处理]]、[[06-LangChain结构化输出与本地校验]]。

---

下一篇：[[05-外部字段映射与额外字段处理]]

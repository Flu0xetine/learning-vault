---
area: Pydantic
type: note
created: 2026-09-18
updated: 2026-09-18
related_daily:
  - "[[2026-09-18]]"
---

# BaseModel继承与运行时校验

本篇回答：`class Request(BaseModel)` 是什么意思？类型注解已经写了 `int`，为什么还需要 Pydantic？适用于 Pydantic v2。

## BaseModel 是父类，不是形参

日记特别记录了这个语法疑点：`BaseModel` 不是 `Request` 的形参。类声明括号里的内容指定父类；下面定义了一个继承 `BaseModel` 的新类。

```python
from pydantic import BaseModel

class Request(BaseModel):
    question: str
    max_results: int

request = Request(question="什么是 RAG？", max_results="3")

assert isinstance(request, Request)
assert request.max_results == 3
assert isinstance(request.max_results, int)
```

- `BaseModel`：Pydantic 提供的基础模型类。
- `Request`：我们定义的子类，描述字段及其规则。
- `request`：调用 `Request(...)` 后得到的实例，保存这一份具体请求的数据。
- `question`、`max_results`：调用时传入的字段参数。

这里不需要自己手写 `__init__`。Pydantic 利用字段注解建立校验规则，在正常构造实例时接收输入、执行允许的转换与校验，并提供导出能力。模型与实例的关系参见 [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)。

## 类型声明和运行时检查是两件事

| 形式 | 描述什么 | 是否自动执行运行时校验 |
|---|---|---|
| 普通 `dict` | 一组键值 | 否 |
| Python 类型注解 | 期望的类型，供编辑器和类型检查工具分析 | Python 本身不会据此阻止赋值 |
| `TypedDict` | 字典应有哪些键、各键值的类型 | 否，运行时对象仍是字典 |
| `BaseModel` 子类 | 字段类型、约束及自定义校验规则 | 正常构造或调用校验方法时会执行 |

例如 `age: int = "hello"` 不会仅因类型注解而在 Python 运行时报错。`TypedDict` 也不是带自动检查能力的字典容器；类型检查工具可以发现不匹配，但那不是运行时的异常。

## 转换成功不代表原始类型相同

本轮练习中的三种输入：

| 输入 | 结果 | 原因 |
|---|---|---|
| `Request(question="RAG？", max_results=3)` | 通过，字段是 `int` | 已是整数 |
| `Request(question="RAG？", max_results="3")` | 通过，字段是 `int` | 默认允许把数字字符串解析为整数 |
| `Request(question="RAG？")` | 失败 | `max_results` 没有默认值，是必填字段 |

如果传入 `"three"`，则无法解析为整数。Pydantic 不会猜测所有输入的含义，允许哪些转换取决于字段类型及配置。

补充边界：`Field(strict=True)` 可以要求这个整数字段拒绝 `"3"` 这样的字符串；也可以在一次校验时用 `Request.model_validate(data, strict=True)`。严格模式的具体规则仍与类型、Python 输入或 JSON 输入有关，不能概括成所有类型都要求完全相同的 Python 对象。[严格模式](https://docs.pydantic.dev/latest/concepts/strict_mode/)

## 校验通过说明什么

它说明这次输入经过处理后满足声明的校验规则，不说明问题内容有意义或答案符合事实。例如 `question: str` 本身不要求字符串非空。

普通赋值也不等于再次校验：默认情况下，创建后写入 `request.max_results = "错误"` 不会自动触发赋值校验。若确有需求，可以配置 `validate_assignment=True`。这也是在程序关键输入位置明确执行校验的原因。[赋值校验配置](https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.validate_assignment)

## 复习自测

**问：`Request` 和 `request` 哪个可以作为输出结构传给框架？**

答：传入模型类 `Request` 描述规则；实例 `request` 已包含一份具体数据。框架如何利用它，见 [[LangChain结构化输出与本地校验]]。

**问：`"3"` 被转成整数后，是否意味着所有外部输入都会被自动修好？**

答：不会。可转换且满足约束才通过；无法转换、缺少必填字段或违反规则都会失败。

下一篇：[[字段的必填性与取值约束]]。

---
area: Pydantic
type: note
created: 2026-09-18
updated: 2026-09-18
related_daily:
  - "[[2026-09-18]]"
---

# LangChain结构化输出与本地校验

本篇回答：Pydantic 类怎样描述大模型的输出？谁生成值、谁检查值？为什么设置了结构化输出还需要处理校验失败？本篇连接 [[模型与字典及JSON的转换]] 与 [[LangGraph状态与节点结果的校验边界]]。

## 传入模型类，生成具体值

```python
from typing import Literal
from pydantic import BaseModel, Field

class RouteDecision(BaseModel):
    route: Literal["search", "answer"] = Field(
        description="需要查资料时选 search，可以直接回答时选 answer"
    )
    reason: str = Field(description="选择该路线的原因")
```

下面是接入代码片段，前提是 `llm` 已配置好，且选定模型与集成支持所用的结构化输出方式；不是可以脱离模型配置直接运行的完整程序。

```python
router = llm.with_structured_output(RouteDecision)
decision = router.invoke("请判断问题的处理路线：今天上海天气怎么样？")
print(decision.route)
```

传入的是模型类 `RouteDecision`，不是已经填了 `route="search"` 的实例。类提供规则，值由大模型生成；`with_structured_output()` 配置调用和解析流程，`invoke()` 才发起请求。

在默认 `include_raw=False`、成功解析及校验的情况下，`decision` 是 `RouteDecision` 实例，可以读取 `decision.route`。这与导出后的字典访问方式不同。[LangChain 结构化输出](https://docs.langchain.com/oss/python/langchain/models#structured-output)

## JSON Schema 如何表达规则

可以在不创建实例时调用：

```python
schema = RouteDecision.model_json_schema()
assert schema["properties"]["route"]["enum"] == ["search", "answer"]
```

本轮已经解决的疑点：这里输出的是类的结构说明，不需要真实字段值。典型的 Schema 内容包括：

| Schema 内容 | 描述什么 |
|---|---|
| `type` | 对象、字符串、整数等类型 |
| `properties` | 每个字段的规则 |
| `required` | 必须提供的字段名称 |
| `enum` | 允许的取值，如 `search`、`answer` |
| `description` | 面向读者或模型的说明 |

许多数值与长度约束也有对应表达，但能否提交给某一模型供应商，还要看其支持的 Schema 子集。通常直接传入 Pydantic 类即可，由 LangChain 集成完成结构转换，不需要手工先调用 `model_json_schema()`。[Pydantic JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/)

## Schema 不必作为普通提示词发送

草稿已经注意到：结构规则不一定只是拼接到提示词里。常见方式包括供应商原生结构化输出，以及通过工具调用参数结构获得输出。部分集成也提供 JSON mode，但 JSON 格式有效本身不代表满足目标 Schema。

具体默认方式、可用参数与 Schema 支持范围取决于模型及其集成。应针对所用模型确认，而不是把一个集成的默认值推广到所有 `llm`。

## 自定义 Python 逻辑与模型端规则的边界

**草稿中需要纠正的表述：“Pydantic 的规则都有对应的 JSON Schema”。**

更准确地说：很多内置类型和约束能表达为 JSON Schema；但 `@field_validator`、`@model_validator` 里任意编写的 Python 业务逻辑，不会自动完整翻译进去。例如“年份范围必须符合某个外部业务条件”不能仅靠注册一个 Python 函数让远端模型知道。

可以通过 `Field(description=...)` 或提示词告诉模型这些要求，以帮助生成；实际检查仍由本地校验器执行。描述文字也不能代替约束，例如 `description="必须非空"` 不等于 `min_length=1` 或去空白检查。

有关字段校验器与 Schema 的关系，参见 [Pydantic 校验器文档](https://docs.pydantic.dev/latest/concepts/validators/#json-schema-and-field-validators)。

## 校验发生在 invoke 成功返回之前

```text
模型类 → 框架提取结构规则 → 发起模型请求
                                  ↓
                            收到供应商响应
                                  ↓
                       解析 + Pydantic 本地校验
                                  ↓
                  invoke 成功返回 RouteDecision 实例
```

**草稿中的“`invoke()` 返回结果后再次本地校验”容易造成时序误解。** 对默认返回已解析 Pydantic 实例的调用而言，本地解析与校验在 `invoke()` 成功返回之前完成；调用者通常不必为了取得实例再手动 `model_validate_json()` 一遍。

结构校验通过只能说明符合已声明的规则。例如 `route="answer"` 是合法选项，但对实时天气问题仍可能是错误判断。Pydantic 不会自动验证事实或任务决策是否正确。

## 校验失败不等于自动重新生成

直接使用 `with_structured_output()`，不能假定它会持续让模型改写直到通过。默认解析失败通常抛出异常；异常可能是 Pydantic 的校验错误或框架包装的解析错误，具体取决于集成。

支持 `include_raw=True` 的标准返回形式允许保留原始响应和解析状态：

```python
router = llm.with_structured_output(RouteDecision, include_raw=True)
result = router.invoke("请判断问题的处理路线：今天上海天气怎么样？")

if result["parsing_error"] is not None:
    # 进入错误分支：记录问题，决定是否有限重试或返回失败
    print(result["parsing_error"])
else:
    decision = result["parsed"]
    print(decision.route)
```

此时 `result` 是包装字典，`parsed` 才是解析后的实例；解析失败时通常为 `None`。这个选项不代表所有网络、鉴权或供应商请求异常也都会被转成 `parsing_error`。[原始响应与解析结果](https://docs.langchain.com/oss/python/langchain/models#structured-output)

需要纠错重试时，应明确次数上限、传回模型的错误提示、最终失败分支。网络错误重试与“根据业务校验错误重新生成”是不同机制。本轮尚未完成真实模型接入与重试实操。

## 复习自测

**问：为什么传 `RouteDecision`，而不是 `RouteDecision(route="search", reason="...")`？**

答：前者描述待生成数据的规则；后者已是一份具体结果，也不是该接口要求的 Pydantic 类形式。

**问：在校验器里写了奇数规则，大模型一定知道吗？**

答：不会自动知道全部 Python 逻辑。需要描述生成要求，并保留本地检查和失败处理。

**问：`include_raw=True` 后能直接写 `result.route` 吗？**

答：不能。先检查错误，再使用 `result["parsed"].route`。

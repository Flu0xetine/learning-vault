---
area: Pydantic
type: note
created: 2026-09-18
updated: 2026-09-19
related_daily:
  - "[[2026-09-19]]"
  - "[[2026-09-18]]"
---

# 07-LangGraph状态与节点结果的校验边界

## 本篇概览

本篇区分外部输入模型、节点结果模型和 LangGraph 共享 State 的职责，并用 `StateGraph` 的最小离线示例演示：读取状态、调用 `model_validate()` 校验数据，再以 `model_dump()` 返回局部更新。它说明 `TypedDict` 状态与节点内部的 Pydantic 模型可以配合使用，关键在于结果如何映射到状态字段以及校验放在哪里。核心是：声明 Pydantic State 不能直接等同于所有更新和最终输出都已校验，字段取值约束也不会自动创建条件边；完整分流、消息状态与真实 LLM 接入仍待继续学习。

## 三种不同职责

| 数据对象 | 描述什么 | 本轮采用的示例 |
|---|---|---|
| 输入模型 | 一次外部请求应满足什么规则 | `Request` |
| 节点结果模型 | 某次分析或 LLM 输出的结构 | `RouteDecision` |
| 图的共享 State | 节点之间需要保存和传递哪些值 | `TypedDict` 或 `BaseModel` 状态模式 |

这三种结构不必相同。分类结果可以只有 `route`、`reason`，而共享 State 还保存原始 `question`。因此“不把整个 State 改成 Pydantic”并不妨碍在节点内部使用 Pydantic。

LangGraph 的 `StateGraph` 支持 `TypedDict`、dataclass 和 Pydantic 状态模式。使用哪一种应由需要的运行时校验、数据访问方式及开销决定；类型注解本身不等于自动校验所有流经的数据。[Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)

## 用 TypedDict 管理状态，在节点边界明确校验

下面是整理时补充的最小离线示例，用固定字典模拟分类器输出，目的是观察数据在边界处的形态；它不是实际调用过 LLM 的问题分流助手。该示例已于 2026-09-18 在 Python 3.12.14、Pydantic 2.13.5、LangGraph 1.2.11 下本地执行通过。

```python
from typing import Literal, NotRequired, TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END

class Request(BaseModel):
    question: str = Field(min_length=1)

class RouteDecision(BaseModel):
    route: Literal["search", "answer"]
    reason: str

class State(TypedDict):
    question: str
    route: NotRequired[Literal["search", "answer"]]
    reason: NotRequired[str]

def classify(state: State):
    request = Request.model_validate({"question": state["question"]})
    raw_result = {
        "route": "search",
        "reason": f"示例：为问题“{request.question}”选择检索",
    }
    decision = RouteDecision.model_validate(raw_result)
    return decision.model_dump()

builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_edge(START, "classify")
builder.add_edge("classify", END)
graph = builder.compile()

result = graph.invoke({"question": "今天上海天气怎么样？"})
assert result["question"] == "今天上海天气怎么样？"
assert result["route"] == "search"
```

`NotRequired`（这里用 Python 3.11+ 写法）描述这两个键可以暂时缺失，因为首次输入只有问题；它不是默认值，也不是 Pydantic 的校验设置。

节点的过程是：读取 State 字典 → 校验请求 → 得到原始分类数据 → 校验为 `RouteDecision` → 返回要更新的状态字段。`TypedDict` 状态用 `state["question"]` 访问；局部 Pydantic 实例用 `decision.route` 访问。

`decision.model_dump()` 在这里恰好得到 `{"route": ..., "reason": ...}`，对应 State 的两个键。图应用这些局部更新，原来的 `question` 保留。并不是任意 Pydantic 模型的导出结果都可以直接作为任意图的更新：若 State 用 `decision` 这个嵌套键保存结果，就必须按该状态设计返回相应结构。

接入真实模型时，可将模拟部分替换为 [[06-LangChain结构化输出与本地校验]] 中的 `router.invoke(...)`，成功返回的 `decision` 已经过解析与校验。条件边再读取路由值选择节点；这个转换本身不会自动创建分支。

## Pydantic State 不是全程校验的承诺

也可以定义 `class State(BaseModel): ...`，然后传给 `StateGraph(State)`。但“声明了 State 模型”与“节点的所有写入和最终输出都再次通过模型校验”不能画等号。

官方的 Pydantic State 用法说明列出了校验范围与返回类型的限制。实际接入时，应结合使用的版本、节点输入模式和调用方式确认；不要因为指定了模型类就假定 `graph.invoke()` 必然返回这个类的实例。[Pydantic State 的限制说明](https://docs.langchain.com/oss/python/langgraph/use-graph-api#use-pydantic-models-for-graph-state)

如果关键输出必须满足业务规则，可以在确定的位置明确调用对应模型的 `model_validate(...)`，并处理失败。对已经存在、后来被修改过的模型实例，不能不加条件地认为再次传给 `model_validate` 一定完整重校验；实例重校验受配置影响。需要检查导出的值时，可从输出字典明确校验。

本篇先固定边界设计，不把尚未做过的完整图集成写成已完成成果。消息 reducer、持久化和多节点更新另行学习。

## 复习自测

**问：State 是 TypedDict，LLM 结果还能是 Pydantic 模型吗？**

答：可以。它们描述不同层的数据；节点负责把结果映射成 State 所需的更新。

**问：节点只返回 `route`、`reason`，是不是把 `question` 删除了？**

答：在这里的状态定义与普通局部更新中不会。没有更新的键保留；复杂字段怎样合并还取决于 reducer。

**问：`Literal` 只允许两个路由值，是否就已经连好了图的两条条件边？**

答：没有。Pydantic 限制值，LangGraph 的条件边决定执行路径。

---

下一篇：暂无

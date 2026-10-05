from typing import TypedDict, Annotated
from operator import add # operator.add 对列表执行的是：旧列表 + 新列表 ，它不是 LangGraph 专属功能，而是 Python 自带的函数；LangGraph 只是把它拿来定义状态的合并方式。
from langgraph.graph import StateGraph, START, END

# Annotated[T, metadata...] 是 Python 为类型 T 附加元数据的工具，不会包装或改变变量本身。静态类型检查主要把变量视为 T 类型 
# 如果用字典or列表实现附加元数据，则会改变数据类型为dict or list

class State(TypedDict):
    logs: Annotated[list[str], add]

# Reducer 绑定在 State 的字段上，不绑定在某个节点上。
# 一旦这样声明，所有节点只要返回 logs 更新，LangGraph 都会默认执行add

def node_a(state: State):
    return {
        "logs": ["node_a 执行完毕"]
    }


def node_b(state: State):
    return {
        "logs": ["node_b 执行完毕"]
    }

# 使用 Overwrite 可以单次绕过 绑定字段的 Reducer 覆盖
# from langgraph.types import Overwrite
# def node_c(state: State):
#     return {
#         "logs": Overwrite(["logs清空"])
#     }

builder = StateGraph(State)

builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)

graph = builder.compile()

result = graph.invoke({
    "logs": ["图开始执行"]
})

print(result)

# 自定义ruducer
# def my_reducer(old,new):
#   ....
#   return result
# Reducer 的返回值会成为该字段的新状态值
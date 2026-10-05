from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    topic: str
    logs: Annotated[list[str], add]


def node_a(state: State):
    return {
        "logs": [f'node_a 处理了 {state["topic"]}']
    }


def node_b(state: State):
    return {
        "logs": [f'node_b 处理了 {state["topic"]}']
    }


def summary(state: State):
    print("summary 看到的日志：", state["logs"])

    return {
        "logs": ["summary 执行完毕"]
    }


builder = StateGraph(State)

builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_node("summary", summary)

# Step1: Start -> node_a & node_b
builder.add_edge(START, "node_a")
builder.add_edge(START, "node_b")
# Step2: node_a & node_b -> summary
builder.add_edge(["node_a", "node_b"], "summary")
# a 和 b 都执行完才会执行summary，如果写成node_a-> summary，node_b -> summary，则 summary 会执行两次
builder.add_edge("summary", END)
# Start -> node_a & node_b -> summary -> END
# a 和 b 可以并行执行  
# LangGraph要求你明确声明：多个并行更新应该怎样合并？ 必须写 ruducer 不接受谁快谁获胜
# 但是如果一个超步中的节点各自修改不同的字段，则不要求写 ruducer
graph = builder.compile()

result = graph.invoke({
    "topic": "LangGraph",
    "logs": ["图开始执行"]
})

print(result)
# START ─→ A
#    └──→ B ─→ C
# A 和 B 在一个超步，如果 A 卡住，B 的下游 C 也会被阻塞，即使 B 早就完成了。
# 所以即使 A 和 C 不存在因为要写同一字段所以强制要求写 reducer 的情况
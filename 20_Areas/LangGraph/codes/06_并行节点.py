from typing import Literal
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
# 如果一个上游节点有多个下游节点，直接连接即可实现多个下游节点同一超步中执行。
class State(TypedDict):
    score: int
    result: str


def check_score(state: State):
    return {}


def passed(state: State):
    return {"result": "通过"}


def failed(state: State):
    return {"result": "未通过"}


def router(state: State) -> Literal["passed", "failed"]:
    if state["score"] >= 60:
        return "passed"
    return "failed"


builder = StateGraph(State)

builder.add_node("check_score", check_score)
builder.add_node("passed", passed)
builder.add_node("failed", failed)

builder.add_edge(START, "check_score")
builder.add_conditional_edges("check_score", router)
builder.add_edge("passed", END)
builder.add_edge("failed", END)

graph = builder.compile()

ascii_graph = graph.get_graph().draw_ascii()
print(ascii_graph)
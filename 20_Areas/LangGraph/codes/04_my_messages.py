# 使用 add_messages 它发现两条消息的 id 相同，就用新消息替换旧消息
# 它比 operator.add 多做了两件事：
# - 新消息追加；
# - 相同消息 id 时更新原消息，而不是产生重复项；
# - 还能把字典形式的消息转换成 LangChain 消息对象。

from typing import TypedDict, Annotated
from langchain.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END

# AnyMessage 是联合类型 并非其他消息的基类
# items: list[str | int] 列表既可以放 str 也可以放 int
# 这里不管是 AIMessage 还是 HumanMessage 都放在同一个列表里
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def add_user_message(state: State):
    return {
        "messages": [
            HumanMessage(content="你好，我叫小汪",id = "h1"), # id 不必须
        ]
    }

def add_user_message_new(state: State):
    return {
        "messages": [
            HumanMessage(content="你好，我叫小王",id = "h1"), # 覆盖 而非追加
        ]
    }

def add_ai_message(state: State):
    return {
        "messages": [
            AIMessage(content="你好，小王！",id = "a1")
        ]
    }


builder = StateGraph(State)

builder.add_node("add_user_message", add_user_message)
builder.add_node("add_user_message_new", add_user_message_new)
builder.add_node("add_ai_message", add_ai_message)

builder.add_edge(START, "add_user_message")
builder.add_edge("add_user_message", "add_user_message_new")
builder.add_edge("add_user_message_new", "add_ai_message")
builder.add_edge("add_ai_message", END)

graph = builder.compile()

result = graph.invoke({
    "messages": []
})

print(result)


# 仅用于理解继承关系的伪代码，非框架源码

# class BaseMessage:
#     content: str
#     id: str | None
#     name: str | None

# class HumanMessage(BaseMessage):
#     type = "human"

# class SystemMessage(BaseMessage):
#     type = "system"

# class AIMessage(BaseMessage):
#     type = "ai"
#     tool_calls: list

# class ToolMessage(BaseMessage):
#     type = "tool"
#     tool_call_id: str
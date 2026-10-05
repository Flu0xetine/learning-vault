from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class User(TypedDict):
    name: str
    age: int
    id: int

# 1. 定义状态
class State(TypedDict):
    user: User
    name: str
    greeting: str
# 若使用 class State(MessagesState):
# 适合聊天机器人和 Agent 自带 messages: Annotated[list[AnyMessage], add_messages] 不必再写，更简洁


# 2. 定义节点
def create_greeting(state: State):
    name = state["name"]

    return {
        "greeting": f"你好，{name}" # 把变量放进字符串的写法 {}  也可直接 "greeting": f"你好，{state['name']}"
    }
# Q：为什么返回字典？
# A： 因为节点需要告诉 LangGraph：我想更新 greeting 字段，新值是 "你好，小王"。 节点返回的是“局部更新”，不必返回完整状态。

# 补：节点不止可以return dict  还可以 return Command/None 给 “langgraph运行时” 由它调度
def get_user_info(state: State):
    return {
        "greeting": f"你好，{state["user"]["name"]},你的年龄是{state["user"]["age"]},你的id是{state["user"]["id"]}"
    }

# 3. 创建图的构建器
builder = StateGraph(State)

# StateGraph(
#     OverallState,
#     context_schema=Context,
#     input_schema=InputState,
#     output_schema=OutputState,
# )

# 4. 添加节点
builder.add_node("create_greeting", create_greeting)
builder.add_node("get_user_info", get_user_info)


# 5. 添加边
builder.add_edge(START, "create_greeting")
builder.add_edge("create_greeting", "get_user_info")
builder.add_edge("get_user_info", END)


# 6. 编译
graph = builder.compile()


# 7. 调用
result = graph.invoke({
    "user":{
        "name": "小李",
        "age": 20,
        "id": 123456
    },
    "name": "小王",
    "greeting": ""
})

print(result)

ascii_graph = graph.get_graph().draw_ascii()
print(ascii_graph)
# 简单图中，result 通常就是最终 State；
# 复杂图中，result 更准确地说是“最终对外输出”；
# 如果设置了 output_schema，它可能只是最终 State 的一部分；
# result 不是最后一个节点的返回值，而是整张图所有有效更新合并后的结果。

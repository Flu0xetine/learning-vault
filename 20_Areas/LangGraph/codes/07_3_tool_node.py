from dotenv import load_dotenv

from langchain.messages import HumanMessage
from langchain.tools import tool
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition


# 读取 .env 中的 DEEPSEEK_API_KEY
load_dotenv()


# 1. 定义工具
@tool
def get_weather(city: str) -> str:
    """查询指定城市今天的天气。"""
    return f"{city}今天晴朗，气温 20～28℃。"

# 工具箱列表，可以有多个工具
tools = [get_weather]


# 2. 创建模型，并把工具说明绑定给模型
model = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
)
model_with_tools = model.bind_tools(tools)


# 3. 定义模型节点
def model_node(state: MessagesState):
    response = model_with_tools.invoke(state["messages"])

    return {
        "messages": [response]
    }


# 4. 构建图
builder = StateGraph(MessagesState)

builder.add_node("model", model_node)
# 工具箱节点，可有多个工具
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "model")
# 模型节点 和 工具箱节点 之间建立条件边，其中路由函数不需要亲自编写
# 路由函数 tools_condition 自动判断 AIMessage最后一条 有 tool_calls 时进入 tools，否则结束，AIMessage 可能会有多个 tool_calls 并为不同工具分配 id 用于区分
builder.add_conditional_edges(
    "model",
    tools_condition,
)

# 工具执行完，将结果交回模型
builder.add_edge("tools", "model")

graph = builder.compile()


# 5. 调用图
result = graph.invoke(
    {
        "messages": [
            HumanMessage(content="北京今天天气怎么样？")
        ]
    }
)


# 6. 输出完整消息过程
for message in result["messages"]:
    message.pretty_print()

# 7. 由于工具箱节点可以包含多个工具，同一条一条 AIMessage 也可能包含多个工具调用放在一个列表里
# 每个调用会分配 id，每个工具返回的 ToolMessage 会有相应的 id 与之对应

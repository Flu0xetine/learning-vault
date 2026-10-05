# 1.Literal：值只能来自指定选项
# def router(state) -> Literal["rejected", "approved"] 这表示：router 应该只返回 "rejected" 或 "approved" 中的一个
# 作用：帮助编辑器发现拼写错误；帮助类型检查工具检查代码；帮助 LangGraph 推断并绘制可能的路径。

# 2.Sequsence：返回一个有顺序的集合，例如：list,tuple 
# def router(state) -> Sequence[str]:
#     return ["node_a", "node_b"]
# 返回多个节点表示：下一超步同时执行这些节点。

# 3.Sequence & Literal :可能返回多个目标(S)，并对每个目标的范围进行限制(L)
# def router(state) -> Sequence[Literal["a", "b", "c"]]: 每个目标只能是 a、b、c 之一。
#     return ["a", "c"]

# 4.path_map : 写在 route 出发的 edge 里，将路由函数返回值 -> 要执行的节点名 。 仅在这一个 route 函数里生效
# def router(state) -> Literal["通过", "不通过"]:
#     if state["passed"]:
#         return "通过"
#     return "不通过"


# 条件边连接的是 节点 -> 路由函数
# builder.add_conditional_edges(
#     "check",
#     router,
#     path_map={
#         "通过": "yes_node",
#         "不通过": "no_node",
#     },
# )
# 如果返回值同节点名 则可以缩写为 path_map=["yes_node", "no_node"]


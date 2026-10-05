from langchain.tools import tool


@tool
def get_weather(city: str) -> str:
    """查询指定城市的当日天气。

    """
    # 严格来说不是普通注释，而是 docstring（文档字符串）。Python 会把它保存到函数对象的 __doc__ 属性里：
    # 模型只知道参数的类型
    print(get_weather.__doc__)
    return f"{city}今天晴，最高气温 26℃"


@tool(parse_docstring=True) # 要求解析并生成参数的描述
def get_weather(city: str) -> str:
    """查询指定城市的当日天气。

    适用于用户询问当前天气、气温或降水情况。
    不支持查询历史天气。

    Args:
        city: 城市名称，例如“北京”或“上海”。
    """
    # 补充何时调用的描述以及参数的描述
    # Args 与 description 之间如果没有空行可能报错：Found invalid Google-Style docstring.
    print(get_weather.__doc__)
    return f"{city}今天晴，最高气温 26℃"

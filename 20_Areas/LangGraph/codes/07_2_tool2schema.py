from langchain.tools import tool

# 补：此方法简洁，适合约束较少的参数
# 后续 工具描述依然使用 doc，但参数描述使用 pydantic 

@tool(parse_docstring=True) # 要求解析并生成参数的描述
def get_weather(city: str) -> str:
    """查询指定城市的当日天气。

    适用于用户询问当前天气、气温或降水情况。
    不支持查询历史天气。
    
    Args:
        city: 城市名称，例如“北京”或“上海”。
    """
    # 补充何时调用的描述以及参数的描述
    print(get_weather.__doc__)
    return f"{city}今天晴，最高气温 26℃"

print(get_weather.args_schema.model_json_schema())

import json
schema = get_weather.args_schema.model_json_schema()
print(
    json.dumps(
        schema,
        ensure_ascii=False,
        indent=2,
    )
)

# model_with_tools = model.bind_tools([get_weather]) # 交付模型说明
# schema不会被直接塞进提示词里
# 以下是http请求示例

example = """POST /chat/completions
Content-Type: application/json
Authorization: Bearer ...
{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "user",
      "content": "北京天气怎么样？"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "查询指定城市当前的天气。",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {
              "type": "string",
              "description": "城市名称。"
            }
          },
          "required": ["city"]
        }
      }
    }
  ],
  "tool_choice": "auto"
}"""

# schema确实在里面
# llm也确实只能接受token序列作为输入
# 但服务商会根据当前模型版本对应的 内部模板 将其序列化 而非直接输入给 llm
# 另外，模型生成的原始结果也仍然是 token。服务商会再进行反向解析，如果结果符合工具调用的协议，则会进一步进行结构化输出


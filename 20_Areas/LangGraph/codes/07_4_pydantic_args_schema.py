from pydantic import BaseModel, Field
from langchain.tools import tool

class WeatherInput(BaseModel):
    city: str = Field(description="城市名称，例如北京")
    days: int = Field(
        ge=1,
        le=7,
        description="查询天数，范围为1到7",
    )

@tool(args_schema=WeatherInput)
def get_weather(city: str, days: int) -> str:
    """查询未来天气。"""
    return f"{city}未来{days}天的天气"
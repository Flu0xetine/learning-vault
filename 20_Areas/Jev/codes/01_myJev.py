import asyncio

from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul, Score
from dotenv import load_dotenv

load_dotenv()

async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        result = await client.system_one(
            "I was charged twice. Please help ASAP.",
            {
                "billing": Noul(instructions="Is this about billing?"),

                "tone": Choice(
                    instructions="What is the tone?",
                    criteria={"calm": None, "angry": None},
                ),
                
                "urgency": Score(
                    instructions="How urgent is this?",
                    criteria=["low", "medium", "high"],
                ),
            },
        )
        print(
            result.nouls["billing"].noul,
            result.choices["tone"].choice,
            result.scores["urgency"].score,
        )


asyncio.run(main())
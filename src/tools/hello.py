from langchain.tools import StructuredTool
from pydantic import BaseModel

from tracing import log_llm_tool


class HelloArgs(BaseModel):
    pass  # No arguments needed


def get_hello_target(args: HelloArgs) -> str:
    """Returns the target to say hello to. Ignores input."""
    log_llm_tool("HelloTool")
    return "World"


hello_tool = StructuredTool.from_function(
    func=get_hello_target,
    name="HelloTool",
    description="Use this tool to find out who to say hello to. It takes no parameters.",
    args_schema=HelloArgs,
)

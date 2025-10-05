from langchain.tools import Tool


def get_hello_target(input_str: str) -> str:
    """Returns the target to say hello to. Ignores input."""
    return "World"


hello_tool = Tool(
    name="HelloTool",
    description="Use this tool to find out who to say hello to. It takes no parameters.",
    func=get_hello_target,
)

from src.tools.hello import hello_tool


def test_hello_tool():
    """Test that the hello tool returns 'World'."""
    result = hello_tool.func("")
    assert result == "World"

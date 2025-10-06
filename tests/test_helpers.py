from helpers.context import Context
from helpers.fuzzy import create_fuzzy_index


def test_fuzzy_index_basic():
    """Test basic fuzzy search functionality."""
    index = create_fuzzy_index()

    # Add some test data
    index.add("Hello", "objectA")
    index.add("World", "objectB")
    index.add("Python", "objectC")

    # Test exact match
    term, obj = index.search("Hello")
    assert term == "Hello"
    assert obj == "objectA"

    # Test fuzzy match
    term, obj = index.search("H1llo")  # Should match "Hello"
    assert term == "Hello"
    assert obj == "objectA"

    # Test case insensitive
    term, obj = index.search("hello")
    assert term == "Hello"
    assert obj == "objectA"

    # Test no match
    term, obj = index.search("Nothing")
    assert term is None
    assert obj is None

    # Test empty query
    term, obj = index.search("")
    assert term is None
    assert obj is None


def test_fuzzy_index_distance_threshold():
    """Test that matches respect distance threshold."""
    index = create_fuzzy_index()
    index.add("test", "value")

    # Should match (distance 1, threshold allows)
    term, obj = index.search("tset")
    assert term == "test"
    assert obj == "value"

    # Should not match (distance too high)
    term, obj = index.search("completelydifferent")
    assert term is None
    assert obj is None


def test_context_build():
    """Test Context building with sections, wraps, and examples."""
    c = Context()
    c = c.add("Chapter To Translate", "Here is attached chapter")
    c = c.wrap("chapter", "Long Text")
    c = c.add("Ask", "Do Translate Attached Chapter")
    c = c.example(in_="Something Nice", out="Что-то Забавное")
    c = c.failure_example(in_="Something Ugly", err="Don't translate word Ugly")
    result = c.build()

    expected = """** CHAPTER TO TRANSLATE **
Here is attached chapter

<chapter>
Long Text
</chapter>

** ASK **
Do Translate Attached Chapter

<examples>
<good_example>
  <in>Something Nice</in>
  <out>Что-то Забавное</out>
</good_example>
<bad_example DON'T DO THIS>
  <in>Something Ugly</in>
  <err>Don't translate word Ugly</err>
</bad_example>
</examples>
"""

    assert result == expected


def test_context_immutability():
    """Test that Context is immutable."""
    c1 = Context()
    c2 = c1.add("Title", "Text")
    c3 = c2.wrap("tag", "content")

    # Original should be unchanged
    assert c1.build() == ""
    assert c2.build() == "** TITLE **\nText\n\n"
    assert c3.build() == "** TITLE **\nText\n\n<tag>\ncontent\n</tag>\n\n"


def test_context_empty():
    """Test empty Context."""
    c = Context()
    assert c.build() == ""


def test_context_only_examples():
    """Test Context with only examples."""
    c = Context()
    c = c.example(in_="in", out="out")
    result = c.build()
    expected = """<examples>
<good_example>
  <in>in</in>
  <out>out</out>
</good_example>
</examples>
"""
    assert result == expected

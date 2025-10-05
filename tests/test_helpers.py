from src.helpers.fuzzy import create_fuzzy_index


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

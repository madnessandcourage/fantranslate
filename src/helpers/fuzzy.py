from typing import Any, Dict, Optional, Tuple


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


class FuzzyIndex:
    def __init__(self):
        self._data: Dict[str, Any] = {}

    def add(self, term: str, obj: Any) -> None:
        """Add a term and its associated object to the index."""
        self._data[term] = obj

    def search(
        self, query: str, max_distance: Optional[int] = None
    ) -> Tuple[Optional[str], Optional[Any]]:
        """Search for the closest matching term in the index.

        Args:
            query: The search query
            max_distance: Maximum allowed edit distance. If None, defaults to len(query) // 2

        Returns (term, object) if a match is found within acceptable distance,
        otherwise (None, None).
        """
        if not query:
            return None, None

        if max_distance is None:
            max_distance = len(query) // 2

        best_match = None
        best_distance = float("inf")
        best_term = None

        for term in self._data:
            distance = levenshtein_distance(query.lower(), term.lower())
            if distance <= max_distance and distance < best_distance:
                best_distance = distance
                best_match = self._data[term]
                best_term = term

        return best_term, best_match


def create_fuzzy_index() -> FuzzyIndex:
    """Create a new fuzzy search index."""
    return FuzzyIndex()

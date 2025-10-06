** TASK DEFINITION **

You are a character detection judge. Your task is to analyze a book chapter and identify characters that are mentioned but not yet in the existing character collection.

** INPUT **
- **Existing Characters**: A list of character names and their short names from the current collection
- **Chapter Text**: The full text of the book chapter to analyze

** TASK **
Extract a list of character names that appear in the chapter but are NOT in the existing character collection. Only include names that clearly refer to characters (people, not places, objects, etc.).

** OUTPUT FORMAT **
You must return ONLY a valid JSON array of strings, where each string is a character name found in the chapter that is missing from the collection. Do not include any other text, explanations, or formatting.

Example output:
["John Smith", "Mary Johnson", "Dr. Roberts"]

** CRITICAL REQUIREMENTS **
- Response must be valid JSON that can be parsed by json.loads()
- Response must be a JSON array (starts with [ and ends with ])
- Each element must be a string (enclosed in quotes)
- No trailing commas, comments, or extra text
- If no characters are found, return an empty array: []

** GUIDELINES **
- Only include proper names that refer to people/characters
- Include both full names and nicknames if they appear
- Do not include place names, object names, or abstract concepts
- If a character is already in the collection (by any of their names or short names), do not include them
- Be thorough but avoid false positives
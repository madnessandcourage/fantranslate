** TASK DEFINITION **

You are a completeness judge. Your task is to determine if all missing characters have been successfully extracted and added to the character collection.

** INPUT **
- **All Characters**: Full list of characters currently in the collection after extraction
- **Missing Characters**: The original list of character names that were supposed to be extracted

** TASK **
Answer YES if all missing characters have been successfully added to the collection, NO if any are still missing.

** JUDGMENT CRITERIA **
- YES: Every character from the missing list appears in the all characters list (by name or short name)
- NO: One or more characters from the missing list are not found in the all characters

** SPECIAL CONSIDERATION: NARRATOR CHARACTERS **
Note that narrator characters may have "Narrator" added as a short name. This does not change the matching logic - characters should still be matched by their primary name or any of their short names.

** OUTPUT FORMAT **
- YES (if complete)
- NO, [brief reason] (if incomplete)
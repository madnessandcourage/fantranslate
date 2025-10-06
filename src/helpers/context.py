import os
from typing import Dict, List, Optional


class Context:
    def __init__(self, parts: Optional[List[Dict[str, str]]] = None) -> None:
        self.parts: List[Dict[str, str]] = parts or []

    def add(self, title: str, text: str) -> "Context":
        new_parts = self.parts + [{"type": "section", "title": title, "text": text}]
        return Context(new_parts)

    def wrap(self, tag: str, content: str) -> "Context":
        new_parts = self.parts + [{"type": "wrap", "tag": tag, "content": content}]
        return Context(new_parts)

    def example(self, in_: str, out: str) -> "Context":
        new_parts = self.parts + [{"type": "good_example", "in": in_, "out": out}]
        return Context(new_parts)

    def failure_example(self, in_: str, err: str) -> "Context":
        new_parts = self.parts + [{"type": "bad_example", "in": in_, "err": err}]
        return Context(new_parts)

    def pipe(self, filename: str) -> "Context":
        """Read content from a markdown file in the prompts directory and add it to context."""
        filepath = os.path.join("prompts", f"{filename}.md")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        new_parts = self.parts + [{"type": "pipe", "content": content}]
        return Context(new_parts)

    def has_examples(self) -> bool:
        """Check if the context already contains examples."""
        return any(
            part["type"] in ["good_example", "bad_example"] for part in self.parts
        )

    def build(self) -> str:
        main_parts: List[Dict[str, str]] = []
        examples: List[Dict[str, str]] = []
        for part in self.parts:
            if part["type"] in ["good_example", "bad_example"]:
                examples.append(part)
            else:
                main_parts.append(part)
        result = ""
        for part in main_parts:
            if part["type"] == "section":
                result += f"** {part['title'].upper()} **\n{part['text']}\n\n"
            elif part["type"] == "wrap":
                result += f"<{part['tag']}>\n{part['content']}\n</{part['tag']}>\n\n"
            elif part["type"] == "pipe":
                result += f"\n{part['content']}\n\n"
        if examples:
            result += "<examples>\n"
            for ex in examples:
                if ex["type"] == "good_example":
                    result += "<good_example>\n"
                    result += f'  <in>{ex["in"]}</in>\n'
                    result += f'  <out>{ex["out"]}</out>\n'
                    result += "</good_example>\n"
                elif ex["type"] == "bad_example":
                    result += "<bad_example DON'T DO THIS>\n"
                    result += f'  <in>{ex["in"]}</in>\n'
                    result += f'  <err>{ex["err"]}</err>\n'
                    result += "</bad_example>\n"
            result += "</examples>\n"
        return result

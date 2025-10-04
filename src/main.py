#!/usr/bin/env python3

import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        print("API key loaded successfully")
        from ai import ai
        joke = ai("You are a comedian.", "Tell me a funny joke.")
        print(joke)
    else:
        print("Failed to load API key")
    print("Hello World")

if __name__ == "__main__":
    main()
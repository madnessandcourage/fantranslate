#!/usr/bin/env python3

import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        print("API key loaded successfully")
    else:
        print("Failed to load API key")
    print("Hello World")

if __name__ == "__main__":
    main()
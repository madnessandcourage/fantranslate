import os
import sys
from pathlib import Path
from typing import Any, List, Optional, Tuple, cast

from dotenv import load_dotenv

# Always load .env
load_dotenv()

# If in no API key mode, unset the key
if os.getenv("NO_API_KEY_MODE"):
    os.environ.pop("OPENROUTER_API_KEY", None)

# pyright: ignore[reportUnknownVariableType] # langchain type stubs are incomplete
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage
from langchain.tools import BaseTool
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI
from openai import OpenAI

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ai_test_helpers import memoise_for_tests
from helpers.context import Context
from tracing import (
    log_enter,
    log_error,
    log_exit,
    log_llm_ai,
    log_llm_operator,
    log_llm_system,
    log_trace,
)

DEFAULT_MODEL: str = os.getenv("DEFAULT_AI_MODEL", "google/gemma-3-12b-it")

_client = None


def get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
    return _client


@memoise_for_tests
def ai(
    system_prompt: str, user_prompt: str, model: Optional[str] = None
) -> Optional[str]:
    log_enter("ai")
    if model is None:
        model = DEFAULT_MODEL
    log_trace("Model", model)
    client = get_client()
    log_llm_system(system_prompt)
    log_llm_operator(user_prompt)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    result = response.choices[0].message.content
    if result:
        log_llm_ai(result)
    log_exit("ai")
    return result


@memoise_for_tests
def agent(
    system_prompt: str,
    user_query: str,
    tools: List[BaseTool],
    previous_chat_history: Optional[List[BaseMessage]] = None,
    model: str = DEFAULT_MODEL,
) -> Tuple[str, List[BaseMessage]]:
    log_enter("agent")
    previous_chat_history = previous_chat_history or []

    log_llm_system(system_prompt)
    log_llm_operator(user_query)
    log_trace("Model", model)

    # Create LLM
    # Set environment variables for OpenAI configuration
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENROUTER_API_KEY", "")
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

    llm = cast(
        BaseLanguageModel[Any],
        ChatOpenAI(
            model=model,
            temperature=0,
        ),
    )

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages(  # type: ignore[attr-defined]
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    # Create memory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    for msg in previous_chat_history:
        memory.chat_memory.add_message(msg)

    # Create agent
    agent = create_openai_tools_agent(llm, tools, prompt)  # type: ignore[return-value,assignment] # langchain type stubs don't fully resolve generic types

    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=False,  # We use our custom tracing framework instead
        handle_parsing_errors=True,
    )

    # Run the agent
    response = agent_executor.invoke({"input": user_query})

    # Get the output
    output = response["output"]
    log_llm_ai(output)

    # Get updated chat history
    chat_history = memory.chat_memory.messages

    log_exit("agent")
    return output, chat_history


def yesno(
    user_prompt: str,
    model: Optional[str] = None,
    max_retries: int = 3,
    system_context: Optional[Context] = None,
) -> Tuple[bool, str]:
    log_enter("yesno")

    # Use provided context or create new one
    context = system_context or Context()

    # Always add YES/NO instructions
    context = context.add(
        "Instructions",
        "You are a judge that answers YES or NO questions. Your response must be exactly one of these formats:\n"
        "- YES (if the answer is yes)\n"
        "- NO, <brief reason> (if the answer is no)\n\n"
        "Do not add any prefixes, explanations, or additional text. Respond with a single line only.",
    )

    # Check if context already has examples
    if not context.has_examples():
        # Add built-in examples
        context = context.example(in_="Is Paris the capital of France?", out="YES")
        context = context.example(
            in_="Is London the capital of Germany?",
            out="NO, Berlin is the capital of Germany",
        )
        context = context.example(in_="Is 2 + 2 = 4?", out="YES")
        context = context.example(in_="Is the sky green?", out="NO, the sky is blue")

        # Add bad examples
        context = context.failure_example(
            in_="Is Tokyo the capital of Japan?", err="Based on my knowledge, YES"
        )
        context = context.failure_example(
            in_="Is Rome the capital of Italy?",
            err="YES\nRome is indeed the capital.",
        )
        context = context.failure_example(
            in_="Is Madrid the capital of Spain?",
            err="The answer is YES because Madrid is the capital city.",
        )

    system_prompt = context.build()

    for attempt in range(max_retries):
        log_trace("Attempt", str(attempt + 1))
        response = ai(system_prompt, user_prompt, model)

        if response is None:
            continue

        response = response.strip()

        if response == "YES":
            log_exit("yesno")
            return True, ""

        if response.startswith("NO, "):
            reason = response[4:].strip()  # Remove "NO, " prefix
            log_exit("yesno")
            return False, reason

        # Invalid response, retry
        log_trace("Invalid response", response)

    # All retries failed
    log_error(f"Failed to get valid YES/NO response after {max_retries} attempts")
    log_exit("yesno")
    raise ValueError(
        f"AI failed to provide a valid YES/NO response after {max_retries} attempts"
    )

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
from tracing import (
    log_enter,
    log_exit,
    log_llm_ai,
    log_llm_operator,
    log_llm_system,
    log_trace,
)

DEFAULT_MODEL: str = os.getenv("DEFAULT_AI_MODEL", "openai/gpt-4o-mini")

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

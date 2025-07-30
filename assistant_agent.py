"""Natural language interface to the BrowserAgent.

This script builds on top of the simple `BrowserAgent` class from
`agent.py` and integrates with OpenAI’s ChatCompletion API to plan actions
from arbitrary user requests.  The assistant receives a request in natural
language, asks a language model to map it to one of the supported browser
commands, and then executes the corresponding action.

To use this assistant you must set the `OPENAI_API_KEY` environment
variable to a valid OpenAI API key.  See https://platform.openai.com/ for
details.

Example usage:

    export OPENAI_API_KEY="sk-..."
    python assistant_agent.py chrome

    Ask me anything: search Python tutorials

The assistant will ask OpenAI to interpret the request and then run the
appropriate browser command.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Dict, Any

import openai

from agent import BrowserAgent


SYSTEM_PROMPT = (
    "You are an interpreter that converts high level browser tasks into"
    " structured commands.  Supported commands are:\n"
    "- open <url>: open a web page.\n"
    "- search <query>: perform a Google search.\n"
    "- click <partial link text>: click a link containing the given text.\n"
    "\n"
    "When given a user request, respond with a JSON object containing"
    " the keys 'command' and 'args'.  Do not include any explanations."
    " Examples:\n"
    "User: Open example.com\nResponse: {\"command\": \"open\", \"args\": \"example.com\"}\n"
    "User: search cats\nResponse: {\"command\": \"search\", \"args\": \"cats\"}"
)



def plan_action(request: str) -> Dict[str, Any]:
    """Use OpenAI to map a natural language request to a browser command.

    The function sends the user request to the ChatCompletion API with a
    fixed system prompt instructing it to output a JSON command.  It then
    parses the JSON response into a Python dict.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set."
        )
    openai.api_key = api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request},
            ],
            temperature=0.0,
        )
    except Exception as e:
        raise RuntimeError(f"Error while calling OpenAI API: {e}")

    content = response.choices[0].message["content"].strip()
    try:
        command_dict = json.loads(content)
        if not isinstance(command_dict, dict):
            raise ValueError
    except Exception:
        raise RuntimeError(
            f"Unexpected response from the language model: {content}"
        )
    return command_dict


def run_assistant(browser: str = "chrome", headless: bool = False) -> None:
    """Interactive loop that accepts natural language and executes actions."""
    agent = BrowserAgent(browser=browser, headless=headless)
    print(
        "Natural language browser assistant ready.  Ask it to open pages, "
        "search or click links.  Type 'exit' to quit."
    )
    try:
        while True:
            try:
                request = input("Ask me anything: ")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if request.strip().lower() in {"exit", "quit", "bye"}:
                break
            # Plan the action using the language model
            try:
                command = plan_action(request)
            except Exception as e:
                print(f"[Assistant] Failed to plan action: {e}")
                continue
            cmd = command.get("command", "").lower()
            args = command.get("args", "")
            # Dispatch the command to the underlying agent
            if cmd == "open":
                agent.open(str(args))
            elif cmd == "search":
                agent.search(str(args))
            elif cmd == "click":
                agent.click(str(args))
            else:
                print(
                    f"[Assistant] Received unsupported command from model: {command}"
                )
    finally:
        agent.close()


def main() -> None:
    browser = "chrome"
    headless = False
    for arg in sys.argv[1:]:
        if arg.lower() in {"chrome", "firefox"}:
            browser = arg.lower()
        elif arg.lower() == "--headless":
            headless = True
    run_assistant(browser=browser, headless=headless)


if __name__ == "__main__":
    main()

"""AutoGPT‑style browser automation agent.

This script defines a simple class, `BrowserAgent`, that wraps Selenium
WebDriver interactions.  The agent exposes a handful of high‑level
commands—opening pages, searching Google, and clicking links by partial text—
and interprets one‑line instructions provided by a user at runtime.

The goal of this example is to demonstrate how you might begin building
a browser automation agent that can be instructed with natural language–like
commands.  It does not attempt to perform long‑term planning or to use a
language model to decide on actions; however, the structure should make it
straightforward to integrate with an LLM if you desire.

Usage:

    python agent.py

    Enter a task (e.g. `open https://example.com`, `search cats`, `click Wikipedia`): search cats
"""
from __future__ import annotations

import sys
import time
import re
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import NoSuchElementException


class BrowserAgent:
    """A very small agent that exposes high level browser actions.

    The agent supports Chrome and Firefox out of the box.  Additional
    browsers can be added by adding more branches to the `__init__` method.
    Each action is implemented as a separate method.  The `run_task`
    dispatcher interprets a one‑line instruction and calls the appropriate
    action.
    """

    def __init__(self, browser: str = "chrome", headless: bool = False) -> None:
        """Create a new BrowserAgent.

        Parameters
        ----------
        browser: str, optional
            Which browser to use.  Supported values are "chrome" and "firefox".
        headless: bool, optional
            If true, runs the browser in headless mode (without a visible window).
        """
        self.browser = browser.lower()
        self.headless = headless
        if self.browser == "chrome":
            options = ChromeOptions()
            if headless:
                options.add_argument("--headless=new")
            # Allow Selenium Manager to download the driver if needed
            self.driver = webdriver.Chrome(options=options)
        elif self.browser == "firefox":
            options = FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            self.driver = webdriver.Firefox(options=options)
        else:
            raise ValueError(f"Unsupported browser: {browser}")

        # Set a short implicit wait time so that find_element will wait up to
        # this many seconds for elements to appear before throwing an error.
        self.driver.implicitly_wait(5)

    def open(self, url: str) -> None:
        """Navigate the browser to the given URL.

        If the URL does not include a scheme (e.g. "http"), this method will
        prefix "https://" automatically.
        """
        if not re.match(r"^[a-zA-Z]+://", url):
            url = "https://" + url
        print(f"[Agent] Opening {url}…")
        self.driver.get(url)

    def search(self, query: str) -> None:
        """Perform a Google search for the given query string."""
        print(f"[Agent] Searching for '{query}'…")
        self.driver.get("https://www.google.com")
        try:
            search_box = self.driver.find_element(By.NAME, "q")
        except NoSuchElementException:
            print("Could not locate Google search box.")
            return
        search_box.clear()
        search_box.send_keys(query)
        search_box.submit()
        # Give Google some time to load results
        time.sleep(2)

    def click(self, text: str) -> None:
        """Click the first link on the page containing the given partial text."""
        print(f"[Agent] Looking for a link containing '{text}'…")
        try:
            link = self.driver.find_element(By.PARTIAL_LINK_TEXT, text)
            link.click()
            print(f"[Agent] Clicked link containing '{text}'.")
        except NoSuchElementException:
            print(f"No link containing '{text}' was found on this page.")

    def run_task(self, instruction: str) -> Optional[bool]:
        """Interpret and execute a single-line instruction.

        Returns True if the agent should continue running, or False to
        indicate that the session should end.  Returns None if the command
        wasn't recognised.
        """
        instruction = instruction.strip()
        if not instruction:
            return True
        # allow the user to exit the loop
        if instruction.lower() in {"exit", "quit", "bye"}:
            print("[Agent] Exiting agent.")
            return False

        tokens = instruction.split()
        command = tokens[0].lower()
        args = tokens[1:]

        if command == "open" and args:
            url = args[0]
            self.open(url)
        elif command == "search" and args:
            query = " ".join(args)
            self.search(query)
        elif command == "click" and args:
            text = " ".join(args)
            self.click(text)
        else:
            print(
                "[Agent] Unrecognised command. Try 'open <url>', 'search <query>', or 'click <partial text>'."
            )
        return True

    def close(self) -> None:
        """Close the browser window."""
        self.driver.quit()


def main() -> None:
    """Entry point for command-line usage."""
    # Choose the browser based on a command-line argument if provided
    browser = "chrome"
    headless = False
    for arg in sys.argv[1:]:
        if arg.lower() in {"chrome", "firefox"}:
            browser = arg.lower()
        elif arg.lower() == "--headless":
            headless = True

    agent = BrowserAgent(browser=browser, headless=headless)
    try:
        print(
            "Browser agent ready. Type commands such as 'open example.com', 'search cats', or 'click Wikipedia'.\n"
            "Type 'exit' to quit."
        )
        while True:
            try:
                instruction = input("Enter a task: ")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            should_continue = agent.run_task(instruction)
            if should_continue is False:
                break
    finally:
        agent.close()


if __name__ == "__main__":
    main()

# AutoGPT Browser Agent

## Overview

This repository provides a **simplified browser automation agent** inspired by projects like Auto‑GPT.  Rather than attempting to replicate the full functionality of larger autonomous agents, this project focuses on one core objective: letting you drive a web browser with easy, natural‑language‑like commands from the command line.

The agent is designed to run on your own machine and uses the [Selenium](https://www.selenium.dev/) web‑automation library to control a Chrome or Firefox browser.  You can instruct it to open websites, perform Google searches, click links by partial text and perform other basic interactions.  This makes it a great starting point for automating repetitive web tasks or as a foundation for more advanced autonomous agents.

## Features

* **Open URLs** – quickly navigate to any site by specifying its URL.
* **Search the web** – perform Google searches directly from the command line.
* **Click links** – click the first visible link that matches a partial link text.
* **Pluggable browser support** – Chrome and Firefox are supported out of the box; other browsers can be added by extending a single class.

## Natural‑Language Assistant

In addition to the basic command interpreter in `agent.py`, the project includes an optional script, `assistant_agent.py`, that integrates with OpenAI’s GPT‑4 model.  This assistant allows you to describe what you want in plain English and will translate your request into one of the supported commands.

To use the assistant you **must** set an OpenAI API key in the environment:

```bash
export OPENAI_API_KEY="sk-..."
python assistant_agent.py
```

The assistant uses GPT‑4 to plan an action and then calls the corresponding method on the underlying `BrowserAgent`.  If the model returns an unsupported or malformed command, the assistant will inform you instead of taking any action.  Note that only a limited set of actions is supported (open, search, click), so some requests may not be possible without extending the agent.

## Requirements

* Python 3.9 or newer
* [Selenium 4](https://pypi.org/project/selenium/)
* A browser driver (e.g. ChromeDriver for Chrome or GeckoDriver for Firefox) installed and available on your `PATH`

You can install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

Make sure you have a matching WebDriver installed.  For Chrome you need [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads), and for Firefox you need [GeckoDriver](https://github.com/mozilla/geckodriver/releases).  The driver must be compatible with your installed browser version and accessible on your system `PATH`.

## Usage

Run the agent from the command line and provide a command when prompted:

```bash
python agent.py

Enter a task (e.g. `open https://example.com`, `search cats`, `click Wikipedia`): search chatbots
```

The agent understands simple one‑word commands followed by parameters:

* `open <url>` – navigates the browser to the specified URL.  If you omit the scheme, `https://` is prefixed automatically.
* `search <query>` – opens Google and performs a search for the given query.
* `click <partial text>` – clicks the first link on the current page that contains the provided text.  This is a simple heuristic and may not always pick the desired link on pages with many similar links.

The agent will remain running after executing a command so that you can issue additional commands without reopening the browser.  Type `exit` or press `Ctrl‑C` to quit.

## Extending the Agent

This project intentionally keeps the command language minimal.  If you need more advanced capabilities—such as filling out forms, scrolling, or extracting information—you can extend the `BrowserAgent` class in `agent.py` by adding new methods and updating `run_task` to recognise new instructions.

## License

This project is released under the MIT License.  See the [LICENSE](LICENSE) file for details.

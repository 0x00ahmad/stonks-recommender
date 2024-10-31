# Trading bot

This is the v0.0.0-alpha01 version of what is going to be a trading llm.

---

## Run it yourself:

Before you proceed, create a `.env` file in the root directory of the project and add the following variables:

```
OPENAI_API_KEY=<your openai api key>
YH_RAPID_API_KEY=<your yahoo finance api key>
```

The `OPENAI_API_KEY` is your OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). (Be sure you are logged in to OpenAI).

The `YH_RAPID_API_KEY` is your Yahoo Finance API key, which you can get [here](https://rapidapi.com/apidojo/api/yh-finance/playground/apiendpoint_04ce8c95-0ca5-4016-90a3-b62f58befdc8) (Be sure you are logged in to RapidAPI).

---

## Installing dependencies

1. Ensure you have `python` available on your system.
2. Download `uv` a python package package manager, checkout more info [here](https://github.com/astral-sh/uv)

Then run the following commands:

```bash
uv run sync
```

```bash
uv run python main.py
```

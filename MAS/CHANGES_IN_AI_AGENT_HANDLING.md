# Changes in AI Agent Handling

Changes timestamp: 11.08.2025
## Changes taken

Due to some team members having issues accessing the OpenAI API, a support for the secondary AI platform was added. The application now fully supports response generation via the Groq platform and all of the models provided by it. 

In order to achieve this compatibility, the module `utils/openai_api.py` was slightly rewritten and renamed `utils/ai_api.py` to fit more with it's usage.

Usage of either OpenAI or Groq platform can be determined via the config file settings. Configfield `openai` was replaced with the `openai` field:

**Before**
```json
 "openai": {
    "primary_model": "gpt-4o",
    "fallback_model": "gpt-4o-mini",
    "max_tokens": 500,
    "temperature": 0.7,
    "max_retries": 3
    }
```

**After**
```json
  "ai_manager": {
    "client": "groq",
    "primary_model": "llama-3.3-70b-versatile",
    "fallback_model": "llama-3.1-8b-instant",
    "max_tokens": 500,
    "temperature": 0.7,
    "max_retries": 3
  },
```

Groq is accessesed via the OpenAI client, which means, that all other settings besides the primary and fallback models can be left as is. Other parts of the code were adjusted to fit the new implementation accordingly.

In order to use Groq, export a new env. variable `GROQ_API_KEY` with the API key provided after registering on the Groq website.

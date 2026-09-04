# API Keys

All credentials are read from environment variables or a local `.env` file.
Never hardcode keys in source files.

## Required for core operation

- `GEMINI_API_KEY` — Google Gemini (default LLM)

## Optional AI providers (used for consensus / fallback)

- `GROQ_API_KEY` — Groq
- `OPENROUTER_API_KEY` — OpenRouter

## Search providers

- `TAVILY_API_KEY` — Tavily Search
- `BRAVE_SEARCH_API_KEY` — Brave Search

## Optional

- `YOUTUBE_API_KEY` — YouTube Data API

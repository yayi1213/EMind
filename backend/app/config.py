import os

# Provider for optional LLM enrichment. Supported: 'openai'. Leave empty for template summaries.
PROVIDER = os.environ.get('PROVIDER', '').lower()

# OpenAI-specific settings
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', '')

# You can add more provider configs (Anthropic, Claude, etc.) and wiring here.

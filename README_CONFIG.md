# Configuration Guide

## Quick Start

Create a `.env` file in the project root and copy this template:

```env
# AI Configuration
AI_PROVIDER=gemini
AI_MODEL=gemini-2.5-flash
AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
AI_TEMPERATURE=0.7

# API Keys (pick one)
GOOGLE_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here

# Database Configuration
DATABASE_PATH=data/village.db
DATABASE_AUTO_CREATE=true

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=7861
SERVER_SHARE=false
SERVER_SHOW_ERROR=true

# Debug
DEBUG=false
```

Fill in your API key and you're ready to go!

---

## All Configuration Options

### Required
```env
# Pick ONE based on your AI provider:
GOOGLE_API_KEY=your_key_here      # For Gemini (default)
# OR
OPENAI_API_KEY=your_key_here      # For OpenAI
# OR
ANTHROPIC_API_KEY=your_key_here   # For Anthropic
```

### Optional - AI Settings
```env
AI_PROVIDER=gemini                    # Provider: gemini, openai, anthropic
AI_MODEL=gemini-2.5-flash            # Model name
AI_TEMPERATURE=0.7                   # 0.0 (focused) to 2.0 (creative)
AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

### Optional - Server Settings
```env
SERVER_HOST=0.0.0.0          # 0.0.0.0 (all) or 127.0.0.1 (local only)
SERVER_PORT=7861             # Port number
SERVER_SHARE=false           # true to create public link
SERVER_SHOW_ERROR=true       # Show errors in UI
```

### Optional - Database Settings
```env
DATABASE_PATH=data/village.db    # Database file location
DATABASE_AUTO_CREATE=true        # Auto-create if missing
DEBUG=false                       # Enable debug logging
```

---

## Common Use Cases

### Use OpenAI instead of Gemini
```env
AI_PROVIDER=openai
AI_MODEL=gpt-4
OPENAI_API_KEY=your_key_here
```

### Change the port
```env
SERVER_PORT=3000
```

### Store database elsewhere
```env
DATABASE_PATH=/custom/path/village.db
```

---

## Programmatic Access

```python
from cheapNPC.config import get_config

config = get_config()

# Access settings
model = config.ai.model_name
port = config.server.port
db_path = config.database.path
```

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| API key not found | Create `.env` file with your API key |
| Database not found | Check `DATABASE_PATH` or set `DATABASE_AUTO_CREATE=true` |
| Port already in use | Change `SERVER_PORT` to a different number |

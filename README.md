# CheapNPC

An AI-powered NPC trading system where intelligent agents generate NPCs, plan trades, and execute transactions autonomously in a fantasy village economy.

## Quick Start

### Prerequisites

- Python 3.12+
- UV package manager (recommended) or pip
- API key from one of: Google (Gemini), OpenAI, or Anthropic

### Installation

```bash
# Install dependencies
uv sync

# Or with pip
pip install -e .
```

### Configuration

Create a `.env` file in the project root with your configuration:

```env
# AI Provider (pick one)
AI_PROVIDER=gemini  # or 'openai' or 'anthropic'

# API Key (required - use the one matching your provider)
GOOGLE_API_KEY=your_key_here
# OR OPENAI_API_KEY=your_key_here
# OR ANTHROPIC_API_KEY=your_key_here

# Optional: Customize model and settings
AI_MODEL=gemini-2.5-flash
AI_TEMPERATURE=0.7
SERVER_PORT=7861
```

For complete configuration options, see [Configuration Guide](README_CONFIG.md).

### Run

```bash
uv run python run_dashboard.py
```

The web interface will be available at `http://localhost:7861`

## Usage

### First Launch

1. Open the landing page and click "Create World" to initialize NPCs
2. Wait for the world generation to complete
3. Refresh and access the dashboard

### Dashboard Features

- **🤖 Agent Operations**: Generate NPCs, create trading plans, execute trades
- **📊 Village Overview**: View all NPCs and their details
- **💰 Trade History**: Track completed transactions
- **📈 Inventory Changes**: Monitor inventory movements

### NPC Types

- **Crafter NPCs**: Blacksmiths, carpenters, brewers, miners, gatherers
- **Sales Person NPCs**: Store owners, merchants

## Project Structure

```
cheapNPC/
├── cheapNPC/
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   ├── agents/          # AI agents (generator, planner, trader)
│   ├── views/           # UI components (web dashboard)
│   └── infrastructure/  # Database and infrastructure
├── scripts/             # Utility scripts
└── data/               # Database and data files
```

## Configuration

### Basic Settings

- **Port**: Default 7861 (change via `SERVER_PORT` in `.env`)
- **Database**: `data/village.db` (auto-created)
- **AI Provider**: Gemini by default (change via `AI_PROVIDER`)

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_PROVIDER` | AI provider: `gemini`, `openai`, or `anthropic` | `gemini` |
| `AI_MODEL` | Model name | `gemini-2.5-flash` |
| `AI_TEMPERATURE` | Creativity level (0.0-2.0) | `0.7` |
| `SERVER_PORT` | Web server port | `7861` |
| `DATABASE_PATH` | Database file path | `data/village.db` |

See [README_CONFIG.md](README_CONFIG.md) for complete configuration guide.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port already in use | Set `SERVER_PORT` to a different number in `.env` |
| API key not found | Create `.env` file with your API key |
| Database errors | Click "Create World" on the landing page |
| Import errors | Run `uv sync` or `pip install -e .` |
| No NPCs showing | Ensure you've created a world first |

Need more help? Check the [full Configuration Guide](README_CONFIG.md) for advanced options.

## Advanced Configuration

For detailed configuration options including:
- Custom AI models
- Database settings
- Server configuration
- Debug mode

See the [Configuration Guide](README_CONFIG.md).
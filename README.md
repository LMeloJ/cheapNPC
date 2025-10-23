# CheapNPC - AI Agent Trading System

A sophisticated AI-powered NPC (Non-Player Character) trading system that simulates a fantasy village economy with intelligent agents that can generate NPCs, plan trades, and execute transactions autonomously.

## 🌟 Features

- **AI-Powered NPC Generation**: Create diverse NPCs with unique professions, skills, and inventories
- **Intelligent Trading System**: AI agents negotiate and execute trades between NPCs
- **Web Dashboard**: Modern Gradio-based interface for monitoring and controlling the system
- **Clean Architecture**: Well-structured codebase with separation of concerns
- **Database Management**: SQLite-based persistence with transaction history
- **Real-time Monitoring**: Track trades, inventory changes, and village economics

## 🏗️ Architecture

The project follows a clean architecture pattern with three main layers:

```
cheapNPC/
├── core/                    # Business logic and models
│   ├── models/             # Data models (NPCs, items, trading)
│   └── services/           # Business services
├── infrastructure/         # External concerns
│   ├── ai/agents/          # AI agents (generator, planner, trader)
│   └── database/           # Database layer
└── presentation/           # User interfaces
    ├── web/                # Gradio web dashboard
    └── cli/                # Command-line tools
```

## 📋 Prerequisites

- **Python 3.12+** (required by pyproject.toml)
- **UV Package Manager** (recommended) or pip
- **API Keys** for AI services (see Configuration section)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd cheapNPC

# Install dependencies using UV (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Environment Configuration

Create a `.env` file in the project root with your API keys:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional: LangSmith for tracing
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=cheapNPC
```

### 3. Launch the Application

```bash
uv run python run_dashboard.py
```

The web interface will be available at `http://localhost:7861`

## 🌐 Web Interface Guide

### Landing Page
When you first launch the application, you'll see the landing page that:
- Checks if the database exists and is properly configured
- Offers a "Create World" button to initialize the NPC village
- Provides status information about the system

### Dashboard Components

#### 🤖 Agent Operations
- **NPC Generator**: Create new NPCs with specific professions
  - Sales Person NPCs: Store owners, merchants
  - Crafter NPCs: Blacksmiths, carpenters, brewers, etc.
- **Trading Planner**: Generate trading plans between NPCs
- **Trade Executor**: Execute planned trades automatically

#### 📊 Village Overview
- View all NPCs in the village
- See their professions, skills, and economic status
- Monitor inventory counts and values

#### 💰 Trade History
- Track all completed transactions
- View trade details including participants, items, and prices
- Monitor economic activity over time

#### 📈 Inventory Changes
- Monitor inventory fluctuations
- Track item movements between NPCs
- Analyze economic trends

## 🛠️ Configuration Options

### Database Configuration

The system uses SQLite with the following default configuration:
- **Database Path**: `data/village.db`
- **Auto-creation**: Database and tables are created automatically
- **Schema**: Includes NPCs, items, inventory, and transaction tables

### AI Agent Configuration

The system uses multiple AI providers:
- **OpenAI**: Primary LLM for most operations
- **Anthropic**: Alternative LLM provider
- **Google Gemini**: Additional LLM option

### Web Interface Configuration

The Gradio interface runs with these defaults:
- **Host**: `0.0.0.0` (accessible from external networks)
- **Port**: `7861`
- **Theme**: Soft theme for better UX
- **Public Sharing**: Disabled by default (set `share=True` in app.py for public links)

## 🔧 Advanced Usage

### Command Line Tools

```bash
# Create the world programmatically
uv run scripts/create_world.py

#IMPLEMENT MORE CLI TOOLS

```

### Programmatic API Usage

```python
from cheapNPC.core.services import NPCService, TradingService
from cheapNPC.infrastructure.ai.agents import NPCAgent, NPCTradingAgent

# Create NPC service
npc_service = NPCService()

# Get all NPCs
npcs = npc_service.get_all_npc_summaries()

# Create an NPC agent
npc_agent = NPCAgent("NPC_Name")

# Execute trading
trading_agent = NPCTradingAgent()
result = await trading_agent.negotiate_trade("NPC1", "NPC2")
```

### Database Management

```python
from cheapNPC.infrastructure.database.migrations import setup_database, reset_database

# Setup database
setup_database()

# Reset database (WARNING: This deletes all data)
reset_database()
```

## 📊 Database Schema

The system uses four main tables:

1. **npcs**: Core NPC information (name, race, profession, skill, silver pieces)
2. **items**: Item catalog (unique item names)
3. **npc_inventory**: Junction table linking NPCs to items (quantity, price, quality)
4. **npc_transactions**: Transaction history (buyer, seller, item, quantity, price, timestamp)

## 🧪 Testing

```bash
# Run all tests
python run_tests.py

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

## 🐛 Troubleshooting

### Common Issues

1. **Database not found**: Run the "Create World" process from the landing page
2. **API key errors**: Ensure all required API keys are set in `.env`
3. **Port conflicts**: Change the port in `app.py` if 7861 is occupied
4. **Import errors**: Make sure you're running from the project root directory

### Debug Mode

Enable debug logging by setting environment variables:
```bash
export PYTHONPATH=/path/to/cheapNPC
export DEBUG=1
```

## 📚 Dependencies

Key dependencies include:
- **Gradio**: Web interface framework
- **OpenAI/Anthropic**: AI language models
- **SQLite**: Database persistence
- **Pydantic**: Data validation
- **Asyncio**: Asynchronous operations

See `pyproject.toml` for the complete dependency list.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the example usage in `examples/`
3. Examine the test cases for usage patterns
4. Create an issue in the repository

---

**Happy Trading!** 🎮✨
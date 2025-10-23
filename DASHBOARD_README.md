# 🤖 CheapNPC Agent Dashboard

A comprehensive web interface for managing NPCs and executing AI-powered trading operations in your D&D village simulation.

## 🚀 Quick Start

### Option 1: Using the Launcher Script
```bash
cd /home/leonardo/projects/cheapNPC
python run_dashboard.py
```

### Option 2: Direct Module Execution
```bash
cd /home/leonardo/projects/cheapNPC
python -m cheapNPC.presentation.web.dashboard
```

The dashboard will be available at: `http://localhost:7861`

## 🎯 Features

### 🤖 Agent Operations Tab
The main feature of the enhanced dashboard - interact with AI agents:

#### 🎭 NPC Generator Agent
- **Create SalesPerson NPCs**: Merchants, traders, and sales-focused characters
- **Create Crafter NPCs**: Blacksmiths, carpenters, tailors, and other crafters
- **Customizable Parameters**:
  - NPC Type: Choose between SalesPerson or Crafter
  - Profession: Specify profession (optional, AI will generate if not provided)
  - Quantity: Generate 1-5 NPCs at once
- **Real-time Output**: See generation progress and results
- **AI-Generated Content**: Each NPC comes with:
  - Unique name starting with profession letter
  - D&D race assignment
  - Profession-specific inventory (10+ items)
  - Appropriate skill level
  - Starting silver pieces

#### 📋 Trading Planner Agent
- **Intelligent Analysis**: AI analyzes all NPCs and their inventories
- **Optimal Pairing**: Creates 3-5 trading pairs based on:
  - Complementary professions
  - Supply and demand patterns
  - Economic viability
- **Real-time Planning**: See the planning process and results
- **Ready for Execution**: Generated plans are immediately available for trading

#### 💰 Trading Executor Agent
- **Plan Execution**: Takes trading plans and executes all trades
- **Database Updates**: Automatically updates NPC inventories and silver pieces
- **Transaction Recording**: Logs all successful trades
- **Error Handling**: Continues execution even if some trades fail
- **Detailed Results**: Shows which trades succeeded/failed and why

### 📊 Village Overview Tab
- **NPC Summary Table**: View all NPCs with key statistics
- **Real-time Data**: Silver pieces, trade counts, professions, inventory values
- **Interactive Selection**: Click any NPC row to view detailed information
- **Auto-refresh**: Keep data current with refresh button

### 💰 Trade History Tab
- **Individual NPC Focus**: Select any NPC to view their trading history
- **Pagination**: Load more trades as needed
- **Detailed Transactions**: See dates, roles, items, quantities, prices, and quality
- **Role Identification**: Clearly shows if NPC was buyer or seller

### 📈 Inventory Changes Tab
- **Before/After Comparison**: Compare initial vs current inventory
- **Visual Indicators**: 
  - 🟢 Green: Items/silver gained
  - 🔴 Red: Items/silver lost  
  - ⚪ White: No change
- **Comprehensive Tracking**: See how NPCs' wealth and items change over time

## 🎨 User Experience Features

### 🎯 Neat UX Design
- **Modern Interface**: Clean, professional Gradio interface with Soft theme
- **Color-coded Status**: Visual indicators for agent states (Ready/Running/Success/Error)
- **Responsive Layout**: Works well on different screen sizes
- **Intuitive Navigation**: Clear tabs and logical workflow

### 🔄 Real-time Feedback
- **Live Progress Updates**: See what each agent is doing in real-time
- **Status Indicators**: Know when agents are running vs ready
- **Output Display**: Detailed results from each agent operation
- **Error Handling**: Clear error messages and recovery options

### 🚀 Workflow Integration
- **Sequential Operations**: Natural flow from generation → planning → execution
- **State Management**: Plans are preserved between operations
- **Cross-tab Integration**: Click NPCs in overview to jump to detailed views
- **Auto-refresh**: Data stays current across all tabs

## 🔧 Technical Details

### 🏗️ Architecture
- **Service Layer Integration**: All operations use clean architecture
- **Async Agent Execution**: Non-blocking agent operations
- **Thread-safe Updates**: Safe concurrent access to database
- **Error Recovery**: Graceful handling of failures

### 🛠️ Dependencies
- **Gradio**: Web interface framework
- **Asyncio**: Async agent execution
- **Service Layer**: Clean data access
- **Agent Framework**: OpenAI agents integration

### 📁 File Structure
```
cheapNPC/
├── presentation/
│   └── web/
│       └── dashboard.py          # Enhanced dashboard with agents
├── infrastructure/
│   └── ai/
│       └── agents/
│           ├── generator_agent.py  # NPC generation
│           ├── planner_agent.py   # Trading planning
│           └── trader_agent.py    # Trade execution
└── run_dashboard.py              # Easy launcher script
```

## 🎮 Usage Workflow

### 1. Generate NPCs
1. Go to "Agent Operations" tab
2. Select NPC type (SalesPerson or Crafter)
3. Optionally specify profession
4. Choose quantity (1-5)
5. Click "Generate NPCs"
6. Watch real-time progress and results

### 2. Create Trading Plan
1. After generating NPCs, click "Create Trading Plan"
2. AI analyzes all NPCs and creates optimal pairings
3. Review the generated trading pairs
4. Plan is ready for execution

### 3. Execute Trades
1. Click "Execute Trades" to run the trading plan
2. Watch as all trades are processed
3. See detailed results of successful/failed trades
4. NPC inventories and silver pieces are updated

### 4. Review Results
1. Check "Village Overview" to see updated NPC statistics
2. Use "Trade History" to see individual transaction details
3. Use "Inventory Changes" to compare before/after states

## 🚨 Troubleshooting

### Database Not Found
If you see "Database not found" error:
1. Make sure you're in the project root directory
2. Check that `data/village.db` exists
3. Run NPC generation scripts first if needed

### Agent Errors
If agents fail to execute:
1. Check that environment variables are set (GOOGLE_API_KEY)
2. Ensure internet connection for AI API calls
3. Check console output for detailed error messages

### Port Conflicts
If port 7861 is in use:
1. The dashboard will show an error
2. Kill any existing Gradio processes
3. Or modify the port in `dashboard.py`

## 🎉 Enjoy Your AI-Powered Village!

The Enhanced CheapNPC Agent Dashboard provides a complete interface for managing your D&D village simulation. Create NPCs, plan trades, execute transactions, and watch your village economy evolve - all through an intuitive web interface powered by AI agents!

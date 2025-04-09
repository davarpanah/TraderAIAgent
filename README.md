# TradingAgent Dashboard
This project provides a comprehensive AI-driven trading dashboard powered by Streamlit and integrates various AI and machine learning tools to analyze market data, provide stock recommendations, and execute trading decisions. It also integrates with external APIs, including financial data sources and trading services, to facilitate real-time trading actions.

**Project Overview**
This application allows users to input stock symbols and get AI-driven market analysis and trading recommendations, including buy, sell, or hold actions. Once a recommendation is made, the user can approve or reject the action, which will update the trading status accordingly.

**Features**
    Market Analysis: Analyzes market data based on the user's query and provides recommendations on stock actions (buy, sell, hold).
    AI-Powered Recommendations: Utilizes machine learning models like Anthropic Claude to provide insights based on market conditions.
    Decision Approval: Users can approve or reject recommendations, which will trigger appropriate trading actions (buy/sell).
    Trading Control: Allows control over trading operations via external services and FastAPI endpoints.

**Getting Started**
To run this project locally, follow the instructions below:

**Prerequisites**
    Python 3.x
    Streamlit
    Boto3
    Requests
    FastAPI
    Langchain and related dependencies

**Setup**
    Clone the repository:
git clone https://github.com/your-repo/trading-agent-dashboard.git
cd trading-agent-dashboard

**Install the required Python dependencies:**
pip install -r requirements.txt
Set up your environment variables and configurations, including API keys for services like Alpaca and any other third-party APIs (i.e., Bedrock).
Run the application:
    For the Streamlit app:
streamlit run app.py
For the FastAPI app (if you're running the backend):
        uvicorn backend:app --reload

**Key Components**
1. TradingAgent Class (trading_aiagent.py)
The TradingAgent class provides methods for:
    Analyzing the market using a financial team API.
    Retrieving and updating trading status.
    Executing trading decisions based on analysis.
2. Streamlit Dashboard (app.py)
The Streamlit app allows users to:
    Input a stock symbol for market analysis.
    Display the analysis and trading recommendations.
    Approve or reject trading recommendations for execution.
3. FastAPI Backend (backend.py)
The FastAPI backend handles:
    Fetching and updating trading status.
    Running trading commands like buy/sell.
    Providing endpoints for external clients to interact with the trading bot.
4. AI Agent with Langchain (ai_agent.py)
The AIAgentFinanceTeamChain utilizes Langchain to integrate multiple tools:
    Yahoo Finance: Fetches financial data and news.
    DuckDuckGo Search: Gathers web insights to enrich analysis.

**API Endpoints**
The FastAPI backend exposes the following endpoints:
    GET /trading/status: Retrieves the current status of the trading bot, including trading settings.
    POST /trading/symbol: Updates the symbol being analyzed for trading.
    POST /trading/parameters: Updates trading parameters such as stop loss, take profit, and quantity.
    POST /trading/control: Controls trading actions such as buy and sell.
    POST /query: Queries the AI agent for market analysis and trading recommendations.

**Example Usage**
    Analyze Market:
        Input a stock symbol (e.g., "AAPL") and click Analyze.
        View the market analysis and the recommendation (e.g., BUY or SELL).
    Approve/Reject:
        If a recommendation is made, you can approve or reject the recommendation.
        Once approved, the relevant trading decision (buy/sell) will be executed.
    Trading Control:
        You can interact with the trading bot via the API to update symbols, change parameters, or execute buy/sell actions.

**Technologies Used**
    Streamlit: Frontend for displaying the trading dashboard.
    FastAPI: Backend API to control the trading bot and interact with external services.
    Boto3: AWS SDK used to interact with Amazon Bedrock services.
    Langchain: Framework to create and manage the AI agent.
    Alpaca: Trading broker API (simulated in this example).

**Contributing**
If you'd like to contribute to this project, feel free to fork the repository and create a pull request. Please ensure that your code is properly tested before submitting.

**License**
This project is licensed under the MIT License - see the LICENSE file for details.

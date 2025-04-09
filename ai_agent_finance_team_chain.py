import json
from fastapi import FastAPI, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore
from langchain.agents import initialize_agent, AgentType, Tool
from langchain_community.tools import DuckDuckGoSearchRun, YahooFinanceNewsTool # type: ignore
from langchain_aws import ChatBedrock # type: ignore
import logging
import uvicorn # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)    

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

class AIAgentFinanceTeamChain:
    def __init__(self):
        self.llm = ChatBedrock(
            model_id="anthropic.claude-3-5-sonnet-20241022-v2.0",
            model_kwargs={
                "max_tokens": 2000,
                "temperature": 0,
                "anthropic_version": "bedrock-2023-05-31"
            },
            #client_kwargs={"region_name": "us-east-1"}  # Ensure the region is correct
        )
        self.web_search_tool = Tool(
            name="DuckDuckGo Search",
            func=DuckDuckGoSearchRun().run,
            description="Use this tool to search the web for information."
        )
        self.yahoo_finance_tool = Tool(
            name="Yahoo Finance News",
            func=self.slfe_yahoo_finance_run, #YahooFinanceNewsTool().run,
            description="Use this tool to get the latest news from Yahoo Finance."
        )
        self.multi_agent = initialize_agent(
            [self.web_search_tool],#, self.yahoo_finance_tool],
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
    def slfe_yahoo_finance_run(self, query: str) -> dict:
        """
        Safely run the Yahoo Finance tool with error handling.
        """
        try:
            ticker = query.strip().split()[0].upper()
            if not ticker:
                raise ValueError("No ticker symbol provided.")
            return YahooFinanceNewsTool().run(ticker)
        except Exception as e:
            logger.error(f"Error in Yahoo Finance tool: {e}")
            return {"error": str(e)}
    def generate_prompt(self, query: str) -> str:
        """
        Generate a prompt for the agent based on the user query.
        """
        ticker = query.strip().split()[0].upper()
        if not ticker:
            raise ValueError("No ticker symbol provided.")
       
        return f"""
        You are a multi agent system designed to fetch financial data and web search results.
        Objectives: Provide a comprehensive response to the user's query by combining insights from Yahoo Finance and web search
        Instructions:
        1. Use Yahoo Finance to fetch financial data, stock prices, and company news.
        2. Use DuckDuckGo Search to gather real-time web search results.
        3. Combine the insights into a structured JSON response

        Required JS ON format:
        {{
            "symbol":"{ticker}",
            "web_insights":"KEY_FINDINGS_FROM_WEB",
            "financial_data"":"KEY_METRICS_FROM_YAHOO_FINANCE",
            "combined_analysis":"SYNTHESIZED_INSIGHTS",
            "recomendation": "BUY, SEL, or HOLD based on the analysis"
        }}
        Here is the user's query: {query}
        """
    
    def run_query(self, query: str) -> str:
        prompt = "ggggg"#self.generate_prompt(query)
        try:
            #response = self.multi_agent.run(prompt)
            return prompt#.strip()
        except Exception as e:
            logger.error(f"Error in agent execution: {e}")
            raise HTTPException(status_code=500, detail=str(e))

ai_agent_chain = AIAgentFinanceTeamChain()

@app.post("/query")
def query_agent(req: QueryRequest):
    try:
        response = ai_agent_chain.run_query(req.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

        

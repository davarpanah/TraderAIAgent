import streamlit as st
import boto3
import json
import requests
from typing import Dict, Any

bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

class TradingAgent:
    def __init__(self):
        self.finance_team_utl = "http://localhost:8000/query"
        self.trdading_status_url = "http://localhost:8000/trading/status"
        self.trading_control_url = "http://localhost:8000/trading/control"

    def analyze_market(self, query:str) -> str:
        try:
            response = requests.post(self.finance_team_utl, headers = {"Content-Type":"application/json"}, json={"query": query})

            return response.json().get("response", "No response received")
        except Exception as e:
            return f"Error in analysis_market: {str(e)}"

    def get_market_analysis(self, symbol: str) -> Dict[str, Any] :
        try:
            response = requests.post(self.finance_team_utl, headers = {"Content-Type":"application/json"}, json = {"user_query": symbol})
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error in API call: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            st.error(f"Error in API call: {e}")
            return None
        except Exception as e:
            st.error(f"Error in API call: {e}")
            return None
        
    def get_trading_status(self) -> Dict[str, Any]:
        try:
            response = requests.get(self.trdading_status_url)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error in API call: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            st.error(f"Error in API call: {e}")
            return None
        except Exception as e:
            st.error(f"Error in API call: {e}")
            return None 
        
    def update_trading_service(self, action: str, symbol: str = None) -> Dict[str, Any]:
        payload = {"action": action, "symbol": symbol}
        try:
            response = requests.post(self.trading_control_url, json=payload, headers = {"Content-Type":"application/json"})
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error in API call: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            st.error(f"Error in API call: {e}")
            return None
        except Exception as e:
            st.error(f"Error in API call: {e}")
            return None
    
    def analyze_with_bedrock(self, market_data: Dict[str, Any], trading_status: Dict[str, Any]) -> str:
        {json.dumps(market_data, indent=2)}
        {json.dumps(trading_status, indent=2)}
        prompt = f"Analyze the market data and trading status to provide a summary of the market and trading status. Use the following data:\n\nMarket Data:\n{json.dumps(market_data, indent=2)}\n\nTrading Status:\n{json.dumps(trading_status, indent=2)}\n\nAssistant:"
        try:
            response = bedrock_runtime.invoke_model(
                modelId="anthropic.claude-v2",
                body=json.dumps({
                    "prompt": f"\n\nHuman: Analyze the market data and trading status to provide a summary of the market and trading status. Use the following data:\n\nMarket Data:\n{json.dumps(market_data, indent=2)}\n\nTrading Status:\n{json.dumps(trading_status, indent=2)}\n\nAssistant:",
                    "max_tokens": 1000,
                    "messages":{"role":"user","content":prompt}
                }),
                contentType="application/json",
                accept="application/json"
            )
            response_body = json.loads(response.get("body").read())
            return response_body['content'][0]['text']
        except Exception as e:
            st.error(f"Error in API call: {e}")
            return None
        
    def execute_decision(self, decision: str, symbol: str) -> Dict[str, Any]:
        if decision.lower() not in ["buy", "sell"]:
            return {"message": "Invalid decision. Must be 'buy' or 'sell'."}
        return self.update_trading_service(decision.lower(), symbol)
    
def main():
    st.title = "AI Trading Dashboard Trading Agent"	
    if 'market_data' not in st.session_state:
        st.session_state.market_data = None
    if 'trading_status' not in st.session_state:
        st.session_state.trading_status = None
    if 'recomendation' not in st.session_state:
        st.session_state.recommendation = None	
    if 'decision' not in st.session_state:
        st.session_state.decision = None
    if 'show_approval' not in st.session_state:
        st.session_state.show_approval = False
    
    agent = TradingAgent()
    symbol = st.text_input("Enter symbol for analysis", "")
    if st.button("Run Analyze"):
        with st.spinner("Analyzing..."):
            st.session_state.market_data = agent.get_market_analysis(symbol)
            st.session_state.Trading_status = agent.get_trading_status()
            if st.session_state.market_data and st.session_state.Trading_status:
                st.session_state.recommandation = agent.analyze_with_bedrock(st.session_state.market_data, st.session_state.Trading_status)
            if "START" in st.session_state.recommandation or "STOP" in st.session_state.recommandation or "MAINTAIN" in st.session_state.recommandation:
                st.session_state.decision = ("START" if "START" in st.session_state.recommandation else "STOP" if "STOP" in st.session_state.recommandation else "MAINTAIN")
                st.session_state.show_approval = True

    if st.session_state.trading_status:
        st.subheader("Trading Status")
        st.json(st.session_state.trading_status)

    if st.session_state.market_data:
        st.subheader("Market Data")
        st.json(st.session_state.market_data)

    if st.session_state.recommendation:
        st.subheader("Recommendation")
        st.info(st.session_state.recommendation)

    if st.session_state.show_approval and st.session_state.recommandation in ["START", "STOP"]:
        col1, col2 = st.columns(2)
        with col1:
            st.button('Approve')
            with st.spinner('Approving...'):
                response = agent.update_trading_state(st.session_state.decission.lower(), symbol) 
                if response and "message" in response: 
                    st.success(response['message']) 
                    with st.spinner('Updating trading status...'):
                        new_status = agent.get_trading_status()
                        if new_status:
                            st.session_state.trading_status = new_status
                            st.subheader("Updated Trading Status")
                            st.json(st.session_state.trading_status)
                else:
                    st.error(f"Error: {response['error']}")
        with col2:
            st.button('Reject')
            st.info(f"Decision: {st.session_state.decision}")
            st.session_state.approval_status = "Rejected"
    elif st.session_state.decision == "MAINTAIN":
        st.info('Maintaining current trading state')

if __name__ == "__main__":
    main()

    
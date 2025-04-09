import streamlit as st
from trading_aiagent import TradingAgent 

def main():   
    st.title('TradingAgent Dashboard')
    agent = TradingAgent()
    if 'analysis' not in st.session_state:
        st.session_state.analysis = None
    if 'recommandation' not in st.session_state:
        st.session_state.recommandation = None
    if 'approval_status' not in st.session_state:
        st.session_state.approval_status = None

    user_query = st.text_input('Enter your query:', value='')
    if st.button('Analyze'):
        with st.spinner('Analyzing...'):
            analysis = agent.analyze_market(user_query)
            st.session_state.analysis = analysis
            
            if "buy" in analysis or "sell" in analysis or "hold" in analysis:
                st.session_state.recommandation = ("BUY" if "buy" in analysis else "SELL" if "sell" in analysis else "HOLD")
            else:
                st.session_state.approval_status = None	


    if st.session_state.analysis:
        st.subheader('Analysis:')
        st.text(st.session_state.analysis)

    if st.session_state.recommandation:
        st.subheader('Recommandation:')
        st.info(st.session_state.recommandation)

        if st.session_state.recommandation in ["BUY", "SELL"]:
            st.warning(f"Do you accept recommandation to {st.session_state.recommandation} the stock?")
            col1, col2 = st.columns(2)
            with col1:
                st.button('Approve')
                with st.spinner('Approving...'):
                    response = agent.execute_decission(st.session_state.recommandation, user_query) 
                    if "error" in response:   
                        st.session_state.approval_status = f"Error: {response['error']}"
                    else:
                        st.session_state.approval_status = "Approved"
            with col2:
                st.button('Reject')
                st.session_state.approval_status = "Rejected"
    if st.session_state.approval_status:
        st.subheader('Approval Status:')
        st.info(st.session_state.approval_status)
        
if __name__ == "__main__":
    main()
    

import json
from fastapi import FastAPI, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore
from lumibot.brokers import Alpaca
from lumibot.strategies import Strategy
from lumibot.traders import Trader
from config import ALPACA_CONFIG
from typing import Optional
import logging
import uvicorn # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 

app = FastAPI()

class SwingHigh(Strategy):
    sleeptime = "1M"
    symbol =  "SPY"
    Quantity = 10
    stop_loss_pct = 0.995
    take_profit_pct = 1.015
    data = []
    order_number = 0
    is_trading_enable = False

    def on_trading_iteration(self):

        if not self.is_trading_enable:
            return
        
        entity_price = self.fetch_latest_price(self.symbol)
        self.log_message(f"Symbol: {self.symbol}, Position: {self.get_position(self.symbol)}")
        self.data.append(self.fetch_latest_price(self.symbol))

        if len(self.data)>3:
            temp = self.data[-3:]
            if temp[-1]>temp[1]>temp[0]:
                self.log_message(f"last 3 points for {self.symbol}: {temp}")
                order = self.create_order(
                    self.symbol,
                    self.Quantity,
                    "buy",
                    type="bracket",
                    take_profit_price=entity_price * self.take_profit_pct,
                    stop_loss_price=entity_price * self.stop_loss_pct
                )
                self.submit_order(order)
                self.order_number += 1
                if self.order_number == 1:
                    self.log_message(f"Enter price for {self.symbol}:{temp[-1]}")
                    entity_price = temp[-1]
            position = self.get_position(self.symbol)
            if position:
                if self.data[-1] < entity_price * self.stop_loss_pct:
                    self.sell_all()
                    self.order_number = 0
                    self.log_message(f"Stop loss triggered for {self.symbol}")
                elif self.data[-1] >= entity_price * self.take_profit_pct:
                    self.sell_all()
                    self.order_number = 0
                    self.log_message(f"Take profit triggered for {self.symbol}")

    def before_market_closes(self):
        self.sell_all()
        self.is_trading_enable = False

    def update_symbol(self, symbol: str) -> bool:
        try:
            if get_last_price(symbol):
                if self.get_position(symbol):
                    self.sell_all()
                self.symbol = symbol
                self.data = []
                self.order_number = 0
                return True
            return False
        except Exception as e:
            self.log_message(f"Error updating symbol: {e}")
            return False
        
    def update_parameters(self, quantity: Optional[int] = None, stop_loss_pct: Optional[float] = None, take_profit_pct: Optional[float] = None):
        try:
            if quantity is not None and quantity > 0:
                self.Quantity = quantity
            if stop_loss_pct is not None and 0 < stop_loss_pct < 1:
                self.stop_loss_pct = stop_loss_pct
            if take_profit_pct is not None and take_profit_pct > 1:
                self.take_profit_pct = take_profit_pct
            return True
        except Exception as e:
            self.log_message(f"Error updating parameters: {e}")
            return False
trader = None
strategy = None

def initialize_trading_bot(): 
    global trader, strategy
    try:
        broker = Alpaca(ALPACA_CONFIG)
        strategy = SwingHigh(broker=broker)
        trader = Trader()
        trader.add_strategy(strategy)
        return True
    except Exception as e:
        logger.error(f"Error initializing trading bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
initialize_trading_bot()

class symbolRequest(BaseModel):
    symbol: str

class parametersRequest(BaseModel):
    quantity: Optional[int] = None
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None

class controlRequest(BaseModel):
    action: str
    symbol: Optional[str] = None    

@app.get("/trading/status")

def get_trading_status():
    try:
        global strategy
        if strategy is None:
            raise HTTPException(status_code=500, details="Trading bot is not initialized.")
        return {
            "status": "Trading bot is running.",
            "symbol": strategy.symbol,
            "quantity": strategy.Quantity,
            "stop_loss_pct": strategy.stop_loss_pct,
            "take_profit_pct": strategy.take_profit_pct,
            "is_trading_enable": strategy.is_trading_enable
        }
    except Exception as e:
        logger.error(f"Error getting trading status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trading/symbol")
def update_symbol(request: symbolRequest):
    try:
        global strategy
        if strategy is None:
            raise HTTPException(status_code=500, details="Trading bot is not initialized.")
        if strategy.update_symbol(request.symbol.upper()):
            return {"message": f"Symbol updated to {request.symbol}"}
        else:
            raise HTTPException(status_code=400, detail="Failed to update symbol.")
    except Exception as e:
        logger.error(f"Error updating symbol: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/trading/parameters")
def update_parameters(request: parametersRequest):
    try:
        global strategy
        if strategy is None:
            raise HTTPException(status_code=500, details="Trading bot is not initialized.")
        if strategy.update_parameters(request.quantity, request.stop_loss_pct, request.take_profit_pct):
            return {"message": "Parameters updated successfully."}
        else:
            raise HTTPException(status_code=400, detail="Failed to update parameters.")
    except Exception as e:
        logger.error(f"Error updating parameters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trading/control")
def control_trading(request: controlRequest):
    try:
        global strategy
        if strategy is None:
            if not initialize_trading_bot():
                raise HTTPException(status_code=500, details="Trading bot is not initialized.")
        action = request.action.lower()
        symbol = request.symbol.upper() if request.symbol else None

        if action not in ["buy" , "sell"]:
            raise HTTPException(status_code=400, detail="Invalid action.")

        if not symbol.isalnum() or len(symbol) > 5:
            raise HTTPException(status_code=400, detail="Invalid action.")

        if action == "buy":
            if strategy.symbol != symbol:
                if not strategy.update_symbol(symbol):
                    raise HTTPException(status_code=400, detail="Invalid action.")
            try:
                order = strategy.create_order(
                    symbol,
                    strategy.Quantity,
                    "buy",
                    type="bracket",
                    take_profit_price=entity_price * strategy.take_profit_pct,
                    stop_loss_price=entity_price * strategy.stop_loss_pct
                )
                strategy.submit_order(order)
                return {"message": "Trading enabled."}
            except Exception as e:
                logger.error(f"Error controlling trading: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        elif action == "sell":
            if strategy.symbol != symbol:
                if not strategy.update_symbol(symbol):
                    raise HTTPException(status_code=400, detail="Invalid action.")

            try:
                strategy.sell_all()
                return {"message": "Trading enabled."}
            except Exception as e:
                logger.error(f"Error controlling trading: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error controlling trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/health")
def health_check():
    return {"status": "OK"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


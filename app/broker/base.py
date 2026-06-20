from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class OrderRequest:
    symbol:      str
    side:        str          # buy / sell
    qty:         float
    order_type:  str = "market"   # market / limit / stop
    limit_price: Optional[float] = None
    stop_price:  Optional[float] = None
    time_in_force: str = "gtc"

@dataclass
class OrderResult:
    order_id:   str
    symbol:     str
    side:       str
    qty:        float
    status:     str
    filled_qty: float = 0.0
    filled_avg_price: float = 0.0
    broker:     str = ""

class BrokerBase(ABC):

    @abstractmethod
    async def place_order(self, order: OrderRequest) -> OrderResult: pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool: pass

    @abstractmethod
    async def get_positions(self) -> list: pass

    @abstractmethod
    async def get_account(self) -> dict: pass

    @abstractmethod
    async def get_price(self, symbol: str) -> float: pass

    @abstractmethod
    async def get_candles(self, symbol: str, timeframe: str, limit: int) -> list: pass

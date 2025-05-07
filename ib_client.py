# ib_trade_engine/ib_client.py
from ib_insync import IB

class IBClient:
    """Thin wrapper around ib_insync.IB with auto‑connect."""
    def __init__(self, host: str = "127.0.0.1", port: int = 7497, client_id: int = 17):
        self.host, self.port, self.client_id = host, port, client_id
        self.ib = IB()

    def connect(self):
        if not self.ib.isConnected():
            self.ib.connect(self.host, self.port, clientId=self.client_id, readonly=False)

    def disconnect(self):
        if self.ib.isConnected():
            self.ib.disconnect()

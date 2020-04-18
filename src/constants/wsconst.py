import src.constants.ccxtconst as ccxtconst

WEBSOCKET_API_ENDPOINT_COINCHECK = "wss://ws-api.coincheck.com/"
WEBSOCKET_API_ENDPOINT_LIQUID = "wss://ws-api.coincheck.com/"

WEBSOCKET_ENDPOINTS = {
    ccxtconst.ExchangeId.COINCHECK: WEBSOCKET_API_ENDPOINT_COINCHECK,
    ccxtconst.ExchangeId.LIQUID: WEBSOCKET_API_ENDPOINT_LIQUID
}

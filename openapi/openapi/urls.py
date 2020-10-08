from django.contrib import admin
from django.urls import path, include
from .views import views_orderbook
from .views import views_ticker
from .views import views_product_currency_code
from .views import views_assets
from .views import views_feerate
from .views.history import views_orderhistory
from .views.history import views_trade_history
from .views.history import views_transaction_history
from .views.order import views_market
from .views.order import views_stop
from .views.order import views_limit
from .views.order import views_stop_cancel
from .views.order import views_limit_cancel
from .views import views_non_trading_order
from .views import views_candles

urlpatterns = [
    ### PUBLIC API (require key -> API KEY) ###
    path('history/transaction', views_transaction_history.TransactionHistory.as_view()),  # 체결내역
    path('ticker', views_ticker.Ticker.as_view()),  # Ticker
    path('orderbook', views_orderbook.OrderBook.as_view()),  # Order Book
    path('currency/code', views_product_currency_code.ProductCurrencyCode.as_view()),  # 상품 코드
    path('candles', views_candles.CandlesView.as_view()),  # OHLC

    ### PRIVATE API (require key -> API KEY, SECRET KEY)
    path('feerate', views_feerate.FeerateView.as_view()),  # 수수료 정보
    path('assets', views_assets.Assets.as_view()),  # 내 자산
    path('history/order', views_orderhistory.OrderHistory.as_view()),  # 주문 내역
    path('history/trade', views_trade_history.TradeHistory.as_view()),  # 거래 내역
    path('order/market', views_market.OrderMarketSend.as_view()),  # 시장가 주문
    path('order/stop', views_stop.StopOrderView.as_view()),  # 예약가 주문
    path('order/limit', views_limit.OrderLimitSend.as_view()),  # 지정가 주문
    path('order/stop/cancel', views_stop_cancel.StopOrderCancelView.as_view()),  # 예약가 주문 취소
    path('order/limit/cancle', views_limit_cancel.OrderCancelSend.as_view()),  # 지정가 주문 취소
    path('nontrade', views_non_trading_order.NonTradingOrder.as_view()),
]

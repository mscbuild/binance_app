import asyncio
import json
import websockets
from plyer import notification
from datetime import datetime, timedelta

last_alerts = {}
ALERT_COOLDOWN = timedelta(minutes=10)
THRESHOLD_PERCENT = 3.0

async def monitor_usdt_pairs():
    url = "wss://stream.binance.com:9443/ws/!ticker@arr"
    print(f"🚀 Мониторинг USDT-пар запущен (порог: {THRESHOLD_PERCENT}%)")

    try:
        async with websockets.connect(url, ping_interval=20, ping_timeout=20) as websocket:
            while True:
                message = await websocket.recv()
                data = json.loads(message)

                for ticker in data:
                    symbol = ticker['s']

                    if symbol.endswith('USDT'):
                        change_percent = float(ticker['P'])
                        last_price = float(ticker['c'])

                        if abs(change_percent) >= THRESHOLD_PERCENT:
                            now = datetime.now()

                            if symbol not in last_alerts or (now - last_alerts[symbol]) > ALERT_COOLDOWN:

                                direction = "📈 Height" if change_percent > 0 else "📉 Fall"
                                alert_title = f"Binance Alert: {symbol}"
                                alert_message = f"{direction}: {change_percent}%\nЦена: {last_price}"

                                notification.notify(
                                    title=alert_title,
                                    message=alert_message,
                                    app_name="Binance Monitor",
                                    timeout=5
                                )

                                last_alerts[symbol] = now
                                print(f"[{now.strftime('%H:%M:%S')}] 🔔 {symbol} {change_percent}%")

    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(monitor_usdt_pairs())
    except KeyboardInterrupt:
        print("\n⛔ Monitoring has been stopped.")

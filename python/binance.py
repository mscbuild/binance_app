import asyncio
import json
import websockets
from plyer import notification
from datetime import datetime, timedelta

# Dictionary for storing the last notification time for each coin
# To avoid spamming notifications too often
last_alerts = {}
ALERT_COOLDOWN = timedelta(minutes=10)  # Repeated notification no earlier than in 10 minutes
THRESHOLD_PERCENT = 3.0                 # Response threshold in percent

async def monitor_usdt_pairs():
    url = "wss://://stream.binance.com"
    print(f"🚀 USDT pair monitoring has been launched. (threshold: {THRESHOLD_PERCENT}%)")

    try:
        async with websockets.connect(url) as websocket:
            while True:
                message = await websocket.recv()
                data = json.loads(message)

                for ticker in data:
                    symbol = ticker['s']
                    
                    # Filter only USDT pairs
                    if symbol.endswith('USDT'):
                        change_percent = float(ticker['P'])
                        last_price = float(ticker['c'])
                        
                        # Checking the alert condition
                        if abs(change_percent) >= THRESHOLD_PERCENT:
                            now = datetime.now()
                            
                            # We check if we have waited for a pause (cooldown) for this coin
                            if symbol not in last_alerts or (now - last_alerts[symbol]) > ALERT_COOLDOWN:
                                
                                # Forming the notification text
                                direction = "📈 Рост" if change_percent > 0 else "📉 Падение"
                                alert_title = f"Binance Alert: {symbol}"
                                alert_message = f"{direction}: {change_percent}%\nЦена: {last_price}"

                                # Sending a system notification
                                notification.notify(
                                    title=alert_title,
                                    message=alert_message,
                                    app_name="Binance Monitor",
                                    timeout=5  # How many seconds does the window hang
                                )

                                # We are updating the time of the last alert
                                last_alerts[symbol] = now
                                print(f"[{now.strftime('%H:%M:%S')}] 🔔 Notification: {symbol} {change_percent}%")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Installation: pip install websockets plyer
    try:
        asyncio.run(monitor_usdt_pairs())
    except KeyboardInterrupt:
        print("\nMonitoring has been stopped..")

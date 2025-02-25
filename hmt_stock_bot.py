import requests
from bs4 import BeautifulSoup
import time

# HMT Watches product page
URL = "https://www.hmtwatches.in/product_details?id=eyJpdiI6IjVJMzhtN3R3bkVyUjhzUzFJOUFJMkE9PSIsInZhbHVlIjoiQkFHL0c4cElNNTF2RTcxcWI1MjA0QT09IiwibWFjIjoiNTMzZWQ1NjNjZDA1Zjc2NmE0M2U3MjdhMzk3ODI2NGUwZDUzMmZhMmIwNTZkYTI2YmUzOTRjMzc2NDc1Y2ZiYyIsInRhZyI6IiJ9"
TELEGRAM_BOT_TOKEN = "7473643871:AAFwMekrLDsamFZ0WOQczjIUOaFfE3wiVoI"
TELEGRAM_CHAT_ID = "1755005210"

# Define headers to mimic a real browser
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/114.0.0.0 Safari/537.36")
}

def check_stock():
    """Checks if the product is available by looking for 'add to cart' text."""
    try:
        response = requests.get(URL, headers=HEADERS)
    except Exception as e:
        print(f"Request failed: {e}")
        return "ERROR"

    if response.status_code != 200:
        print(f"Failed to load page! Status Code: {response.status_code}")
        return "ERROR"

    soup = BeautifulSoup(response.text, 'html.parser')

    # Try to find the button element
    button = soup.find('a', class_="add-to-cart btn btn-default")
    
    # If the button isn't found, try with the extra class (if any)
    if not button:
        button = soup.find('a', class_="add-to-cart btn btn-default update_cart_product")

    if button:
        # Get the text inside the button, converted to lowercase for a case-insensitive comparison
        button_text = button.get_text(strip=True).lower()
        return button_text
    else:
        return "NOT FOUND"

def send_telegram_alert(message):
    """Sends a Telegram notification."""
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(telegram_url, data=payload)
        print("Telegram alert sent!")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

# Track the last known stock status (initialize to "notify me")
last_status = "notify me"

while True:
    current_status = check_stock()
    print(f"Current Status: {current_status}")

    # Check if the current status contains "add to cart" (case-insensitive)
    if "add to cart" in current_status and "add to cart" not in last_status:
        send_telegram_alert(f"🎉 The product is now in stock! Buy here: {URL}")
        last_status = "add to cart"
    elif "notify me" in current_status:
        # Reset the status if it changes back
        last_status = "notify me"

    time.sleep(120)  # Check every 5 minutes
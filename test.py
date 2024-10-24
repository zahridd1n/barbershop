import requests

# Sizning bot tokeningiz
BOT_TOKEN = "8033657841:AAHHpzPug1FdMZ9rhDLoEW6DA0PQKo7jojQ"

# getUpdates so'rovini yuborish
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)

# Javobni chop etish
print(response.json())  # Javobni chop etish
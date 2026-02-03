import requests

def send_webhook(url: str, payload: dict):
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Webhook sent successfully to {url} with payload: {payload}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send webhook to {url}: {e}")
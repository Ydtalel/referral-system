import requests
from decouple import config

HUNTER_API_URL = "https://api.hunter.io/v2/email-verifier"
API_KEY = config('HUNTER_API_KEY')


def verify_email(email):
    """
    Проверяет валидность указанного email-адреса с помощью Hunter API
    """
    params = {
        'email': email,
        'api_key': API_KEY
    }
    try:
        response = requests.get(HUNTER_API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return

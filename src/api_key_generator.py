import secrets
API_KEY_LENGTH = 32
api_key = secrets.token_urlsafe(API_KEY_LENGTH)
print(api_key)

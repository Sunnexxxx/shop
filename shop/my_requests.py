import requests

url = 'http://127.0.0.1:8000/api/v3/cart/'
headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE3Njc1MzkyLCJpYXQiOjE3MTc2NzUwOTIsImp0aSI6IjBhYjY3MDY4ZGIxZjRhM2E4OGE4NzRmMmU3ZjBjYTk0IiwidXNlcl9pZCI6MX0.Tp-6uiNKE1uCVYtHzkz2_kTL2mEQqm5M4ZDty1NCzHc',
}

response = requests.get(url, headers=headers)

print(f"Status code: {response.status_code}")
print(response.text)

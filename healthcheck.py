import requests

url = "http://localhost:5000/healthcheck"
resp = requests.get(url)
resp.raise_for_status()
print("Healthcheck succeeded: container healthy")

import requests

url = "https://api.deepseek.com/user/balance"

payload={}
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer sk-2ded84ccdfc342e68158539be2af8ad3'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
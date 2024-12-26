import json
import requests

# LinkedIn API credentials
client_id = "86bu3fgnz7dthc"
client_secret = "WPL_AP1.9qgvrCtGOqN0IPoy.tVFNlg=="

# Get access token
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
access_token_url = "https://www.linkedin.com/oauth/v2/accessToken"
access_data = {'grant_type':'client_credentials','client_id': client_id, 'client_secret' : client_secret }

response = requests.post(access_token_url, headers=headers, data=access_data)
data = json.loads(response.text)
print(data)

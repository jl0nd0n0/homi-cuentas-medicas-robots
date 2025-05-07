import requests

# URL to your PHP endpoint
url = 'http://yourdomain.com/download.php'

# Send GET request
response = requests.get(url, stream=True)

# Save the ZIP file locally
with open('downloaded_file.zip', 'wb') as f:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)
print("ZIP file downloaded successfully.")
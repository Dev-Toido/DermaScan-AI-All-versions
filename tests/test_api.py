import requests
import numpy as np
import cv2
import base64
import sys

# Create dummy image
img = np.zeros((400, 600, 3), dtype=np.uint8)
cv2.rectangle(img, (200, 100), (400, 300), (0, 0, 255), -1) # fake red lesion
cv2.imwrite('dummy.jpg', img)

url = 'http://localhost:8000/api/analyze'
files = {'file': ('dummy.jpg', open('dummy.jpg', 'rb'), 'image/jpeg')}
data = {'age': '50', 'sex': 'Female', 'site': 'Anterior torso', 'demo_mode': 'false'}

try:
    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        res = response.json()
        print("Success!")
        if res.get('heatmap'):
            print("Heatmap returned! Length:", len(res['heatmap']))
        else:
            print("ERROR: Heatmap is None!")
    else:
        print("API Error:", response.status_code, response.text)
except Exception as e:
    print("Request failed:", e)

Python 3.13.2 (tags/v3.13.2:4f8bb39, Feb  4 2025, 15:23:48) [MSC v.1942 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import Message

import requests
import base64

... 
... class ImageUrlToBase64(Component):
...     display_name = "Image URL to Base64 (Raw)"
...     description = "Fetches an image from a URL and returns raw Base64 only"
...     icon = "image"
... 
...     inputs = [
...         MessageTextInput(
...             name="image_url",
...             display_name="Image URL",
...             required=True,
...         ),
...     ]
... 
...     outputs = [
...         Output(
...             display_name="Base64 Output",
...             name="base64_output",
...             method="convert_to_base64",
...         ),
...     ]
... 
...     def convert_to_base64(self) -> Message:
...         try:
...             image_url = self.image_url.strip()
... 
...             headers = {
...                 "User-Agent": "Mozilla/5.0"
...             }
... 
...             response = requests.get(image_url, headers=headers, timeout=10)
...             response.raise_for_status()
... 
...             # ✅ Only raw base64
...             encoded_string = base64.b64encode(response.content).decode("utf-8")
... 
...             return Message(text=encoded_string)
... 
...         except Exception as e:

from langflow.custom import Component
from langflow.inputs import SecretStrInput, MessageTextInput, DropdownInput
from langflow.io import Output
from langflow.schema import Message
from groq import Groq
import base64
import json
import re


class GroqVisionBase64Component(Component):
    display_name = "Groq Vision (Pure 2D Array)"
    description = "Returns ONLY raw 2D JSON array"
    icon = "Groq"

    inputs = [
        SecretStrInput(
            name="groq_api_key",
            display_name="Groq API Key",
            required=True,
        ),
        MessageTextInput(
            name="base64_image",
            display_name="Base64 Image Data",
            required=True,
        ),
        MessageTextInput(
            name="prompt",
            display_name="Text Prompt",
            required=True,
        ),
        DropdownInput(
            name="model",
            display_name="Model",
            options=[
                "meta-llama/llama-4-scout-17b-16e-instruct",
                "meta-llama/llama-4-maverick-17b-128e-instruct"
            ],
            required=True,
        ),
        DropdownInput(
            name="image_type",
            display_name="Image Type",
            options=[
                "image/jpeg",
                "image/png",
                "image/webp"
            ],
            value="image/jpeg",
        )
    ]

    outputs = [
        Output(display_name="2D Array Output", name="response", method="process_image"),
    ]

    #  Improved JSON extractor (array OR object)
    def extract_json(self, text: str):
        # Remove markdown wrappers
        text = re.sub(r"```json", "", text)
        text = re.sub(r"```", "", text)

        # Try extract array first
        array_match = re.search(r"\[\s*\[.*?\]\s*\]", text, re.DOTALL)
        if array_match:
            return array_match.group(0)

        # Fallback to object extraction
        object_match = re.search(r"\{.*\}", text, re.DOTALL)
        if object_match:
            return object_match.group(0)

        return None

    def process_image(self) -> Message:
        try:
            model = getattr(self, "model", None)
            if not model:
                return Message(text="[]")

            client = Groq(api_key=self.groq_api_key)

            base64_data = self.base64_image.strip()

            # Remove prefix if present
            if base64_data.startswith("data:"):
                base64_data = base64_data.split(",", 1)[1]

            # Validate base64
            base64.b64decode(base64_data)

            image_url = f"data:{self.image_type};base64,{base64_data}"

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": self.prompt + "\n\nReturn ONLY a raw 2D JSON array like [[\"A\",\"B\"],[\"C\",\"D\"]]. No object wrapper. No explanation. No markdown."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ]

            chat_completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
                max_tokens=2048,
            )

            raw_output = chat_completion.choices[0].message.content

            extracted_json = self.extract_json(raw_output)

            if not extracted_json:
                return Message(text="[]")

            parsed = json.loads(extracted_json)

            # If model returned {"grid": [...]}
            if isinstance(parsed, dict) and "grid" in parsed:
                return Message(text=json.dumps(parsed["grid"]))

            # If model already returned 2D array
            if isinstance(parsed, list):
                return Message(text=json.dumps(parsed))

            # Fallback
            return Message(text="[]")

        except Exception:
            return Message(text="[]")

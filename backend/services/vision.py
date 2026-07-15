import base64
import json
import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def extract_invoice(image_path: str):

    with open(image_path, "rb") as image:
        image_data = base64.b64encode(
            image.read()
        ).decode()

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": """
You are an invoice extraction assistant.

Extract the invoice and return ONLY JSON.

Format:

{
  "vendor":"",
  "invoice_number":"",
  "invoice_date":"",
  "currency":"",
  "subtotal":0,
  "tax":0,
  "total":0,
  "confidence":0.95
}
"""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type":"text",
                        "text":"Extract this invoice."
                    },
                    {
                        "type":"image_url",
                        "image_url":{
                            "url":f"data:image/png;base64,{image_data}"
                        }
                    }
                ]
            }
        ]
    )

    return json.loads(
        response.choices[0].message.content
    )
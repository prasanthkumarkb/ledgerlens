import base64
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq
from core.logger import logger

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing in .env file")

client = Groq(api_key=OPENAI_API_KEY)

# models = client.models.list()

# for model in models.data:
#     print(model.id)


def extract_invoice(image_path: str) -> dict:
    """
    Extract invoice details using OpenAI Vision.

    Args:
        image_path (str): Path to invoice image

    Returns:
        dict: Extracted invoice fields

    Raises:
        FileNotFoundError
        RuntimeError
    """

    logger.info("Starting invoice extraction: %s", image_path)

    try:

        image_file = Path(image_path)

        if not image_file.exists():
            logger.error("Image not found: %s", image_path)
            raise FileNotFoundError(f"Image not found: {image_path}")

        with image_file.open("rb") as image:
            image_data = base64.b64encode(image.read()).decode("utf-8")

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are an invoice extraction assistant.

                    Extract invoice information and return ONLY valid JSON.

                    {
                    "vendor":"",
                    "invoice_number":"",
                    "invoice_date":"",
                    "currency":"",
                    "subtotal":0,
                    "tax":0,
                    "total":0,
                    "overall_confidence":0.95
                    }
                    """,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract invoice information."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_data}"},
                        },
                    ],
                },
            ],
        )

        content = response.choices[0].message.content

        if not content:
            logger.error("OpenAI returned empty response.")
            raise RuntimeError("Empty response from OpenAI")

        logger.info("OpenAI response received.")

        try:
            result = json.loads(content)
            print(result)

        except json.JSONDecodeError as ex:
            logger.exception(ex)
            raise RuntimeError("Invalid JSON returned by OpenAI")

        result.setdefault("vendor", "")
        result.setdefault("invoice_number", "")
        result.setdefault("invoice_date", "")
        result.setdefault("currency", "")
        result.setdefault("subtotal", 0)
        result.setdefault("tax", 0)
        result.setdefault("total", 0)
        result.setdefault("overall_confidence", 0)

        logger.info(
            "Invoice extracted successfully. Vendor=%s Invoice=%s",
            result["vendor"],
            result["invoice_number"],
        )

        return result

    except FileNotFoundError:
        raise

    except Exception as ex:

        logger.exception("Invoice extraction failed.")

        raise RuntimeError(f"Invoice extraction failed: {str(ex)}") from ex

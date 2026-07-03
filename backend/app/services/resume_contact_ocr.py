import base64
import json
import re
from io import BytesIO
from typing import Optional

import pypdfium2 as pdfium
from openai import OpenAI
from PIL import Image
from pydantic import BaseModel

from app.config import settings


class ResumeContactInfo(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None


PHONE_RE = re.compile(r"(?<!\d)(?:\+?86[-\s]?)?1[3-9]\d[-\s]?\d{4}[-\s]?\d{4}(?!\d)")
EMAIL_RE = re.compile(r"(?i)[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}")


def extract_contact_from_text(text: str) -> ResumeContactInfo:
    clean_text = (text or "").replace("\x00", "")
    phone_match = PHONE_RE.search(clean_text)
    email_match = EMAIL_RE.search(clean_text)
    return ResumeContactInfo(
        phone=normalize_phone(phone_match.group(0)) if phone_match else None,
        email=email_match.group(0).strip() if email_match else None,
    )


def should_ocr_pdf_contact(text: str) -> bool:
    if not text:
        return True

    contact = extract_contact_from_text(text)
    if contact.phone and contact.email:
        return False

    nul_count = text.count("\x00")
    has_contact_shape = "@" in text or "｜" in text or "|" in text
    return nul_count >= 3 and has_contact_shape


def extract_pdf_contact_with_vision(file_path: str) -> ResumeContactInfo:
    image_data_url = render_first_page_data_url(file_path)
    client = OpenAI(api_key=settings.QWEN_API_KEY, base_url=settings.QWEN_BASE_URL)
    response = client.chat.completions.create(
        model=settings.QWEN_VISION_MODEL,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Read this resume image and extract only the candidate phone number "
                            "and email address. Return strict JSON only, with keys phone and email. "
                            "Use null when absent."
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            }
        ],
    )
    content = response.choices[0].message.content or "{}"
    return parse_contact_json(content)


def enrich_resume_text_with_pdf_contact(file_path: str, text: str) -> str:
    if not should_ocr_pdf_contact(text):
        return text

    try:
        contact = extract_pdf_contact_with_vision(file_path)
    except Exception as exc:
        print(f"PDF contact OCR failed: {exc}")
        return text

    contact_lines = []
    if contact.phone:
        contact_lines.append(f"phone: {contact.phone}")
    if contact.email:
        contact_lines.append(f"email: {contact.email}")

    if not contact_lines:
        return text

    return f"{text.rstrip()}\n\nOCR contact:\n" + "\n".join(contact_lines)


def merge_contact_result(result, text: str):
    contact = extract_contact_from_text(text)
    if contact.phone:
        result.phone = contact.phone
    if contact.email:
        result.email = contact.email
    return result


def render_first_page_data_url(file_path: str) -> str:
    pdf = pdfium.PdfDocument(file_path)
    try:
        page = pdf[0]
        try:
            bitmap = page.render(scale=2.5)
            image = bitmap.to_pil().convert("RGB")
        finally:
            page.close()
    finally:
        pdf.close()

    image = shrink_image(image)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def shrink_image(image: Image.Image, max_side: int = 1800) -> Image.Image:
    width, height = image.size
    largest = max(width, height)
    if largest <= max_side:
        return image
    ratio = max_side / largest
    new_size = (int(width * ratio), int(height * ratio))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def parse_contact_json(content: str) -> ResumeContactInfo:
    json_text = strip_code_fence(content)
    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError:
        payload = {}

    phone = payload.get("phone") if isinstance(payload, dict) else None
    email = payload.get("email") if isinstance(payload, dict) else None
    return ResumeContactInfo(
        phone=normalize_phone(str(phone)) if phone else None,
        email=str(email).strip() if email else None,
    )


def strip_code_fence(content: str) -> str:
    text = (content or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("86") and len(digits) == 13:
        digits = digits[2:]
    return digits or phone.strip()

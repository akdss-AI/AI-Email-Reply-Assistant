import os
import json

from dotenv import load_dotenv
from groq import Groq

from schemas.message import AIEmailResult


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "openai/gpt-oss-20b"


class GroqServiceError(Exception):
    pass


class GroqQuotaError(Exception):
    pass


class GroqOutputError(Exception):
    pass


class GroqScopeError(Exception):
    pass
def check_request_scope(
    incoming_email: str,
    instruction: str
) -> bool:

    prompt = f"""
You are a strict scope classifier for an AI email reply drafting application.

The application has ONLY ONE purpose:

To transform a user's intended response into a reply to an incoming email.

Classify the request as:

IN_SCOPE = true
ONLY when the user is clearly asking the AI to draft, write, compose,
rewrite, formulate, or improve a reply to the provided incoming email.

IN_SCOPE = false
when the user is asking the AI to:
- answer a general question
- explain a technical concept
- provide information
- solve a problem
- write something unrelated to replying to the incoming email
- perform a task that is not email reply drafting

Important:
Do NOT classify based only on whether the input contains an email-like sentence.

Determine the user's actual requested task.

Incoming email:
{incoming_email}

User instruction:
{instruction}

Return ONLY true or false.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict binary scope classifier. "
                        "Return only true or false."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

    except Exception as e:
        print("GROQ SCOPE ERROR:", repr(e))

        error_text = str(e).lower()

        if "rate limit" in error_text or "quota" in error_text:
            raise GroqQuotaError(
                "Groq API rate limit or quota exceeded."
            ) from e

        raise GroqServiceError(
            "Groq scope check is currently unavailable."
        ) from e

    content = response.choices[0].message.content

    if not content:
        raise GroqOutputError(
            "Groq returned an empty scope response."
        )

    result = content.strip().lower()

    if result == "true":
        return True

    if result == "false":
        return False

    raise GroqOutputError(
        "Groq returned an invalid scope response."
    )

def draft_email_reply(
    incoming_email: str,
    instruction: str,
    tone: str
) -> AIEmailResult:
    if not check_request_scope(
    incoming_email=incoming_email,
    instruction=instruction
    ):
                
                raise GroqScopeError(
                  "This service only drafts replies to incoming emails."
                )

    prompt = f"""
You are an AI email reply drafting assistant.

Your ONLY purpose is to draft replies to incoming emails.

First determine whether the user's request is actually about
drafting a reply to an email.

If the request IS about drafting an email reply:

- Set in_scope to true.
- Draft the reply.
- Follow the requested tone.
- Do not invent facts.
- Do not change the user's intended meaning.
- Use only information provided by the user and incoming email.

If the request is NOT about drafting an email reply:

- Set in_scope to false.
- Do not answer the unrelated request.
- Set subject, greeting, body, and closing to null.
- Provide a short refusal explaining that this service only
  drafts email replies.

The user chooses the tone.
You must NOT choose a different tone.

Incoming email:
{incoming_email}

User instruction:
{instruction}

Requested tone:
{tone}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict email reply drafting assistant. "
                        "Return only the requested JSON structure."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "email_reply_result",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "in_scope": {
                                "type": "boolean"
                            },
                            "subject": {
                                "type": ["string", "null"]
                            },
                            "greeting": {
                                "type": ["string", "null"]
                            },
                            "body": {
                                "type": ["string", "null"]
                            },
                            "closing": {
                                "type": ["string", "null"]
                            },
                            "refusal": {
                                "type": ["string", "null"]
                            }
                        },
                        "required": [
                            "in_scope",
                            "subject",
                            "greeting",
                            "body",
                            "closing",
                            "refusal"
                        ],
                        "additionalProperties": False
                    }
                }
            }
        )

    except Exception as e:
        print("GROQ ACTUAL ERROR:", repr(e))

        error_text = str(e).lower()

        if "rate limit" in error_text or "quota" in error_text:
            raise GroqQuotaError(
                "Groq API rate limit or quota exceeded."
            ) from e

        raise GroqServiceError(
            "Groq service is currently unavailable."
        ) from e

    content = response.choices[0].message.content

    if not content:
        raise GroqServiceError(
            "Groq returned an empty response."
        )

    try:
        result = AIEmailResult.model_validate_json(content)
        return result

    except Exception as e:
        raise GroqOutputError(
            "Groq returned an invalid response format."
        ) from e
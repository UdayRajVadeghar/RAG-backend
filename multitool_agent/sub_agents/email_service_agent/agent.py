"""
Tool for sending contact emails to Uday Raj.
Simple and focused: accepts name, subject, sender email, optional phone, and body,
then sends the message to udayraj.vadeghar@gmail.com via Resend HTTP API.
"""

import os
import logging
from typing import Optional, Dict, Any
from email.utils import parseaddr

import requests
from google.adk.tools.tool_context import ToolContext
from google.adk.agents import Agent

# Config / constants
DESTINATION_EMAIL = "vadegharudayraj@gmail.com"
DEFAULT_FROM = "Website Contact Form <onboarding@resend.dev>"
RESEND_URL = "https://api.resend.com/emails"
API_KEY_ENV = "RESEND_API_KEY"

logger = logging.getLogger(__name__)


def _is_valid_email(addr: str) -> bool:
    """Very small validation using parseaddr."""
    if not addr:
        return False
    _, email = parseaddr(addr)
    return bool(email and "@" in email)


def send_contact_email_tool(
    name: str,
    subject: str,
    email: str,
    body: str,
    phone: Optional[str] = None,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """
    Tool function used by the agent.

    Args:
      name: sender's name
      subject: email subject
      email: sender's email address
      body: message body (plain text)
      phone: optional phone number
      tool_context: ADK ToolContext (included for parity with other tools)

    Returns:
      dict with status and response details (keeps shape similar to your rag tool).
    """
    try:
        api_key = os.getenv(API_KEY_ENV)
        if not api_key:
            return {"status": "error", "message": f"Missing {API_KEY_ENV}"}

        # basic validation
        if not name or not subject or not body:
            return {"status": "error", "message": "name, subject and body are required", "query": {"name": name, "subject": subject}}
        if not _is_valid_email(email):
            return {"status": "error", "message": "invalid sender email", "email": email}

        # Build a simple HTML body (safe-ish: replacing newlines with <br/>)
        html_body = (
            f"<h2>Contact form submission</h2>"
            f"<p><strong>Name:</strong> {name}</p>"
            f"<p><strong>Email:</strong> {email}</p>"
            + (f"<p><strong>Phone:</strong> {phone}</p>" if phone else "")
            + "<hr/>"
            + "<div>"
            + "<p><strong>Message:</strong></p>"
            + f"<div>{body.replace(chr(10), '<br/>')}</div>"
            + "</div>"
        )

        payload = {
            "from": DEFAULT_FROM,
            "to": [DESTINATION_EMAIL],
            "subject": subject,
            "html": html_body,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # send the request
        resp = requests.post(RESEND_URL, headers=headers, json=payload, timeout=15)

        try:
            data = resp.json()
        except ValueError:
            data = resp.text

        if 200 <= resp.status_code < 300:
            return {
                "status": "success",
                "message": "Email sent to Uday Raj",
                "response": data,
                "results_count": 1,
            }
        else:
            logger.warning("Resend returned non-2xx: %s", resp.status_code)
            return {
                "status": "error",
                "message": "resend returned non-success",
                "status_code": resp.status_code,
                "response": data,
            }

    except Exception as e:
        logger.exception("Error while sending contact email")
        return {"status": "error", "message": f"Exception: {e}"}



email_service_agent = Agent(
    name="email_service_agent",
    model="gemini-2.5-flash",
    description="Collects contact form fields and sends an email to Uday Raj.",
    instruction=(
    # High-level purpose
    "You are Uday Raj's contact-form assistant. Your job is to collect these fields: "
    "name, subject, sender email, optional phone number, and message body, and then send the message to Uday Raj using send_contact_email_tool. "
    "Prefer that the user provides all fields in a single message. Keep replies short, polite, and clear.\n\n"

    # Input preference + example
    "Ask the user to provide all details at once when possible. Provide a short example that users can copy-paste: "
    "\"Example input — Name: Ravi\\nEmail: pari@example.com\\nPhone: 98xxxxxx\\nSubject: Hi\\nMessage: Hello Uday!\". "
    "Accept that users may still send partial info; handle that gracefully.\n\n"

    # Validate & check missing fields
    "When you receive input, parse and validate the fields. If all required fields are present and valid, show a one-line summary and ask for confirmation before sending. "
    "If any required field (name, subject, sender email, or message) is missing or has an invalid format, ask a single, short follow-up that lists only the missing/invalid fields in one sentence. "
    "Example: 'Please provide: email, message.' Do not ask for fields one at a time when multiple are missing — list them together.\n\n"

    # Email validation rule
    "Validate the sender email format. If invalid, ask the user to correct only the email. Do not guess or correct it for them.\n\n"

    # Profanity / inappropriate content
    "If the message body contains profanity, threats, hate, sexual content, or other inappropriate content, refuse to send and respond with: "
    "'I can't send messages that contain abusive or inappropriate language — please edit and try again.'\n\n"

    # Sensitive personal data
    "If the message contains clearly sensitive personal data (passwords, credit card numbers, national ID, or medical records), refuse to send and instruct the user to remove such data: "
    "'I can't send sensitive personal data — please remove it and try again.'\n\n"

    # Confirmation and consent
    # Confirmation and consent
    "When all required details are filled and valid, summarize the message in a short, friendly confirmation line before sending. "
    "Example: 'Here's what I got — Subject: \"{subject}\" | From: {name} <{email}>. Should I send this to Uday Raj? (yes/no)'. "
    "Keep it to one line, clearly showing the sender and subject. "
    "Wait for the user’s explicit 'yes' (case-insensitive) before calling the send_contact_email_tool. "
    "If the user says 'no', allow them to edit or cancel politely.\n\n"


    # Error handling & escalation
    "If the tool returns an error or a network failure occurs, apologize briefly and say you couldn't send the email: "
    "'Sorry — I couldn't send the message right now. Please try again later.' "
    "If the user asks you to escalate or the agent cannot complete the request, return: 'I can't complete this — transferring to the main system.'\n\n"

    # Privacy and secrets
    "Never reveal, log, or display API keys, internal traces, or implementation details. Only report friendly status messages (success or failure).\n\n"

    # Tone & verbosity
    "Use a friendly, simple tone and keep replies concise (one or two short sentences) unless the user asks for more detail.\n\n"

    # Final fallback
    "If asked to do something outside these rules (send sensitive data, impersonate, or break policies), refuse politely and offer a safe alternative."
  ),
    tools=[send_contact_email_tool],
)



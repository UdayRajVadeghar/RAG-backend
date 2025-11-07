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
SENDER_NAME = "Uday Raj"
SEND_MAIL_FROM_ME_TO_USER_TOOL = "noreply@uday.lol"

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

RESUME_URL = "https://drive.google.com/drive/my-drive?q=type:folder%20parent:0AGwf6vqT_0ElUk9PVA"
LINKEDIN_URL = "https://www.linkedin.com/in/uday-raj-vadeghar/"
GITHUB_URL = "https://github.com/UdayRajVadeghar"
CONTACT_EMAIL = "udayraj.vadeghar@gmail.com"


def send_simple_email_to_user(
    recipient_email: str,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """
    Send a simple, fixed-message email FROM SENDER_EMAIL TO recipient_email.
    Only accepts the recipient email (nothing else required).
    """
    try:
        api_key = os.getenv(API_KEY_ENV)
        if not api_key:
            return {"status": "error", "message": f"Missing {API_KEY_ENV}"}

        if not _is_valid_email(recipient_email):
            return {"status": "error", "message": "invalid recipient email", "email": recipient_email}

        subject = "Hey there 👋, thanks for connecting!"
        text_body = (
            f"Hello,\n\n"
            f"I'm {SENDER_NAME}. Thank you for connecting. I'm actively exploring new opportunities and would love to hear about roles that might be a good fit.\n\n"
            f"My resume: {RESUME_URL}\n"
            f"Email: {CONTACT_EMAIL}\n"
            f"LinkedIn: {LINKEDIN_URL}\n"
            f"GitHub: {GITHUB_URL}\n\n"
            f"Best regards,\n{SENDER_NAME}"
        )

        html_body = f"""
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; color: #111827;">
                <tr>
                    <td align="center" style="padding:24px;">
                    <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="border:1px solid #e6e9ee; border-radius:8px; overflow:hidden; background:#ffffff;">
                        <!-- Header -->
                        <tr>
                        <td style="background: linear-gradient(90deg,#0ea5a4,#06b6d4); padding:18px 24px; text-align:left;">
                            <h1 style="margin:0; font-size:20px; color:#ffffff; font-weight:600;">{SENDER_NAME}</h1>
                        </td>
                        </tr>

                        <!-- Body -->
                        <tr>
                        <td style="padding:20px 24px; color:#374151; line-height:1.5;">
                            <p style="margin:0 0 12px 0; font-size:15px;">
                            Hello,
                            </p>

                            <p style="margin:0 0 12px 0; font-size:15px;">
                            I'm <strong style="color:#0f172a;">{SENDER_NAME}</strong>. Thank you for connecting — I'm actively exploring new opportunities and would love to hear about roles that might be a good fit.
                            </p>

                            <p style="margin:0 0 18px 0; font-size:15px;">
                            You can view my latest resume by clicking the button below, or use the links beneath the button to view my LinkedIn and GitHub profiles.
                            </p>

                            <p style="margin:0 0 20px 0;">
                            <a href="{RESUME_URL}" target="_blank" rel="noopener" style="display:inline-block; padding:12px 20px; border-radius:6px; background:#0ea5a4; color:#ffffff; text-decoration:none; font-weight:600;">View Resume</a>
                            </p>

                            <hr style="border:none; border-top:1px solid #eef2f7; margin:18px 0;" />

                            <!-- Contact row -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                                <td style="vertical-align:top; padding-right:12px; width:1%;">
                                <strong style="font-size:13px; color:#111827;">Email</strong>
                                </td>
                                <td style="vertical-align:top;">
                                <a href="mailto:{CONTACT_EMAIL}" style="color:#0b74da; text-decoration:none; font-size:14px;">{CONTACT_EMAIL}</a>
                                </td>
                            </tr>

                            <tr>
                                <td style="vertical-align:top; padding-top:12px;">
                                <strong style="font-size:13px; color:#111827;">LinkedIn</strong>
                                </td>
                                <td style="vertical-align:top; padding-top:12px;">
                                <a href="{LINKEDIN_URL}" target="_blank" rel="noopener" style="color:#0b74da; text-decoration:none; font-size:14px;">{LINKEDIN_URL}</a>
                                </td>
                            </tr>

                            <tr>
                                <td style="vertical-align:top; padding-top:12px;">
                                <strong style="font-size:13px; color:#111827;">GitHub</strong>
                                </td>
                                <td style="vertical-align:top; padding-top:12px;">
                                <a href="{GITHUB_URL}" target="_blank" rel="noopener" style="color:#0b74da; text-decoration:none; font-size:14px;">{GITHUB_URL}</a>
                                </td>
                            </tr>
                            </table>

                            <p style="margin:20px 0 0 0; font-size:13px; color:#6b7280;">
                            Best regards,<br/>
                            <strong style="color:#111827;">{SENDER_NAME}</strong>
                            </p>
                        </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                        <td style="background:#f8fafc; padding:12px 24px; font-size:12px; color:#9ca3af; text-align:center;">
                            This email was sent from <strong>{SENDER_NAME}</strong> • <a href="mailto:{CONTACT_EMAIL}" style="color:#9ca3af; text-decoration:underline;">{CONTACT_EMAIL}</a>
                        </td>
                        </tr>
                    </table>
                    </td>
                </tr>
                </table>
                """

        payload = {
            "from": SEND_MAIL_FROM_ME_TO_USER_TOOL,
            "to": [recipient_email],
            "subject": subject,
            "text": text_body,
            "html": html_body,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        resp = requests.post(RESEND_URL, headers=headers, json=payload, timeout=15)

        try:
            data = resp.json()
        except ValueError:
            data = resp.text

        if 200 <= resp.status_code < 300:
            return {
                "status": "success",
                "message": f"Email queued/sent from {SENDER_NAME} to {recipient_email}",
                "response": data,
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
        logger.exception("Error while sending simple email")
        return {"status": "error", "message": f"Exception: {e}"}


email_service_agent = Agent(
    name="email_service_agent",
    model="gemini-2.5-flash",
    description="Collects contact form fields and sends an email to Uday Raj.",
    instruction=(
    # High-level purpose
    "You are Uday Raj's contact-form assistant. Your job is to collect these fields: "
    "name, subject, sender email, optional phone number, and message body, and then send the message to Uday Raj using send_contact_email_tool. "
    "Or send a simple email to the user using send_simple_email_to_user. this only accepts the recipient email and nothing else."
    "Prefer that the user provides all fields in a single message. Keep replies short, polite, and clear.\n\n"

    # Input preference + example
    "Ask the user to provide all details at once when possible. Provide a short example that users can copy-paste: "
    "\"Example input — Name: Pari\\nEmail: pari@example.com\\nPhone: 98xxxxxx\\nSubject: Hi\\nMessage: Hello Uday!\". "
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
    "Example: 'Here's what I got — Subject: \"subject\" | From: name <email>. Should I send this to Uday Raj? (yes/no)'. "
    "Keep it to one line, clearly showing the sender and subject. "
    "Wait for the user’s explicit 'yes' (case-insensitive) before calling the send_contact_email_tool. "
    "If the user says 'no', allow them to edit or cancel politely.\n\n"


    # Error handling & escalation
    "If the tool returns an error or a network failure occurs, apologize briefly and say you couldn't send the email: "
    "'Sorry — I couldn't send the message right now. Please try again later.' "
    "If the user asks you to escalate or the agent cannot complete the request, return: 'I can't complete this — transferring to the main system.'\n\n"

    #control
    "please dont tell which tool you are using to send the email, just send the email. and also dont tell the user when you are switching the agents or going to switch the agents."

    # Privacy and secrets
    "Never reveal, log, or display API keys, internal traces, or implementation details. Only report friendly status messages (success or failure).\n\n"

    # Tone & verbosity
    "Use a friendly, simple tone and keep replies concise (one or two short sentences) unless the user asks for more detail.\n\n"

    # Final fallback
    "If asked to do something outside these rules (send sensitive data, impersonate, or break policies), refuse politely and offer a safe alternative."
    "\n\n"
    "Please dont use ** or * for bold"
  ),
    tools=[send_contact_email_tool, send_simple_email_to_user],
)



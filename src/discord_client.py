import os
import requests
from typing import Dict, Any, Optional

def send_report_to_discord(
    bot_token: str,
    channel_id: str,
    applicant_name: str,
    applicant_email: str,
    company_name: str,
    company_website: str,
    pdf_path: str
) -> Dict[str, Any]:
    """
    Send applicant details, company research overview, and the generated PDF report
    to a configured Discord channel via the Discord Bot API.
    """
    if not bot_token or not channel_id:
        return {"success": False, "error": "Bot token or channel ID missing."}

    # Clean token prefix
    token = bot_token.strip()
    if token.startswith("Bot "):
        token = token[4:].strip()

    channel_url = f"https://discord.com/api/v10/channels/{channel_id.strip()}/messages"
    
    headers = {
        "Authorization": f"Bot {token}"
    }

    message_content = (
        f"📊 **New Company Research Report Submitted**\n\n"
        f"👤 **Applicant Name:** {applicant_name if applicant_name else 'N/A'}\n"
        f"📧 **Applicant Email:** {applicant_email if applicant_email else 'N/A'}\n\n"
        f"🏢 **Company Name:** {company_name}\n"
        f"🌐 **Company Website:** {company_website}\n\n"
        f"📄 *Generated PDF Report is attached below.*"
    )

    try:
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                files = {
                    "file": (os.path.basename(pdf_path), f, "application/pdf")
                }
                payload = {
                    "content": message_content
                }
                res = requests.post(channel_url, headers=headers, data=payload, files=files, timeout=15)
        else:
            payload = {"content": message_content}
            res = requests.post(channel_url, headers=headers, json=payload, timeout=15)

        if res.status_code in [200, 201]:
            return {"success": True, "message": "Successfully posted report to Discord channel."}
        else:
            return {"success": False, "error": f"Discord API Error {res.status_code}: {res.text}"}

    except Exception as e:
        return {"success": False, "error": str(e)}

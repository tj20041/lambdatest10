import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger("cognito_sms_custom_sender")
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.handlers = [stream_handler]

class SmsNotificationFormatter:
    def __init__(self, template: str):
        self.template = template

    def format_code_message(self, one_time_code: str, target_phone: str, sent_date: Optional[str] = None) -> str:
        logger.info(f"Rendering SMS message template for recipient: {target_phone}")

        # Use str.format() with named placeholders instead of the '%' printf-style operator.
        # This avoids the ambiguity between literal date tokens (e.g. '%Y-%m-%d') and
        # printf-style conversion specifiers, which previously caused:
        # TypeError: not enough arguments for format string
        if sent_date is None:
            sent_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        try:
            rendered_message = self.template.format(code=one_time_code, date=sent_date)
        except (TypeError, ValueError, KeyError, IndexError) as exc:
            logger.error(f"Failed to render SMS template, falling back to plain OTP message: {exc}")
            rendered_message = f"Your verification code is: {one_time_code}. Valid for 5 minutes."

        return rendered_message

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info("Cognito Custom SMS Sender Lambda trigger initiated...")

    # Template now uses explicit named placeholders ({code}, {date}) so it can be safely
    # rendered with str.format() without colliding with printf-style '%' tokens.
    sms_template = "Your verification code is: {code}. Sent on {date}. Valid for 5 minutes."

    simulated_cognito_trigger_event = {
        "version": "1",
        "triggerSource": "CustomSMSSender_SignUp",
        "region": "us-east-1",
        "userPoolId": "us-east-1_mockPool",
        "userName": "usr_99812",
        "callerContext": {"clientId": "client_app_abc123"},
        "request": {
            "type": "customSMSSenderRequestV1",
            "code": "489201",
            "userAttributes": {
                "phone_number": "+15550199283"
            }
        }
    }

    otp_code = simulated_cognito_trigger_event["request"]["code"]
    phone_number = simulated_cognito_trigger_event["request"]["userAttributes"]["phone_number"]
    sent_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    formatter = SmsNotificationFormatter(template=sms_template)
    message_text = formatter.format_code_message(one_time_code=otp_code, target_phone=phone_number, sent_date=sent_date)

    logger.info("Constructed message ready for delivery dispatch.")
    return {"statusCode": 200, "rendered_message": message_text}

if __name__ == "__main__":
    lambda_handler({}, None)

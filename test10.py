import json
import logging
import sys
from typing import Any, Dict

logger = logging.getLogger("cognito_sms_custom_sender")
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.handlers = [stream_handler]

class SmsNotificationFormatter:
    def __init__(self, template: str):
        self.template = template

    def format_code_message(self, one_time_code: str, target_phone: str) -> str:
        logger.info(f"Rendering SMS message template for recipient: {target_phone}")

        # FAILS HERE: The template contains an unescaped date token '%Y-%m-%d' alongside printf markers '%s'.
        # Python interprets '%Y' as a printf format type character and raises ValueError: unsupported format character 'Y'
        rendered_message = self.template % (one_time_code,)
        return rendered_message

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info("Cognito Custom SMS Sender Lambda trigger initiated...")

    # Template containing unescaped percent signs from a logging timestamp pattern
    sms_template = "Your verification code is: %s. Sent on %Y-%m-%d. Valid for 5 minutes."

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

    formatter = SmsNotificationFormatter(template=sms_template)
    message_text = formatter.format_code_message(one_time_code=otp_code, target_phone=phone_number)

    logger.info("Constructed message ready for delivery dispatch.")
    return {"statusCode": 200, "rendered_message": message_text}

if __name__ == "__main__":
    lambda_handler({}, None)

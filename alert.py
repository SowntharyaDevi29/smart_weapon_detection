from twilio.rest import Client

ACCOUNT_SID = "AC9ed5689263866f7364761fdd460a6b22"
AUTH_TOKEN = "4caca4ff930d6251604d1ddc02f96dfd"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_sms_alert(weapon_name, time_detected):
    message_body = f"ALERT! Weapon Detected: {weapon_name} at {time_detected}"

    message = client.messages.create(
        body=message_body,
        from_='+15822285774',      # Twilio SMS number
        to='+916381853620'         # Your mobile number
    )

    print("SMS Sent Successfully:", message.sid)
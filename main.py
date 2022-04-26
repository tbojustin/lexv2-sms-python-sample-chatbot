import json
import boto3
import os
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    # log SNS Message from pinpoint
    message = event['Records'][0]['Sns']['Message']
    print("From SNS: " + message)
    """
    the message looks something like this
    {
    "originationNumber": "+17045551212",
    "destinationNumber": "+18557741671",
    "messageKeyword": "KEYWORD_13146xxxx",
    "messageBody": "This is the message",
    "previousPublishedMessageId": "2f53b013-rrrr-4bfe-8766-869db2f667bb",
    "inboundMessageId": "c32c3a9c-4703-4a40-rrrr-d66e64565388"
    }
    """
    SNS_message=json.loads(message)
    
    #setup LexV2 
    #We'll need the botid, botaliasid, localeid, a sessionID...
    #...and the message
    botId = os.environ['BotId']
    botAliasId = os.environ['BotAliasID']
    localeId = 'en_US'
    sessionId = 'test_session'
    text = SNS_message['messageBody']

    client = boto3.client('lexv2-runtime')
    
    response = client.recognize_text(
    botId=botId,
    botAliasId=botAliasId,
    localeId=localeId,
    sessionId=sessionId,
    text=text)
    
    #send response to pinpoint

    pinpoint=boto3.client('pinpoint')
    app_id = os.environ['PinpointApplicationId']
    origination_number=SNS_message['destinationNumber']
    destination_number=SNS_message['originationNumber']
    message=response['messages'][0]['content']
    print("Sending SMS message.")
    message_id = send_sms_message(
        pinpoint_client=pinpoint, 
        app_id=app_id, 
        origination_number=origination_number, 
        destination_number=destination_number,
        message=message)
    print(f"Message sent! Message ID: {message_id}.")
    return message_id
    
def send_sms_message(
        pinpoint_client, app_id, origination_number, destination_number, message,
        message_type="TRANSACTIONAL"):
    """
    Sends an SMS message with Amazon Pinpoint.

    :param pinpoint_client: A Boto3 Pinpoint client.
    :param app_id: The Amazon Pinpoint project/application ID to use when you send
                   this message. The SMS channel must be enabled for the project or
                   application.
    :param destination_number: The recipient's phone number in E.164 format.
    :param origination_number: The phone number to send the message from. This phone
                               number must be associated with your Amazon Pinpoint
                               account and be in E.164 format.
    :param message: The content of the SMS message.
    :param message_type: The type of SMS message that you want to send. If you send
                         time-sensitive content, specify TRANSACTIONAL. If you send
                         marketing-related content, specify PROMOTIONAL.
    :return: The ID of the message.
    """
    try:
        response = pinpoint_client.send_messages(
            ApplicationId=app_id,
            MessageRequest={
                'Addresses': {destination_number: {'ChannelType': 'SMS'}},
                'MessageConfiguration': {
                    'SMSMessage': {
                        'Body': message,
                        'MessageType': message_type,
                        'OriginationNumber': origination_number}}})
    except ClientError:
        logger.exception("Couldn't send message.")
        raise
    else:
        return response['MessageResponse']['Result'][destination_number]['MessageId']
    

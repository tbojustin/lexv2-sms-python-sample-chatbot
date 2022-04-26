# What & Why
This is a Python script for an SMS chatbot in Lambda using AWS Pinpoint and Lex V2. Everything else I saw was either in Node, didn't have SMS capabilities, or was for Lex V1

# Prerequisites

This is basically the same procedure as found in: https://aws.amazon.com/blogs//messaging-and-targeting/create-an-sms-chatbox-with-amazon-pinpoint-and-lex/

Key differences:
- This is in Python (the example is Javascript)
- This uses Lex V2 which means you'll have to give permissions for "Lex v2" - Write: "Recognize Text" in your Lambda Role

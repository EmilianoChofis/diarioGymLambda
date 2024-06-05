import json

# import requests


def lambda_handler(event, context):
    """
        :param event:
        :param context:
        :return:
    """

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "login Lambda",
            # "location": ip.text.replace("\n", "")
        }),
    }

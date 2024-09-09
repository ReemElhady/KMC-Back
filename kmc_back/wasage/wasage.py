import json
from urllib.parse import quote

import requests

from kmc_back.settings import WASAGE_USER, WASAGE_PASSWORD, WASAGE_SECRET


class Wasage:
    api = "https://wasage.com/"
    default_params = {
        "username": WASAGE_USER,
        "password": WASAGE_PASSWORD,
        "SenderKey": "",
    }
    secret = WASAGE_SECRET

    @classmethod
    def send_otp(cls, user_id):
        params = {
            **cls.default_params,
            "Reference": user_id,
            "Message": "Welcome to KMC",
        }
        response = requests.post(cls.api + "api/otp/", params=params)
        response = json.loads(response.text)
        response_code = response.get("Code")
        if response_code != "5500":
            raise Exception(response)

        return response

    @classmethod
    def send_message(cls, phone, message: str):
        params = {
            **cls.default_params,
            "Mobile": phone,
            "Text": quote(message, encoding="utf-8"),
        }
        response = requests.post(cls.api + "api/Text/", params=params)
        response = json.loads(response.text)
        response_code = response.get("Code")

        if response_code != "5505":
            raise Exception(response)

        return response

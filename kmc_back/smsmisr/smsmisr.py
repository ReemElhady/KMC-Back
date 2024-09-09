# import json
# import requests
# from kmc_back import settings
# from urllib.parse import quote
#
# default_params = {
#     "environment": 2 if settings.DEBUG else 1,  # 1 For Live , 2 For Test
#     # "username": "dfb478f2-57e5-4546-b73a-7ef3db64725f",
#     # "password": "1bc44ed76948e14419246e31f2bbb526482e0d164a5ef5a307b8fe4245a19638",
#     # "sender": "b611afb996655a94c8e942a823f1421de42bf8335d24ba1f84c437b2ab11ca27",
#     # "template": "e83faf6025ec41d0f40256d2812629f5fa9291d05c8322f31eea834302501da8",
#     "username": "e9e63c07-7050-461d-abff-1dbea8b29b7a",
#     "password": "8316fb5c9f06553d218998a4113feea924887da2526147a2cc8fee454abec8f6",
#     "sender": "b611afb996655a94c8e942a823f1421de42bf8335d24ba1f84c437b2ab11ca27",
# }
#
#
# class SmsMisrOTP:
#     api = "https://smsmisr.com/api/OTP/"
#
#     default_params[
#         "template"
#     ] = "e83faf6025ec41d0f40256d2812629f5fa9291d05c8322f31eea834302501da8"
#
#     response_map = {
#         "4901": "Success, Message Submitted Successfully",
#         "4903": "Invalid value in username or password field",
#         "4904": 'Invalid value in "sender" field',
#         "4905": 'Invalid value in "mobile" field',
#         "4906": "Insufficient Credit",
#         "4907": "Server under updating",
#         "4908": "Invalid OTP",
#         "4909": "Invalid Template Token",
#         "4012": "Invalid Environment",
#     }
#
#     @classmethod
#     def send(cls, otp, mobile):
#         params = {
#             **default_params,
#             "mobile": f"2{mobile}",
#             "otp": otp,
#         }
#         response = requests.post(cls.api, params=params)
#         response = json.loads(response.text.lower())
#         response_code = response.get("code")
#
#         if response_code != "4901":
#             print(
#                 f"-------------------- sms error {cls.response_map.get(response_code)}"
#             )
#             raise Exception(cls.response_map.get(response_code))
#
#         # print(f"-------------------- sms done {response}")
#
#
# class SmsMisrMessage:
#     api = "https://smsmisr.com/api/SMS/"
#
#     default_params["language"] = 2  # 1 For English , 2 For Arabic , 3 For Unicode
#     response_map = {
#         "1901": "Success, Message Submitted Successfully",
#         "1902": "Invalid Request",
#         "1903": "Invalid value in username or password field",
#         "1904": "Invalid value in 'sender' field",
#         "1905": "Invalid value in 'mobile' field",
#         "1906": "Insufficient Credit",
#         "1907": "Server under updating",
#         "1908": "Invalid Date & Time format in 'DelayUntil=' parameter",
#         "1909": "Invalid Message",
#         "1910": "Invalid Language",
#         "1911": "Text is too long",
#         "1912": "Invalid Environment",
#     }
#
#     @classmethod
#     def send(cls, message: str, mobile):
#         params = {
#             **default_params,
#             "mobile": f"2{mobile}",
#             "message": quote(message, encoding="utf-8"),
#         }
#         # print(params)
#         response = requests.post(cls.api, params=params)
#         response = json.loads(response.text.lower())
#         response_code = response.get("code")
#
#         if response_code != "1901":
#             raise Exception(cls.response_map.get(response_code))

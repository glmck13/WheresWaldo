import requests, json, sys, os

def button_handler (event, context=None):
    query = {}
    query["deviceId"] = event["deviceInfo"]["deviceId"]
    dict = event["deviceEvent"]["buttonClicked"]
    for key in dict.keys():
        query[key] = dict[key]
    dict = event["placementInfo"]["attributes"]
    for key in dict.keys():
        query[key] = dict[key]
    try:
        query["cellId"] = event["devicePayload"]["NS"][1]
    except:
        pass
    query.pop("additionalInfo", "")
    page = requests.get(os.environ.get("IOT_URL"), auth=(os.environ.get("IOT_USER"), os.environ.get("IOT_PASS")), params=query)
    print(page.content)

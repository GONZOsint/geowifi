import requests


def mac(bssid):
    response = requests.get('http://macvendors.co/api/' + bssid)

    return response




import re

import googlemaps
import requests
import yaml
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from yaml import CLoader

from helpers import BSSIDApple_pb2

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

with open('utils/API.yaml', 'r') as APIconfig:
    cfg = yaml.load(APIconfig, Loader=CLoader)


def wigle_bssid(bssid):
    if cfg['wigle_auth']:
        headers = {
            'accept': 'application/json',
            'Authorization': 'Basic ' + cfg['wigle_auth']
        }
        params = (
            ('netid', bssid),
        )
        response = requests.get('https://api.wigle.net/api/v2/network/detail', headers=headers, params=params)
        if response.json()['success'] == 'true':
            lat = response.json()['results'][0]['trilat']
            lon = response.json()['results'][0]['trilong']
            ssid = response.json()['results'][0]['ssid']
            data = {"bssid": bssid, "ssid": ssid, "lat": lat, "lon": lon}

            return data
    else:
        return 'AUTH code not configured or API limit exceeded'


def wigle_ssid(ssid):
    if cfg['wigle_auth']:
        headers = {
            'accept': 'application/json',
            'Authorization': 'Basic ' + cfg['wigle_auth']
        }
        params = (
            ('onlymine', 'false'),
            ('freenet', 'false'),
            ('paynet', 'false'),
            ('ssid', ssid)
        )
        response = requests.get('https://api.wigle.net/api/v2/network/search', headers=headers, params=params)
        if response.json()['success']:
            json_data = {'results': []}
            for result in response.json()['results']:
                lat = result['trilat']
                lon = result['trilong']
                address = '{} {} {} {} {} {}'.format(str(result['housenumber']), result['road'], result['city'],
                                                     str(result['postalcode']), result['region'],
                                                     result['country']).replace('None ', '')
                data = {'lat': lat, 'lon': lon, 'address': address}
                json_data['results'].append(data)
            return json_data
    else:
        return 'AUTH code not configured or API limit exceeded'


def milnikov_bssid(bssid):
    response = requests.get('https://api.mylnikov.org/geolocation/wifi?v=1.1&data=open&bssid=' + bssid)
    if response.json()['result'] == 200:
        lat = response.json()['data']['lat']
        lon = response.json()['data']['lon']
        data = {"bssid": bssid, "lat": lat, "lon": lon}

        return data


def openwifi_bssid(bssid):
    response = requests.get('https://openwifi.su/api/v1/bssids/' + bssid.replace(':', ''))
    if 'BSSIDISNULL' not in response.text:
        if response.json()['count_results'] != 0:
            lat = response.json()['lat']
            lon = response.json()['lon']
            data = {"bssid": bssid, "lat": lat, "lon": lon}

            return data


def apple_bssid(bssid):
    data_bssid = f"\x12\x13\n\x11{bssid}\x18\x00\x20\01"
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': '*/*',
               "Accept-Charset": "utf-8",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "en-us",
               'User-Agent': 'locationd/1753.17 CFNetwork/711.1.12 Darwin/14.0.0'
               }
    data = "\x00\x01\x00\x05en_US\x00\x13com.apple.locationd\x00\x0a" + "8.1.12B411\x00\x00\x00\x01\x00\x00\x00" + \
           chr(len(data_bssid)) + data_bssid
    response = requests.post('https://gs-loc.apple.com/clls/wloc', headers=headers, data=data, verify=False)
    bssid_response = BSSIDApple_pb2.BSSIDResp()
    bssid_response.ParseFromString(response.content[10:])
    lat = re.search('lat: (\S*)', str(bssid_response)).group(1)
    if '18000000000' not in lat:
        latlist = list(str(lat))
        latlist.insert(2, '.')
        lat = "".join(latlist)
        lon = re.search('lon: (\S*)', str(bssid_response)).group(1)
        lonlist = list(str(lon))
        lonlist.insert(2, '.')
        lon = "".join(lonlist)
        data = {"bssid": bssid, "lat": lat, "lon": lon}

        return data

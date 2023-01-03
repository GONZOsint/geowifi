import argparse
import concurrent.futures
import json
import os
import re

import folium
import requests
import yaml
from google.protobuf.message import DecodeError
from rich import print
from rich._emoji_codes import EMOJI
from rich.console import Console
from rich.table import Table

emoji_list = ['cd', 'ab', 'ox', 'wc', 'cl', 'id', 'sa', 'vs', 'o2', 'on', 'tm']
for emj in emoji_list:
    del EMOJI[emj]
# import the BSSIDResp protobuf message from the BSSIDApple_pb2 module
from helpers.BSSIDApple_pb2 import BSSIDResp

console = Console()
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


def banner():
    print("""
   ██████╗ ███████╗ ██████╗   ██╗    ██╗     ███████╗ 
  ██╔════╝ ██╔════╝██╔═══██╗  ██║    ██║ ██╗ ██╔════╝ ██╗
  ██║  ███╗█████╗  ██║   ██║  ██║ █╗ ██║ ██║ █████╗   ██║
  ██║   ██║██╔══╝  ██║   ██║  ██║███╗██║ ██║ ██╔══╝   ██║
  ╚██████╔╝███████╗╚██████╔╝  ╚███╔███╔╝ ██║ ██║      ██║
   ╚═════╝ ╚══════╝ ╚═════╝    ╚══╝╚══╝  ╚═╝ ╚═╝      ╚═╝ :earth_africa:[bold medium_purple1 italic]by GOΠZO[/bold medium_purple1 italic]                          
""")


def read_config():
    """Loads the configuration data from config.yaml file.

    Returns:
        dict: A dictionary containing the configuration data.
    """
    try:
        # Open the config.yaml file in read mode
        with open('gw_utils/config.yaml', 'r') as config_file:
            # Parse the contents of the file into a dictionary
            parsed_config = yaml.safe_load(config_file)
            return parsed_config
    except FileNotFoundError:
        # Return an error message if the file is not found
        return {'error': 'config.yaml file not found'}
    except yaml.YAMLError:
        # Return an error message if there is an error parsing the file
        return {'error': 'Error parsing config.yaml file'}


def wigle_ssid(ssid_param):
    """Searches for a network with a specific SSID in the Wigle database.

    Parameters:
        ssid_param (str): The SSID of the network to search for.

    Returns:
        list: A list of dictionaries, each containing information about a network. If an error occurred, the list will contain a single dictionary with an error message.
    """
    # Load the configuration data from the config.yaml file
    parsed_config = read_config()
    # Get the Wigle API key from the configuration data
    api_key = parsed_config.get('wigle_auth')
    # Set the headers for the request
    headers = {
        'accept': 'application/json',
        'Authorization': f'Basic {api_key}'
    }
    # Set the parameters for the request
    params = {'ssid': ssid_param}
    # Set the endpoint for the request
    endpoint = 'https://api.wigle.net/api/v2/network/search'
    try:
        # Send the GET request
        response = requests.get(
            endpoint,
            headers=headers,
            params=params,
            # Disable SSL verification if specified in the configuration data
            verify=not parsed_config.get('no-ssl-verify', False)
        )
        # If the request is successful
        if response.json()['success']:
            # If the request is successful
            if response.json()['totalResults'] != 0:
                # Get the results from the response
                results = response.json()['results']
                # Create a list of dictionaries containing the data
                data = [{
                    'module': 'wigle',
                    'bssid': result.get('netid', ''),
                    'ssid': result.get('ssid', ''),
                    'latitude': result.get('trilat', ''),
                    'longitude': result.get('trilong', '')
                } for result in results]
                return data
            else:
                # Return an error message if the request is not successful
                return {
                    'module': 'wigle',
                    'error': 'No results detected'
                }
        else:
            # Return an error message if the request is not successful
            return {
                'module': 'wigle',
                'error': response.json()['message']
            }
    except Exception as e:
        # Return an error message if an exception occurs
        return {
            'module': 'wigle',
            'error': str(e)
        }


def wifidb_ssid(ssid_param):
    """Searches for a network with a specific SSID in the wifidb database.

    Parameters:
        ssid_param (str): The SSID of the network to search for.

    Returns:
        list: A list of dictionaries, each containing information about a network. If an error occurred, the list will contain a single dictionary with an error message.
    """
    # Load the configuration data from the config.yaml file
    parsed_config = read_config()
    # Set the parameters for the request
    params = {
        'func': 'exp_search',
        'ssid': ssid_param,
        'mac': '',
        'radio': '',
        'chan': '',
        'auth': '',
        'encry': '',
        'sectype': '',
        'json': 0,
        'labeled': 0
    }
    # Set the endpoint for the request
    endpoint = 'https://wifidb.net/wifidb/api/geojson.php'
    try:
        # Send the GET request
        response = requests.get(
            endpoint,
            params=params,
            # Disable SSL verification if specified in the configuration data
            verify=not parsed_config.get('no-ssl-verify', False)
        )
        # If the request is successful
        if response.status_code == 200:
            # Get the results from the response
            results = response.json()['features']
            # Check if the SSID is in the results
            if len(results) > 0:
                # Create a list of dictionaries containing the data
                data = [{
                    'module': 'wifidb',
                    'bssid': result['properties']['mac'],
                    'ssid': result['properties']['ssid'],
                    'latitude': result['properties']['lat'],
                    'longitude': result['properties']['lon']
                } for result in results]
                return data
            else:
                # Return an error message if the SSID is not in the results
                return {
                    'module': 'wifidb',
                    'error': 'SSID not found'
                }
        else:
            # Return an error message if the request is not successful
            return {
                'module': 'wifidb',
                'error': 'Request failed'
            }
    except Exception as e:
        # Return an error message if an exception occurs
        return {
            'module': 'wifidb',
            'error': str(e)
        }


def openwifimap_ssid(ssid_param):
    """Searches for a node with a specific SSID in the openwifimap.net database.

    Parameters:
        ssid_param (str): The SSID of the node to search for.

    Returns:
        dict: A dictionary containing information about the node, or an error message if an error occurred.
    """
    # Load the configuration data from the config.yaml file
    parsed_config = read_config()
    # Set the endpoint for the request
    endpoint = 'https://api.openwifimap.net/view_nodes'
    # Set the headers for the request
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    # Set the request body
    data = {'keys': [ssid_param]}
    try:
        # Send the POST request
        response = requests.post(
            endpoint,
            headers=headers,
            json=data,
            # Disable SSL verification if specified in the configuration data
            verify=not parsed_config.get('no-ssl-verify', False)
        )
        # If the request is successful
        if response.status_code == 200:
            # Get the results from the response
            results = response.json()['rows']
            # If there are no results, return an error message
            if not results:
                return {
                    'module': 'openwifimap',
                    'error': f'No node found with SSID "{ssid_param}"'
                }
            # Extract the relevant fields from the first result
            result = results[0]['value']
            # Create the output dictionary using a dictionary comprehension
            data = {
                'module': 'openwifimap',
                'ssid': ssid_param,
                'hostname': result['hostname'],
                'latitude': result['latlng'][0],
                'longitude': result['latlng'][1]
            }
            return data
        else:
            # Return the error message if the request is not successful
            return {
                'module': 'openwifimap',
                'error': f'Request to openwifimap.net failed with status code {response.status_code}'
            }
    except Exception as e:
        # Return an error message if an exception occurs
        return {
            'module': 'openwifimap',
            'error': str(e)
        }


def freifunk_karte_ssid(ssid_param):
    """Searches for a network with a specific SSID in the freifunk-karte.de database.

    Parameters:
        ssid_param (str): The SSID of the network to search for.

    Returns:
        dict: A dictionary containing information about the network, or an error message if an error occurred.
    """
    # Load the configuration data from the config.yaml file
    parsed_config = read_config()
    # Set the endpoint for the request
    endpoint = 'https://www.freifunk-karte.de/data.php'
    try:
        # Send the GET request
        response = requests.get(
            endpoint,
            # Disable SSL verification if specified in the configuration data
            verify=not parsed_config.get('no-ssl-verify', False)
        )
        # If the request is successful
        if response.status_code == 200:
            # Get the results from the response
            results = response.json()['allTheRouters']
            # Check if the SSID is in the results
            for result in results:
                if result['name'] == ssid_param:
                    # Extract the relevant fields from the result
                    data = {
                        'module': 'freifunk-karte',
                        'ssid': result['name'],
                        'latitude': result['lat'],
                        'longitude': result['long'],
                        'community': result['community'],
                    }
                    return data
            # If the SSID is not in the results, return an error message
            return {
                'module': 'freifunk-karte',
                'error': 'SSID not found'
            }
        else:
            # Return an error message if the request is not successful
            return {
                'module': 'freifunk-karte',
                'error': 'Request failed'
            }
    except Exception as e:
        # Return an error message if an exception occurs
        return {
            'module': 'freifunk-karte',
            'error': str(e)
        }


def wigle_bssid(bssid_param):
    """Searches for a network with a specific BSSID in the Wigle database.

    Parameters:
        bssid_param (str): The BSSID of the network to search for.

    Returns:
        list: A list of dictionaries, each containing information about a network. If an error occurred, the list will contain a single dictionary with an error message.
    """
    # Load the configuration data from the config.yaml file
    parsed_config = read_config()
    # Get the Wigle API key from the configuration data
    api_key = parsed_config.get('wigle_auth')
    # Set the headers for the request
    headers = {
        'accept': 'application/json',
        'Authorization': f'Basic {api_key}'
    }
    # Set the parameters for the request
    params = {'netid': bssid_param}
    # Set the endpoint for the request
    endpoint = 'https://api.wigle.net/api/v2/network/search'
    try:
        # Send the GET request
        response = requests.get(
            endpoint,
            headers=headers,
            params=params,
            # Disable SSL verification if specified in the configuration data
            verify=not parsed_config.get('no-ssl-verify', False)
        )
        # If the request is successful
        if response.json()['success']:
            # If the request is successful
            if response.json()['totalResults'] != 0:
                # Get the results from the response
                results = response.json()['results']
                # Create a list of dictionaries containing the data
                data = [{
                    'module': 'wigle',
                    'bssid': result.get('netid', ''),
                    'ssid': result.get('ssid', ''),
                    'latitude': result.get('trilat', ''),
                    'longitude': result.get('trilong', '')
                } for result in results]
                return data
            else:
                # Return an error message if the request is not successful
                return {
                    'module': 'wigle',
                    'error': 'No results detected'
                }
        else:
            # Return an error message if the request is not successful
            return {
                'module': 'wigle',
                'error': response.json()['message']
            }
    except Exception as e:
        # Return an error message if an exception occurs
        return {
            'module': 'wigle',
            'error': str(e)
        }


def mylnikov_bssid(bssid_param):
    """Searches for a network with a specific BSSID in the mylnikov database.

    Parameters:
        bssid_param (str): The BSSID of the network to search for.

    Returns:
        dict: A dictionary containing information about the network, or an error message if an error occurred.
    """

    # Read the configuration from the config.yaml file
    parsed_config = read_config()

    # Set up the HTTP headers
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Set up the query parameters with the BSSID
    params = {'bssid': bssid_param}

    # Set the endpoint for the request
    endpoint = 'https://api.mylnikov.org/geolocation/wifi?v=1.1&data=open'
    # Make the HTTP POST request to the mylnikov API
    try:
        # Send the POST request
        response = requests.post(
            endpoint,
            headers=headers,
            params=params,
            # Disable SSL verification if specified in the configuration data
            verify=not parsed_config.get('no-ssl-verify', False)
        )
        # Check if the request was successful
        if response.json()['result'] == 200:
            # Extract the relevant fields from the response
            result = response.json()['data']
            # Create the output dictionary using a dictionary comprehension
            data = {
                'module': 'mylnikov',
                'bssid': bssid_param,
                'latitude': result['lat'],
                'longitude': result['lon']
            }
            return data
        else:
            # Return the error message in a dictionary
            return {
                'module': 'mylnikov',
                'error': response.json()['desc']
            }
    except Exception as e:
        # Return the exception message in a dictionary
        return {
            'module': 'wigle',
            'error': str(e)
        }


def apple_bssid(bssid_param):
    """Searches for a network with a specific BSSID in the Apple database.

    Parameters:
        bssid_param (str): The BSSID of the network to search for.

    Returns:
        dict: A dictionary containing information about the network, or an error message if an error occurred.
    """
    # Read the configuration from the config.yaml file
    parsed_config = read_config()

    # Set up the HTTP headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'Accept-Charset': 'utf-8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-us',
        'User-Agent': 'locationd/1753.17 CFNetwork/711.1.12 Darwin/14.0.0'
    }

    # Set up the POST data
    data_bssid = f'\x12\x13\n\x11{bssid_param}\x18\x00\x20\01'
    data = '\x00\x01\x00\x05en_US\x00\x13com.apple.locationd\x00\x0a' + '8.1.12B411\x00\x00\x00\x01\x00\x00\x00' + chr(
        len(data_bssid)) + data_bssid
    # Set the endpoint for the request
    endpoint = 'https://gs-loc.apple.com/clls/wloc'
    # Make the HTTP POST request using the requests library
    response = requests.post(
        endpoint,
        headers=headers,
        data=data,
        verify=not parsed_config.get('no-ssl-verify', False))

    # Parse the binary content of the response into a BSSIDResp protobuf object.
    bssid_response = BSSIDResp()
    try:
        bssid_response.ParseFromString(response.content[10:])
    except DecodeError as e:
        return f'Failed to decode response: {e}'
    lat_match = re.search('lat: (\S*)', str(bssid_response))
    lon_match = re.search('lon: (\S*)', str(bssid_response))
    try:
        # Extract the latitude and longitude values from the response
        lat = lat_match.group(1)
        lon = lon_match.group(1)

        if '18000000000' not in lat:
            # format the latitude and longitude values
            lat = float(lat[:-8] + '.' + lat[-8:])
            lon = float(lon[:-8] + '.' + lon[-8:])
            # create the output dictionary
            data = {
                'module': 'apple',
                'bssid': bssid_param,
                'latitude': lat,
                'longitude': lon
            }
            return data
        else:
            return {
                'module': 'apple',
                'error': 'Latitude or longitude value not found in response'
            }
    except Exception as e:
        if not lat_match or not lon_match:
            # Return the error message in a dictionary
            return {
                'module': 'apple',
                'error': 'Latitude or longitude value not found in response'
            }
        # Return the exception message in a dictionary
        return {
            'module': 'apple',
            'error': str(e)
        }


def google_bssid(bssid_param):
    """Searches for a network with a specific BSSID in the Google geolocation API.

    Parameters:
        bssid_param (str): The BSSID of the network to search for.

    Returns:
        dict: A dictionary containing information about the network, or an error message if an error occurred.
    """

    # Read the configuration from the config.yaml file
    parsed_config = read_config()
    # Get the Comba.in API key from the configuration data
    api_key = parsed_config.get('google_api')
    # Set up the HTTP headers
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    # Set up the query parameters with the BSSID
    params = {
        'considerIp': 'false',
        'wifiAccessPoints': [
            {
                'macAddress': bssid_param,
            },
            {
                'macAddress': '00:25:9c:cf:1c:ad',
            }
        ]
    }
    # Set the endpoint for the request
    endpoint = f'https://www.googleapis.com/geolocation/v1/geolocate?key={api_key}'
    # Make the HTTP POST request to the Google geolocation API
    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=params,
            verify=not parsed_config.get('no-ssl-verify', False)
        )
        # Check if the request was successful
        if response.status_code == 200:
            # Extract the relevant fields from the response
            result = response.json()
            # Create the output dictionary using a dictionary comprehension
            data = {
                'module': 'google',
                'bssid': bssid_param,
                'latitude': result['location']['lat'],
                'longitude': result['location']['lng']
            }
            return data
        else:
            # Return the error message in a dictionary
            return {
                'module': 'google',
                'error': response.json()['error']['message']
            }
    except Exception as e:
        # Return the exception message in a dictionary
        return {
            'module': 'google',
            'error': str(e)
        }


def combain_bssid(bssid_param):
    """Searches for a network with a specific BSSID in the Comba.in database.

    Parameters:
        bssid_param (str): The BSSID of the network to search for.

    Returns:
        dict: A dictionary containing information about the network, or an error message if an error occurred.
    """
    # Load the configuration data from the config.yaml file
    parsed_config = read_config()
    # Get the Comba.in API key from the configuration data
    api_key = parsed_config.get('combain_api')
    # Set the headers for the request
    headers = {
        'Content-Type': 'application/json',
    }
    # Set the parameters for the request
    params = {
        'wifiAccessPoints': [{
            'macAddress': bssid_param,
            'macAddress': '28:28:5d:d6:39:8a'
        }],
        'indoor': 1
    }
    # Set the endpoint for the request
    endpoint = f'https://apiv2.combain.com?key={api_key}'
    try:
        # Send the POST request
        response = requests.post(
            endpoint,
            headers=headers,
            json=params,
            # Disable SSL verification if specified in the configuration data
            verify=not parsed_config.get('no-ssl-verify', False)
        )
        # If the request is successful
        if response.status_code == 200:
            # Extract the relevant fields from the response
            result = response.json()
            data = {
                'module': 'combain',
                'bssid': bssid_param,
                'latitude': result['location']['lat'],
                'longitude': result['location']['lng'],
            }
            if 'indoor' in result:
                data['building'] = result['indoor']['building']
            return data
        else:
            # Return an error message if the request is not successful
            return {
                'module': 'combain',
                'error': response.json()['error']['message']
            }
    except Exception as e:
        # Return an error message if an exception occurs
        return {
            'module': 'combain',
            'error': str(e)
        }


def wifidb_bssid(bssid_param):
    """Searches for a network with a specific BSSID in the wifidb database.

    Parameters:
        bssid_param (str): The BSSID of the network to search for.

    Returns:
        list: A list of dictionaries, each containing information about a network. If an error occurred, the list will contain a single dictionary with an error message.
    """
    # Load the configuration data from the config.yaml file
    parsed_config = read_config()
    # Set the endpoint for the request
    endpoint = 'https://wifidb.net/wifidb/api/geojson.php'
    # Set the parameters for the request
    params = {
        'func': 'exp_search',
        'ssid': '',
        'mac': bssid_param,
        'radio': '',
        'chan': '',
        'auth': '',
        'encry': '',
        'sectype': '',
        'json': '0',
        'labeled': '0'
    }
    try:
        # Send the GET request
        response = requests.get(
            endpoint,
            params=params,
            # Disable SSL verification if specified in the configuration data
            verify=not parsed_config.get('no-ssl-verify', False)
        )
        # If the request is successful
        if response.status_code == 200:
            # Get the results from the response
            results = response.json()['features']
            # Create a list of dictionaries containing the data
            data = [{
                'module': 'wifidb',
                'bssid': result['properties']['mac'],
                'ssid': result['properties']['ssid'],
                'latitude': result['properties']['lat'],
                'longitude': result['properties']['lon']
            } for result in results]
            return data
        else:
            # Return an error message if the request is not successful
            return {
                'module': 'wifidb',
                'error': 'Request failed'
            }
    except Exception as e:
        # Return an error message if an exception occurs
        return {
            'module': 'wifidb',
            'error': str(e)
        }


def vendor_check(bssid):
    """Searches for information about the vendor of a device with the specified BSSID.

    Parameters:
        bssid (str): The BSSID of the device to search for.

    Returns:
        dict: A dictionary containing information about the vendor of the device, or an error message if an error occurred.
    """

    try:
        # Send a GET request to the macvendors.com API, with the BSSID as a parameter
        response = requests.get('https://api.macvendors.com/' + bssid)
        # Raise an exception if the response indicates that an error occurred
        response.raise_for_status()
        # Extract the vendor information from the response
        data = {
            'module': 'vendor_check',
            'vendor': response.text
        }
        # Return the vendor information
        return data
    except requests.exceptions.RequestException as e:
        # Return an error message if an exception occurs
        return {'error': str(e)}


def search_networks(bssid=None, ssid=None):
    """Searches for networks using the specified search criteria.

    Parameters:
        bssid (str, optional): The BSSID of the network to search for.
        ssid (str, optional): The SSID of the network to search for.

    Returns:
        list: A list of dictionaries, each containing information about a network.
    """

    # Initialize an empty list to store the results
    results = []

    # Create a list of functions to be called concurrently
    functions = []
    if bssid:
        functions.extend(
            [wigle_bssid, apple_bssid, mylnikov_bssid, google_bssid, combain_bssid, wifidb_bssid, vendor_check])
    if ssid:
        functions.extend([wigle_ssid, openwifimap_ssid, wifidb_ssid, freifunk_karte_ssid])

    # Use a ThreadPoolExecutor to call the functions concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a list of futures for each function
        futures = [executor.submit(f, bssid or ssid) for f in functions]

        # Iterate over the completed futures
        for future in concurrent.futures.as_completed(futures):
            try:
                # Get the result from the future
                result = future.result()

                # Add the result to the list of results
                if bssid:
                    if isinstance(result, list):
                        for res in result:
                            if str(res['bssid']).lower() == str(bssid).lower():
                                if res['latitude'] != 0.0:
                                    results.append(res)
                    else:
                        results.append(result)
                if ssid:
                    if isinstance(result, list):
                        for res in result:
                            if str(res['ssid']).lower() == str(ssid).lower():
                                if res['latitude'] != 0.0:
                                    results.append(res)
                    else:
                        results.append(result)
            except Exception as e:
                # Add an error message to the list of results if an exception occurred
                module_name = functions[futures.index(future)].__name__.split('_')[0]
                results.append({
                    'module': module_name,
                    'error': str(e)
                })

    # Format the json data
    for locations in results:
        if 'latitude' in locations:
            locations['latitude'] = float(locations['latitude'])
        if 'longitude' in locations:
            locations['longitude'] = float(locations['longitude'])

    return results


def create_map(search_results_data):
    # Set a default location for the map
    default_location = [48.8566, 2.3522]

    # Use the default location if the first search result is missing a latitude or longitude, or if there are no search results
    map = folium.Map(location=[39.600441, -41.141473], zoom_start=3,
                     tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google')

    # Iterate through the search results
    for result in search_results_data:
        # Check if the result contains an error message
        if 'error' in result:
            # Skip this result if it contains an error message
            continue
        # Check if the result contains a latitude and longitude
        elif 'latitude' in result and 'longitude' in result:
            # Create the popup text with increased font size and line height
            popup_text = f'<style>body {{font-size: 20px; line-height: 1.5; font-family: "Consolas";}}</style>'
            # Create the popup text with headings and paragraphs
            popup_text = f'<h3>Network Information</h1>'
            popup_text += f'<p><b>Module</b>: {result["module"]}</p>'
            if 'bssid' in result:
                popup_text += f'<p><b>BSSID</b>: {result["bssid"]}</p>'
            elif 'ssid' in result:
                popup_text += f'<p><b>SSID</b>: {result["ssid"]}</p>'
            # Look for a vendor_check result with the same BSSID
            for vendor_result in search_results_data:
                if vendor_result['module'] == 'vendor_check':
                    # Use the vendor information from the vendor_check result
                    popup_text += f'<p><b>Vendor</b>: {vendor_result["vendor"]}</p>'
                    break
            # Create an IFrame with the formatted popup text
            popup = folium.Popup(popup_text)
            # Add a marker to the map at the location of the network
            folium.Marker(location=[result['latitude'], result['longitude']], popup=popup,
                          icon=folium.Icon(color='red', icon='wifi', prefix='fa')).add_to(map)

    return map


def is_valid_bssid(bssid):
    """Checks if a string is a valid BSSID.

    A valid BSSID is a string in the format XX:XX:XX:XX:XX:XX where X is a hexadecimal digit.

    Parameters:
        bssid (str): The string to be checked.

    Returns:
        bool: True if the string is a valid BSSID, False otherwise.
    """
    # Define the regular expression pattern for a valid BSSID
    bssid_regex = r'^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$'

    # Use the re module's match function to check if the given string matches the pattern
    # If it matches, the match function returns a Match object. If it doesn't match, it returns None.
    return re.match(bssid_regex, bssid) is not None


def print_results_table(results, main_color='bright_yellow', secondary_color='bright_blue'):
    """Prints search_results in a table format, including any errors that occurred during the search and the result of
        a vendor check module (if one was run).

    Parameters:
        - results (list): a list of dictionaries, where each dictionary represents the results of a search
        - main_color (str, optional): the color of the table header. Defaults to 'bright_yellow'
        - secondary_color (str, optional): the color of the other cells in the table. Defaults to 'bright_blue'

    The function also prints any errors that occurred during the search, indicated with a red circle emoji.
    If a vendor check module was run, the result is also printed, indicated with a green circle emoji.
    """
    # Create a table with the desired columns
    table = Table(show_header=True, header_style=main_color, title_justify='center', title='Search Results')
    table.add_column('Module', style=secondary_color)
    table.add_column('BSSID', style=secondary_color, justify='center')
    table.add_column('SSID', style=secondary_color, justify='center')
    table.add_column('Latitude', style=secondary_color, justify='center')
    table.add_column('Longitude', style=secondary_color, justify='center')

    # Add a row for each result
    for result in results:
        if result['module'] != 'vendor_check':
            module = result.get('module', '')
            bssid = result.get('bssid', '')
            ssid = result.get('ssid', '')
            latitude = str(result.get('latitude', ''))
            longitude = str(result.get('longitude', ''))

            # Use emojis to indicate empty fields
            if not bssid:
                bssid = '❌'
            if not ssid:
                ssid = '❌'
            if not latitude:
                latitude = '❌'
            if not longitude:
                longitude = '❌'

            # Use a different color for cells that contain errors
            if 'error' in result:
                table.add_row(module, bssid, ssid, latitude, longitude, style='bright_red')
            else:
                table.add_row(module, bssid, ssid, latitude, longitude)

    # Print the table to the console
    console.print(table)
    print()

    # Print errors
    for result in results:
        if 'error' in result:
            console.print(' [:red_circle:] [bright_yellow]Error in [/bright_yellow][bright_blue]' + result[
                'module'] + ' [/bright_blue][bright_yellow]module[/bright_yellow]: ' + str(result['error']).lower())
    print()

    # Print vendor check results
    for result in results:
        if result['module'] == 'vendor_check':
            console.print(
                ' [:green_circle:] [bright_yellow] Vendor_check module result: [/bright_yellow]: [bright_blue]' +
                result['vendor'] + '[/bright_blue]')
            console.print()


# Set up the argument parser
parser = argparse.ArgumentParser(description='Search for information about a network with a specific BSSID or SSID.')
parser.add_argument('identifier', help='The BSSID or SSID of the network to search for.')
parser.add_argument('-s', '--search-by', choices=['bssid', 'ssid'], default='bssid',
                    help='Specifies whether to search by BSSID or SSID (default: bssid)')
parser.add_argument('-o', '--output-format', choices=['map', 'json'], default='html',
                    help='Specifies the output format for the search results (default: map)')

# Print banner
banner()

# Parse the arguments
args = parser.parse_args()

# Get the search identifier and search type from the arguments
identifier = args.identifier
search_by = args.search_by
output_format = args.output_format

# Check if the search identifier is a valid BSSID
if search_by == 'bssid':
    if not is_valid_bssid(identifier):
        console.print(' [:red_circle:] Error: Invalid BSSID')
        exit(1)

# Search for information about the network
if search_by == 'bssid':
    search_results = search_networks(identifier)
elif search_by == 'ssid':
    search_results = search_networks(ssid=identifier)

print_results_table(search_results)

# Save the search results in the specified output format
if output_format == 'map':
    # Create a map with markers for the search results
    map = create_map(search_results)
    # Save the map to an HTML file
    map.save('results/' + str(args.identifier).replace(':', '_') + '.html')
    filepath = os.getcwd()
    console.print(' [:green_circle:] [bright_yellow]Map saved at[/bright_yellow]: [bright_blue]' + str(
        filepath) + '\\results\\' + str(args.identifier).replace(':', '_') + '.html[/bright_blue]')
    print()
elif output_format == 'json':
    # Save the search results to a JSON file
    with open('results/' + str(args.identifier).replace(':', '_') + '.json', 'w') as outfile:
        json.dump(search_results, outfile)
    filepath = os.getcwd()
    console.print(' [:green_circle:] [bright_yellow]Json file saved at[/bright_yellow]: [bright_blue]' + str(
        filepath) + '\\results\\' + str(args.identifier).replace(':', '_') + '.json[/bright_blue]')
    print()

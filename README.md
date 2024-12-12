
# 📡💘🌎 | geowifi  

Search WiFi geolocation data by BSSID and SSID on different public databases.

![geowifi](https://imgur.com/C4eZL2P.png)

### 💾 Databases


| **[Wigle](https://wigle.net/)**       | **Apple**                           | **[Google](https://developers.google.com/maps/documentation/geolocation/overview)** | **[Milnikov](https://www.mylnikov.org/)**             |
|---------------------------------------|-------------------------------------|-------------------------------------------------------------------------------------|-------------------------------------------------------|
| **[WifiDB](https://www.wifidb.net/)** | **[Combain](https://combain.com/)** | **[Freifunk Carte](https://www.freifunk-karte.de/)**                                | **❌ (Discontinued) [OpenWifi](https://openwifi.su/)** |

---

## ✔️Prerequisites

- [Python3](https://www.python.org/download/releases/3.0/).
- In order to display emojis on **Windows**, it is recommended to install the [new Windows terminal](https://www.microsoft.com/en-us/p/windows-terminal/9n0dx20hk701).

---

## 🔑 APIs and configuration file

The tool has a configuration file in the `gw_utils` folder called **config.yaml**. Each of the configuration parameters and how to obtain the necessary information is explained below:


- ### **wigle_auth**: 
In order to use the Wigle service it is necessary to [obtain an API](https://api.wigle.net/)  and configure the `gw_utils/config.yaml` file replacing the value of the "**wigle_auth**" parameter for the "**Encoded for use**" data [provided by Wigle](https://wigle.net/account).

- ### **google_api**: 
In order to use the [Google Geolocation Services](https://developers.google.com/maps/documentation/geolocation/overview) it is necessary to [obtain an API](https://developers.google.com/maps/documentation/geolocation/get-api-key)  and configure the `gw_utils/config.yaml` file replacing the value of the "**google_api**" parameter for the "**API**" provided. Google provides $200 of free monthly usage.

- ### **combain_api**: 
In order to use the [Combain API](https://combain.com/api/) it is necessary to [obtain an API](https://portal.combain.com/#/auth/register)  and configure the `gw_utils/config.yaml` file replacing the value of the "**combain_api**" parameter for the "**API**" provided. Combain provides a free trial and paid plans.


- ### **no-ssl-verify**: 
Option to enable or disable the SSL verification process on requests.

---

## 🛠️ Installation

Start by cloning locally the GitHub repo then enter into the geowifi folder.
git must be present on your system
```bash
git clone https://github.com/GONZOsint/geowifi
cd ./geowifi/
```

Alternative is to use https://github.com/GONZOsint/geowifi/archive/refs/heads/main.zip then unzip the downloaded file.

### Use local Python ##

Note: Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.

```bash
virtualenv geowifi
source geowifi/bin/activate
python3 -m pip install -r requirements.txt
```

### Docker ###

```bash
docker build -t geowifi:latest .
```

---

## 🔎 Usage

```
usage: geowifi.py [-h] [-s {bssid,ssid}] [-o {map,json}] identifier

Search for information about a network with a specific BSSID or SSID.

positional arguments:
  identifier            The BSSID or SSID of the network to search for.

options:
  -h, --help            show this help message and exit
  -s {bssid,ssid}, --search-by {bssid,ssid}
                        Specifies whether to search by BSSID or SSID (default: bssid)
  -o {map,json}, --output-format {map,json}
                        Specifies the output format for the search results (default: map)
```

- Search by BSSID:

```
python3 geowifi.py -s bssid <input>
```

- Search by SSID:

```
python3 geowifi.py -s ssid <input>
```

It is possible to export the results in json format using the `-o json` parameter and show the locations on html map using `-o map`.

### 🐳 Docker usage ###

```bash
docker run --rm geowifi:latest
```

- Search by BSSID:

```bash
docker run --rm geowifi:latest -s bssid <input>
```

- Search by SSID:

```bash
docker run --rm geowifi:latest -s ssid <input>
```

### 🗺️ Map output example

![Map output](https://imgur.com/CilV4LR.png)

### 💾 Json output example

```json
[
  {
    "module": "google", 
    "bssid": "C8:XX:XX:XX:5E:45", 
    "latitude": 33.571844, 
    "longitude": -1XX.XXXXX97
  }, 
  {
    "module": "combain", 
    "error": "Not enough witooth"}, 
  {
    "module": "mylnikov", 
    "error": "Object was not found"
  },
  {
    "module": "vendor_check", 
    "vendor": "Cisco-Linksys, LLC"}, 
  {
    "module": "apple", 
    "bssid": "C8:XX:XX:XX:5E:45", 
    "latitude": 33.57198715, 
    "longitude": -1XX.XXXXX12}, 
  {
    "module": "wigle", 
    "bssid": "C8:XX:XX:XX:5E:45", 
    "ssid": "Vertigo", 
    "latitude": 33.60998154, 
    "longitude": -1XX.XXXXX22}, 
  {
    "module": "wifidb", 
    "bssid": "C8:XX:XX:XX:5E:45", 
    "ssid": "Vertigo", 
    "latitude": 33.6109, 
    "longitude": -1XX.XXXXX533
  }
]
```

---

## 📢 Mentions

- This project uses some of the research and code used at [iSniff-GPS](https://github.com/hubert3/iSniff-GPS).
- Thanks to [Micah Hoffman](https://twitter.com/WebBreacher) for his attention and answers to my questions.
- Thanks to [kennbro](https://twitter.com/kennbroorg) for lending me his scrupulous eyes to give me feedback.

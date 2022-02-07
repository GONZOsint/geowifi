# geowifi
![geowifi](https://imgur.com/pKOkeI6.png)

🌎 Search WiFi geolocation data by BSSID and SSID on different public databases.

### Databases:
- Wigle (https://wigle.net/)
- Apple
- OpenWifi (https://openwifi.su/)
- Milnikov (https://www.mylnikov.org/)
---

## ✔️ Prerequisites
- [Python3](https://www.python.org/download/releases/3.0/)
---

## 🛠️ Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.

```bash
python3 -m pip install -r requirements.txt
```

❗ In order to use the Wigle service it is necessary to [obtain an API](https://api.wigle.net/)  and configure the `utils/API.yaml`file with the value of the token.

## 🔎 Usage

```
usage: geowifi.py [-h] [-s SSID] [-b BSSID] [-j] [-m]


optional arguments:
  -h, --help               Show this help message and exit
  -s SSID, --ssid SSID     Search by SSID
  -b BSSID, --bssid BSSID  Search by BSSID
  -j, --json               Json output
  -m, --map                Map output
```
### 🗺️ Map output example
![Map output](https://imgur.com/rDBXmXv.png)
### 💾 Json output example
```json
{
   "data":{
      "bssid":"A0:XX:XX:XX:6F:90",
      "vendor":"TP-LINK TECHNOLOGIES CO.,LTD.",
      "mac_type":"MA-L",
      "wigle":{
         "lat":00.000908922099,
         "lon":00.000945220028
      },
      "apple":{
         "lat":"not_found",
         "lon":"not_found"
      },
      "openwifi":{
         "lat":00.000808900099,
         "lon":00.000845500028
      },
      "milnikov":{
         "lat":"not_found",
         "lon":"not_found"
      }
   }
}
```



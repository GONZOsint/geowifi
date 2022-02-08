# 📡💘🌎 | geowifi  

Search WiFi geolocation data by BSSID and SSID on different public databases.

![geowifi](https://imgur.com/pKOkeI6.png)

### 💾 Databases:
- [Wigle](https://wigle.net/)
- Apple
- [OpenWifi](https://openwifi.su/)
- [Milnikov](https://www.mylnikov.org/)
---


## ✔️ Prerequisites
- [Python3](https://www.python.org/download/releases/3.0/).
- In order to display emojis on **Windows**, it is recommended to install the [new Windows terminal](https://www.microsoft.com/en-us/p/windows-terminal/9n0dx20hk701).
- ⚠️ In order to use the Wigle service it is necessary to [obtain an API](https://api.wigle.net/)  and configure the `utils/API.yaml` file with the value of the "**Encoded for use**" parameter provided by Wigle.  **This is necessary for searching by SSID**. 

---


## 🛠️ Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.

```bash
python3 -m pip install -r requirements.txt
```


---


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
- Search by BSSID: 
```
python3 geowifi.py -b BSSID
```

- Search by SSID: 
```
python3 geowifi.py -s SSID
```


It is possible to export the result in json using the `-j` parameter and show the results in a map using `-m`.

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

---


## 📢 Mentions

- This project uses some of the research and code used at [iSniff-GPS](https://github.com/hubert3/iSniff-GPS).
- Thanks to [Micah Hoffman](https://twitter.com/WebBreacher) for his attention and answers to my questions.

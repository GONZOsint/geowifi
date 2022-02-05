import folium


def create_map():
    global m
    m = folium.Map(location=[39.600441, -41.141473], zoom_start=3,
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google')


def add_marker(lat, long, mac):
    global m
    folium.Marker(location=[lat, long], popup=mac).add_to(m)


def save_map(name):
    global m
    m.save(name)

import dbus
import nmobject

DBUS_INTERFACE_ACCESS_POINT = "org.freedesktop.NetworkManager.AccessPoint"

def mode_to_str(mode):
    if mode == 0:
        return "Automatic mode controlled by the driver"
    elif mode == 1:
        return "adhoc, single cell network"
    elif mode == 2:
        return "Multi cell network, roaming"
    elif mode == 3:
        return "Synchronisation master or Access Point"
    elif mode == 3:
        return "Wireless Repeater (forwarder)"
    elif mode == 4:
        return "Secondary master/repeater (backup)"
    elif mode == 5:
        return "Passive monitor (listen only)"
    else:
        return "(unknown)"

def ap_flags_to_str(flags):
    if flags:
        return "Yes"
    else:
        return "No"

def ap_sec_to_str(sec):
    if sec == 0:
        return "None"

    list = []
    if sec & 0x1:
        list.append("pairwise 40-bit WEP")
    if sec & 0x2:
        list.append("pairwise 104-bit WEP")
    if sec & 0x4:
        list.append("pairwise TKIP")
    if sec & 0x8:
        list.append("pairwise CCMP")
    if sec & 0x10:
        list.append("group 40-bit WEP")
    if sec & 0x20:
        list.append("group 104-bit WEP")
    if sec & 0x40:
        list.append("group TKIP")
    if sec & 0x80:
        list.append("group CCMP")
    if sec & 0x100:
        list.append("PSK")
    if sec & 0x200:
        list.append("802.1X")

    return ", ".join(list)


class AP(nmobject.NMObject):
    def __init__(self, path):
        nmobject.NMObject.__init__(self, path)

        # Connect signal handlers
        self.proxy.connect_to_signal("PropertiesChanged", self.on_properties_changed,
                                     dbus_interface=DBUS_INTERFACE_ACCESS_POINT)

    def get_ssid(self):
        return self.get_property(DBUS_INTERFACE_ACCESS_POINT, "Ssid")

    def get_flags(self):
        return self.get_property(DBUS_INTERFACE_ACCESS_POINT, "Flags")

    def get_wpa_flags(self):
        return self.get_property(DBUS_INTERFACE_ACCESS_POINT, "WpaFlags")

    def get_rsn_flags(self):
        return self.get_property(DBUS_INTERFACE_ACCESS_POINT, "RsnFlags")

    def get_frequency(self):
        return self.get_property(DBUS_INTERFACE_ACCESS_POINT, "Frequency")

    def get_hw_address(self):
        return self.get_property(DBUS_INTERFACE_ACCESS_POINT, "HwAddress")

    def get_mode(self):
        return self.get_property(DBUS_INTERFACE_ACCESS_POINT, "Mode")

    def get_max_bitrate(self):
        return self.get_property(DBUS_INTERFACE_ACCESS_POINT, "MaxBitrate")

    def get_strength(self):
        return self.get_property(DBUS_INTERFACE_ACCESS_POINT, "Strength")

    def on_properties_changed(self, props):
        pass

    def __str__(self):
        s = ""
        for c in self.get_ssid():
            s += chr(c)
        return s

    def get_properties(self):
        props = []
        props.append(("Protected", ap_flags_to_str(self.get_flags())))
        props.append(("WpaFlags", ap_sec_to_str(self.get_wpa_flags())))
        props.append(("RsnFlags", ap_sec_to_str(self.get_rsn_flags())))
        props.append(("Ssid", str(self)))
        props.append(("Frequency", str(self.get_frequency())))
        props.append(("HW Address", self.get_hw_address()))
        props.append(("Mode", mode_to_str(self.get_mode())))
        props.append(("Max Bitrate", str(self.get_max_bitrate())))
        props.append(("Strength", str(int(self.get_strength()))))

        return props

import dbus
import nm
import nmdevice
import nmap

DBUS_INTERFACE_DEVICE_WIRELESS = "org.freedesktop.NetworkManager.Device.Wireless"

def caps_to_str(caps):
    if caps == 0:
        return "(unknown)"

    list = []
    if caps & 0x1:
        list.append("40-bit WEP")
    if caps & 0x2:
        list.append("104-bit WEP")
    if caps & 0x4:
        list.append("TKIP")
    if caps & 0x8:
        list.append("CCMP")
    if caps & 0x10:
        list.append("WPA")
    if caps & 0x20:
        list.append("RSN")

    return ", ".join(list)


class WirelessDevice(nmdevice.Device):
    def __init__(self, path):
        nmdevice.Device.__init__(self, path)
        self.wireless_iface = dbus.Interface(self.proxy, dbus_interface=DBUS_INTERFACE_DEVICE_WIRELESS)

        # Connect signal handlers
        self.proxy.connect_to_signal("AccessPointAdded", self.on_access_point_added,
                                     dbus_interface=DBUS_INTERFACE_DEVICE_WIRELESS)
        self.proxy.connect_to_signal("AccessPointRemoved", self.on_access_point_removed,
                                     dbus_interface=DBUS_INTERFACE_DEVICE_WIRELESS)

    def __str__(self):
        return "WiFi"

    def get_access_points(self):
        l = []
        for ap_path in self.wireless_iface.GetAccessPoints():
            l.append (nmap.AP(ap_path))

        return l

    def get_hw_address(self):
        return self.get_property(DBUS_INTERFACE_DEVICE_WIRELESS, "HwAddress")

    def get_mode(self):
        return self.get_property(DBUS_INTERFACE_DEVICE_WIRELESS, "Mode")

    def get_bitrate(self):
        return self.get_property(DBUS_INTERFACE_DEVICE_WIRELESS, "Bitrate")

    def get_active_access_point(self):
        ap_path = self.get_property(DBUS_INTERFACE_DEVICE_WIRELESS, "ActiveAccessPoint")
        if ap_path and ap_path != "/":
            return nmap.AP(ap_path)
        return None

    def get_wireless_capabilities(self):
        return self.get_property(DBUS_INTERFACE_DEVICE_WIRELESS, "WirelessCapabilities")

    def on_access_point_added(self, ap_path):
        print "ap added: %s" % ap_path

    def on_access_point_removed(self, ap_path):
        print "ap removed: %s" % ap_path

    def get_properties(self):
        props = nmdevice.Device.get_properties(self)

        proxy = self.bus.get_object(nm.DBUS_SERVICE, self.path)
        iface = dbus.Interface(proxy, dbus_interface="org.freedesktop.DBus.Properties")

        props.append(("HWAddress", self.get_hw_address()))
        props.append(("Mode", nmap.mode_to_str(self.get_mode())))
        props.append(("Bitrate", str(self.get_bitrate())))
        props.append(("WirelessCapabilities", caps_to_str(self.get_wireless_capabilities())))

        return props

    def get_specific_object(self, args):
        ssid = args.pop(0)
        for ap in self.get_access_points():
            if str(ap) == ssid:
                return ap

        # Didn't find any, maybe it's hidden? Let NM figure out.
        return None


nm.register_device_type(2, WirelessDevice)


# FIXME: These don't belong here

class GsmDevice(nmdevice.Device):
    def __init__(self, path):
        nmdevice.Device.__init__(self, path)

    def __str__(self):
        return "GSM"

nm.register_device_type(3, GsmDevice)


class CdmaDevice(nmdevice.Device):
    def __init__(self, path):
        nmdevice.Device.__init__(self, path)

    def __str__(self):
        return "CDMA"

nm.register_device_type(4, CdmaDevice)

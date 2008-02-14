import dbus
import nm
import nmdevice

DBUS_INTERFACE_DEVICE_WIRED = "org.freedesktop.NetworkManager.Device.Wired"

class WiredDevice(nmdevice.Device):
    def __init__(self, path):
        nmdevice.Device.__init__(self, path)

    def get_hw_address(self):
        return self.get_property(DBUS_INTERFACE_DEVICE_WIRED, "HwAddress")

    def get_speed(self):
        return self.get_property(DBUS_INTERFACE_DEVICE_WIRED, "Speed")

    def __str__(self):
        return "ethernet"

    def get_properties(self):
        props = nmdevice.Device.get_properties(self)

        props.append(("HWAddress", self.get_hw_address()))
        props.append(("Speed", str(self.get_speed())))

        return props


nm.register_device_type(1, WiredDevice)

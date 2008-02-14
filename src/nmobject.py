import dbus
import nm

class NMObject:
    def __init__(self, path):
        self.bus = dbus.SystemBus()
        self.path = path
        self.proxy = self.bus.get_object(nm.DBUS_SERVICE, path)
        self.prop_iface = dbus.Interface(self.proxy, dbus_interface="org.freedesktop.DBus.Properties")

    def get_property(self, iface, property_name):
        return self.prop_iface.Get(iface, property_name)

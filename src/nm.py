import dbus
import nmobject
import nmdevice
import nmsettings

DBUS_SERVICE   = "org.freedesktop.NetworkManager"
DBUS_PATH      = "/org/freedesktop/NetworkManager"
DBUS_INTERFACE = "org.freedesktop.NetworkManager"

MANAGER_STATE_UNKNOWN      = 0
MANAGER_STATE_SLEEPING     = 1
MANAGER_STATE_CONNECTING   = 2
MANAGER_STATE_CONNECTED    = 3
MANAGER_STATE_DISCONNECTED = 4

def manager_state_to_str(status):
    if status == MANAGER_STATE_SLEEPING:
        return "sleeping"
    elif status == MANAGER_STATE_CONNECTING:
        return "connecting"
    elif status == MANAGER_STATE_CONNECTED:
        return "connected"
    elif status == MANAGER_STATE_DISCONNECTED:
        return "disconnected"
    else:
        return "(unknown)"


class NetworkManager(nmobject.NMObject):
    def __init__(self):
        nmobject.NMObject.__init__(self, DBUS_PATH)
        self.nm_iface = dbus.Interface(self.proxy, dbus_interface=DBUS_INTERFACE)

        # Connect signal handlers
        self.proxy.connect_to_signal("StateChange", self.on_state_change,
                                     dbus_interface=DBUS_INTERFACE)
        self.proxy.connect_to_signal("DeviceAdded", self.on_device_added,
                                     dbus_interface=DBUS_INTERFACE)
        self.proxy.connect_to_signal("DeviceRemoved", self.on_device_removed,
                                     dbus_interface=DBUS_INTERFACE)

    def _create_device(self, path):
        proxy = self.bus.get_object(DBUS_SERVICE, path)
        iface = dbus.Interface(proxy, dbus_interface="org.freedesktop.DBus.Properties")
        dev_type = iface.Get(nmdevice.DBUS_INTERFACE_DEVICE, "DeviceType")

        if not registered_devices.has_key(dev_type):
            nmtalk.fatal("Unknown device type '%d'" % dev_type)

        ctor = registered_devices[dev_type]
        return ctor(path)

    def get_devices(self):
        list = []
        for path in self.nm_iface.GetDevices():
            list.append(self._create_device((path)))

        return list

    def get_device_by_iface(self, dev_iface):
        for device in self.get_devices():
            if device.get_interface() == dev_iface:
                return device
        return None

    def get_active_connections(self):
        result = []

        list = self.nm_iface.GetActiveConnections()
        for item in list:
            (setting_service, connection_path, specific_object_path, dev_path_list) = item

            connection = nmsettings.Connection(self.bus, setting_service, connection_path)

            dev_list = []
            for dev_path in dev_path_list:
                dev_list.append(self._create_device(dev_path))
            result.append((connection, dev_list, specific_object_path))

        return result

    def activate_device(self, device, connection, specific_object=None):
        if specific_object:
            specific_object_path = specific_object.path
        else:
            specific_object_path = "/"

        self.nm_iface.ActivateDevice(device.path, connection.service, connection.path, specific_object_path)

    def sleep(self, sleep):
        self.nm_iface.Sleep(sleep)

    def get_state(self):
        return self.get_property(DBUS_INTERFACE, "State")

    def get_wireless_state(self):
        return self.get_property(DBUS_INTERFACE, "WirelessEnabled")

    def set_wireless_state(self, enabled):
        self.prop_iface.Set(DBUS_INTERFACE, "WirelessEnabled", enabled)

    def get_wireless_hw_state(self):
        return self.get_property(DBUS_INTERFACE, "WirelessHardwareEnabled")

    def on_state_change(self, state):
        print "State changed: %s" % manager_state_to_str(state)

    def on_device_added(self, device_path):
        print "Device added: %s" % device_path

    def on_device_removed(self, device_path):
        print "Device removed %s" % device_path


###############################################################################

registered_devices = {}

def register_device_type(device_type, ctor):
    global registered_devices
    registered_devices[device_type] = ctor

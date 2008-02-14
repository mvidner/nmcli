import dbus
import nm
import nmobject
import nmformat
import nmtalk
import nmip4config

DBUS_INTERFACE_DEVICE = "org.freedesktop.NetworkManager.Device"

DEVICE_STATE_UNKNOWN      = 0
DEVICE_STATE_DOWN         = 1
DEVICE_STATE_DISCONNECTED = 2
DEVICE_STATE_PREPARE      = 3
DEVICE_STATE_CONFIG       = 4
DEVICE_STATE_NEED_AUTH    = 5
DEVICE_STATE_IP4_CONFIG   = 6
DEVICE_STATE_ACTIVATED    = 7
DEVICE_STATE_FAILED       = 8
DEVICE_STATE_CANCELLED    = 9

DEVICE_CAP_NONE           = 0
DEVICE_CAP_SUPPORTED      = 0x01
DEVICE_CAP_CARRIER_DETECT = 0x02


def device_state_to_str(state):
    if state == DEVICE_STATE_DOWN:
        return "down"
    elif state == DEVICE_STATE_DISCONNECTED:
        return "disconnected"
    elif state == DEVICE_STATE_PREPARE:
        return "prepare"
    elif state == DEVICE_STATE_CONFIG:
        return "config"
    elif state == DEVICE_STATE_NEED_AUTH:
        return "need authentication"
    elif state == DEVICE_STATE_IP4_CONFIG:
        return "ip config"
    elif state == DEVICE_STATE_ACTIVATED:
        return "activated"
    elif state == DEVICE_STATE_FAILED:
        return "failed"
    elif state == DEVICE_STATE_CANCELLED:
        return "cancelled"
    else:
        return "(unknown)"


def device_cap_to_str(caps):
    if caps == DEVICE_CAP_NONE:
        return "none"

    list = []
    if caps & DEVICE_CAP_SUPPORTED:
        list.append("supported")
    if caps & DEVICE_CAP_CARRIER_DETECT:
        list.append("carrier detect")

    return ", ".join(list)


class Device(nmobject.NMObject):
    def __init__(self, path):
        nmobject.NMObject.__init__(self, path)
        self.device_iface = dbus.Interface(self.proxy, dbus_interface=DBUS_INTERFACE_DEVICE)

        # Connect signal handlers
        #self.proxy.connect_to_signal("StateChanged", self.on_state_changed, dbus_interface=DBUS_INTERFACE_DEVICE)
        self.proxy.connect_to_signal("CarrierChanged", self.on_carrier_changed, dbus_interface=DBUS_INTERFACE_DEVICE)

    def deactivate(self):
        self.device_iface.Deactivate()

    def get_udi(self):
        return self.get_property(DBUS_INTERFACE_DEVICE, "Udi")

    def get_interface(self):
        return self.get_property(DBUS_INTERFACE_DEVICE, "Interface")

    def get_driver(self):
        return self.get_property(DBUS_INTERFACE_DEVICE, "Driver")

    def get_capabilities(self):
        return self.get_property(DBUS_INTERFACE_DEVICE, "Capabilities")

    def get_state(self):
        return self.get_property(DBUS_INTERFACE_DEVICE, "State")

    def get_ip4_config(self):
        conf_path = self.get_property(DBUS_INTERFACE_DEVICE, "Ip4Config")
        if conf_path and conf_path != "/":
            return nmip4config.Ip4Config(conf_path)
        return None

    def get_carrier(self):
        return self.get_property(DBUS_INTERFACE_DEVICE, "Carrier")

    def on_state_changed(self, state):
        print "Device '%s' state changed: %s" % (self.get_interface(), device_state_to_str(state))

    def on_carrier_changed(self, carrier_on):
        print "Device carrier changed: %s" % nmformat.bool_to_str(carrier_on)

    def get_properties(self):
        props = []
        props.append(("Type", str(self)))
        props.append(("State", device_state_to_str(self.get_state())))
        props.append(("Udi", self.get_udi()))
        props.append(("Driver", self.get_driver()))
        props.append(("Capabilities", device_cap_to_str (self.get_capabilities())))
        props.append(("Carrier", nmformat.bool_to_str(self.get_carrier())))

        return props

    def get_specific_object(self, args):
        return None

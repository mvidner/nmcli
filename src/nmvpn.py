import dbus
import nmobject

DBUS_PATH_VPN                 = "/org/freedesktop/NetworkManager/VPN/Manager"
DBUS_INTERFACE_VPN            = "org.freedesktop.NetworkManager.VPN.Manager"
DBUS_PATH_VPN_CONNECTION      = "/org/freedesktop/NetworkManager/VPN/Connection"
DBUS_INTERFACE_VPN_CONNECTION = "org.freedesktop.NetworkManager.VPN.Connection"

VPN_CONNECTION_STATE_UNKNOWN       = 0
VPN_CONNECTION_STATE_PREPARE       = 1
VPN_CONNECTION_STATE_NEED_AUTH     = 2
VPN_CONNECTION_STATE_CONNECT       = 3
VPN_CONNECTION_STATE_IP_CONFIG_GET = 4
VPN_CONNECTION_STATE_ACTIVATED     = 5
VPN_CONNECTION_STATE_FAILED        = 6
VPN_CONNECTION_STATE_DISCONNECTED  = 7

VPN_CONNECTION_STATE_REASON_UNKNOWN               = 0
VPN_CONNECTION_STATE_REASON_NONE                  = 1
VPN_CONNECTION_STATE_REASON_USER_DISCONNECTED     = 2
VPN_CONNECTION_STATE_REASON_DEVICE_DISCONNECTED   = 3
VPN_CONNECTION_STATE_REASON_SERVICE_STOPPED       = 4
VPN_CONNECTION_STATE_REASON_IP_CONFIG_INVALID     = 5
VPN_CONNECTION_STATE_REASON_CONNECT_TIMEOUT       = 6
VPN_CONNECTION_STATE_REASON_SERVICE_START_TIMEOUT = 7
VPN_CONNECTION_STATE_REASON_SERVICE_START_FAILED  = 8
VPN_CONNECTION_STATE_REASON_NO_SECRETS            = 9


def vpn_connection_state_to_str(state):
    if state == VPN_CONNECTION_STATE_PREPARE:
        return "Preparing"
    elif state == VPN_CONNECTION_STATE_NEED_AUTH:
        return "Need authentication information"
    elif state == VPN_CONNECTION_STATE_CONNECT:
        return "Connecting"
    elif state == VPN_CONNECTION_STATE_IP_CONFIG_GET:
        return "Getting IP configuration"
    elif state == VPN_CONNECTION_STATE_ACTIVATED:
        return "Activated"
    elif state == VPN_CONNECTION_STATE_FAILED:
        return "Failed"
    elif state == VPN_CONNECTION_STATE_DISCONNECTED:
        return "Disconnected"
    else:
        return "(unknown)"


def vpn_connection_state_reason_to_str(reason):
    if reason == VPN_CONNECTION_STATE_REASON_NONE:
        return "None"
    elif reason == VPN_CONNECTION_STATE_REASON_USER_DISCONNECTED:
        return "User disconnected"
    elif reason == VPN_CONNECTION_STATE_REASON_DEVICE_DISCONNECTED:
        return "Device disconnected"
    elif reason == VPN_CONNECTION_STATE_REASON_SERVICE_STOPPED:
        return "Service stopped"
    elif reason == VPN_CONNECTION_STATE_REASON_IP_CONFIG_INVALID:
        return "Invalid IP configuration"
    elif reason == VPN_CONNECTION_STATE_REASON_CONNECT_TIMEOUT:
        return "Connection timed out"
    elif reason == VPN_CONNECTION_STATE_REASON_SERVICE_START_TIMEOUT:
        return "Starting VPN service timed out"
    elif reason == VPN_CONNECTION_STATE_REASON_SERVICE_START_FAILED:
        return "Starting VPN service failed"
    elif reason == VPN_CONNECTION_STATE_REASON_NO_SECRETS:
        return "No secrets provided"
    else:
        return "(unknown)"


class VpnConnection(nmobject.NMObject):
    def __init__(self, path):
        nmobject.NMObject.__init__(self, path)
        self.vpn_iface = dbus.Interface(self.proxy, dbus_interface=DBUS_INTERFACE_VPN_CONNECTION)

        # Connect signal handlers
        #self.proxy.connect_to_signal("StateChanged", self.on_state_changed, 
        #                             dbus_interface=DBUS_INTERFACE_VPN_CONNECTION)


    def disconnect(self):
        self.vpn_iface.Disconnect()

    def get_name(self):
        return self.get_property(DBUS_INTERFACE_VPN_CONNECTION, "Name")

    def get_state(self):
        return self.get_property(DBUS_INTERFACE_VPN_CONNECTION, "State")

    def get_banner(self):
        return self.get_property(DBUS_INTERFACE_VPN_CONNECTION, "Banner")

    def on_state_changed(self, state, reason):
        print "VPN connection state changed: %s (%s)" % (vpn_connection_state_to_str(state),
                                                         vpn_connection_state_reason_to_str(reason))


class VpnManager(nmobject.NMObject):
    def __init__(self):
        nmobject.NMObject.__init__(self, DBUS_PATH_VPN)
        self.vpn_iface = dbus.Interface(self.proxy, dbus_interface=DBUS_INTERFACE_VPN)

    def list_active_connections(self):
        list = []
        for path in self.vpn_iface.ListConnections():
            list.append(VpnConnection(path))
        return list

    def get_active_connection_by_name(self, name):
        for c in self.list_active_connections():
            if c.get_name() == name:
                return c

        return None

    def connect(self, connection, device):
        path = self.vpn_iface.Connect(connection.service, connection.path, device.path)
        if path:
            return VpnConnection(path)
        return None

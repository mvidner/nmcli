import dbus

DBUS_SERVICE_USER_SETTINGS   = "org.freedesktop.NetworkManagerUserSettings"
DBUS_SERVICE_SYSTEM_SETTINGS = "org.freedesktop.NetworkManagerSystemSettings"
DBUS_IFACE_SETTINGS          = "org.freedesktop.NetworkManagerSettings"
DBUS_PATH_SETTINGS           = "/org/freedesktop/NetworkManagerSettings"

DBUS_IFACE_SETTINGS_CONNECTION = "org.freedesktop.NetworkManagerSettings.Connection"


class Connection:
    def __init__(self, bus, service, path):
        self.bus = bus
        self.service = service
        self.path = path
        self.proxy = bus.get_object(service, path)
        self.con_iface = dbus.Interface(self.proxy, dbus_interface=DBUS_IFACE_SETTINGS_CONNECTION)

    def get_id(self):
        return self.con_iface.GetID()

    def get_settings(self):
        return self.con_iface.GetSettings()

    def get_setting_by_type(self, type):
        settings = self.con_iface.GetSettings()
        if settings:
            return settings.get(type)
        return None

    def get_type(self):
        connection_setting = self.get_setting_by_type("connection")
        if connection_setting:
            return connection_setting.get("type")
        return None


class ConnectionManager:

    def get_connections(self, service, type=None):
        bus = dbus.SystemBus()
        try:
            proxy = bus.get_object(service, DBUS_PATH_SETTINGS)
        except Exception:
            # looks like the settings daemon isn't running, no problem
            return []

        iface = dbus.Interface(proxy, dbus_interface=DBUS_IFACE_SETTINGS)

        list = []
        con_paths = iface.ListConnections()
        for path in con_paths:
            connection = Connection(bus, service, path)
            if not type or type == connection.get_type():
                list.append(connection)

        return list

    def get_connection_by_name(self, service, name, type=None):
        connections = self.get_connections(service, type)
        if not connections:
            return None

        for connection in connections:
            if connection.get_id() == name:
                return connection

        return None

import dbus
import nmformat
import nmobject

DBUS_INTERFACE_IP4_CONFIG = "org.freedesktop.NetworkManager.IP4Config"

class Ip4Config(nmobject.NMObject):
    def __init__(self, path):
        nmobject.NMObject.__init__(self, path)

    def get_address(self):
        return self.get_property(DBUS_INTERFACE_IP4_CONFIG, "Address")

    def get_gateway(self):
        return self.get_property(DBUS_INTERFACE_IP4_CONFIG, "Gateway")

    def get_netmask(self):
        return self.get_property(DBUS_INTERFACE_IP4_CONFIG, "Netmask")

    def get_broadcast(self):
        return self.get_property(DBUS_INTERFACE_IP4_CONFIG, "Broadcast")

    def get_hostname(self):
        return self.get_property(DBUS_INTERFACE_IP4_CONFIG, "Hostname")

    def get_nameservers(self):
        return self.get_property(DBUS_INTERFACE_IP4_CONFIG, "Nameservers")

    def get_domains(self):
        return self.get_property(DBUS_INTERFACE_IP4_CONFIG, "Domains")

    def get_nis_domain(self):
        return self.get_property(DBUS_INTERFACE_IP4_CONFIG, "NisDomain")

    def get_nis_servers(self):
        return self.get_property(DBUS_INTERFACE_IP4_CONFIG, "NisServers")

    def get_properties(self):
        props = []
        props.append(("Address", nmformat.ip4_address_to_str(self.get_address())))
        props.append(("Gateway", nmformat.ip4_address_to_str(self.get_gateway())))
        props.append(("Netmask", nmformat.ip4_address_to_str(self.get_netmask())))
        props.append(("Broadcast", nmformat.ip4_address_to_str(self.get_broadcast())))
        props.append(("Hostname", self.get_hostname()))

        for ns in self.get_nameservers():
            props.append(("Nameserver", nmformat.ip4_address_to_str(ns)))

        for domain in self.get_domains():
            props.append(("Domain", domain))

        props.append(("NIS domain", self.get_nis_domain()))

        for ns in self.get_nis_servers():
            props.append(("NIS server", nmformat.ip4_address_to_str(ns)))

        return props

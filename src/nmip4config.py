import dbus
import nmformat
import nmobject

DBUS_INTERFACE_IP4_CONFIG = "org.freedesktop.NetworkManager.IP4Config"

class Ip4Config(nmobject.NMObject):
    def __init__(self, path):
        nmobject.NMObject.__init__(self, path)

    def get_addresses(self):
        return self.get_property(DBUS_INTERFACE_IP4_CONFIG, "Addresses")

    def get_routes(self):
        return self.get_property(DBUS_INTERFACE_IP4_CONFIG, "Routes")

    def get_nameservers(self):
        return self.get_property(DBUS_INTERFACE_IP4_CONFIG, "Nameservers")

    def get_domains(self):
        return self.get_property(DBUS_INTERFACE_IP4_CONFIG, "Domains")

    def get_properties(self):
        props = []
        for (addr, mask, gw) in self.get_addresses():
            s = "%s/%s via %s" % (nmformat.ip4_address_to_str(addr),
                                  mask,
                                  nmformat.ip4_address_to_str(gw))
            props.append(("Address", s))

        for ns in self.get_nameservers():
            props.append(("Nameserver", nmformat.ip4_address_to_str(ns)))

        for domain in self.get_domains():
            props.append(("Domain", domain))

        for route in self.get_routes():
            props.append(("Route", route))

        return props

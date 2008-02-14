import gobject
import dbus
import nmcommand
import nmtalk
import nmformat
import nm
import nmdevice
import nmsettings
import nmvpn


class VpnListCmd(nmcommand.NmCommand):

    def name(self):
        return "vpn-list"

    def is_basic(self):
        return 1

    def aliases(self):
        return ["vl"]

    def description_short(self):
        return "List configured VPN profiles"

    def category(self):
        return "VPN"

    def local_opt_table(self):
        return [["s", "system", "", "Show system connections only"],
                ["u", "user",   "", "Show user connections only"]]

    def local_orthogonal_opts(self):
        return [["system", "user"]]

    def execute(self, options_dict, non_option_args):
        manager = nmsettings.ConnectionManager()

        if options_dict.has_key("system"):
            connections = manager.get_connections(nmsettings.DBUS_SERVICE_SYSTEM_SETTINGS, "vpn")
            print_service = False
        elif options_dict.has_key("user"):
            connections = manager.get_connections(nmsettings.DBUS_SERVICE_USER_SETTINGS, "vpn")
            print_service = False
        else:
            connections = manager.get_connections(nmsettings.DBUS_SERVICE_SYSTEM_SETTINGS, "vpn")
            connections += manager.get_connections(nmsettings.DBUS_SERVICE_USER_SETTINGS, "vpn")
            print_service = True

        vpn_manager = nmvpn.VpnManager()
        active_map = {}
        for c in vpn_manager.list_active_connections():
            active_map[c.get_name()] = nmvpn.vpn_connection_state_to_str(c.get_state())

        rows = []
        for connection in connections:
            name = connection.get_id()
            r = [name, active_map.get(name, "")]
            if print_service:
                if connection.service == nmsettings.DBUS_SERVICE_USER_SETTINGS:
                    r.append("User")
                else:
                    r.append("System")

            rows.append(r)

        if rows:
            headers = ["Name", "Status"]
            if print_service:
                headers.append("Service type")

            rows.sort(lambda x,y:cmp(x[0].lower(), y[0].lower()))
            nmformat.tabular(headers, rows)
        else:
            nmtalk.message("No VPN connections found.")

        return 0

nmcommand.register(VpnListCmd)


class VpnConnectCmd(nmcommand.NmCommand):

    def name(self):
        return "vpn-connect"

    def is_basic(self):
        return 1

    def aliases(self):
        return ["vc"]

    def description_short(self):
        return "Connect VPN"

    def category(self):
        return "VPN"

    def arguments(self):
        return "<VPN connection>"

    def local_opt_table(self):
        return [["s", "system", "", "Use connection from system connections"],
                ["u", "user",   "", "Use connection from user connections"],
                ["", "dont-wait", "" ,"Don't wait until the connection is estabilished"]]

    def local_orthogonal_opts(self):
        return [["system", "user"]]


    def execute(self, options_dict, non_option_args):
        if len(non_option_args) != 1:
            self.usage()

        # Find the VPN connection
        manager = nmsettings.ConnectionManager()
        connection_name = non_option_args.pop(0)

        if options_dict.has_key("system"):
            connection = manager.get_connection_by_name(nmsettings.DBUS_SERVICE_SYSTEM_SETTINGS,
                                                        connection_name, "vpn")
        elif options_dict.has_key("user"):
            connection = manager.get_connection_by_name(nmsettings.DBUS_SERVICE_USER_SETTINGS,
                                                        connection_name, "vpn")
        else:
            connection = manager.get_connection_by_name(nmsettings.DBUS_SERVICE_SYSTEM_SETTINGS,
                                                        connection_name, "vpn")
            if not connection:
                connection = manager.get_connection_by_name(nmsettings.DBUS_SERVICE_USER_SETTINGS,
                                                            connection_name, "vpn")

        if not connection:
            nmtalk.error("VPN connection '%s' not found." % connection_name)
            return 1

        manager = nm.NetworkManager()

        # Find the first active device
        device = None
        for d in manager.get_devices():
            if d.get_state() == nmdevice.DEVICE_STATE_ACTIVATED:
                device = d
                break

        if not device:
            nmtalk.fatal("Can not activate VPN, no active device found")

        vpn_manager = nmvpn.VpnManager()
        vpn_connection = vpn_manager.connect(connection, device)

        if options_dict.has_key("dont-wait"):
            return 0

        loop = gobject.MainLoop()
        self.exit_status = 0

        def monitor(state, reason):
            msg = "'%s': %s" % (connection_name, nmvpn.vpn_connection_state_to_str(state))
            if reason != nmvpn.VPN_CONNECTION_STATE_REASON_NONE:
                msg += " (%s)" % nmvpn.vpn_connection_state_reason_to_str(reason)

            nmtalk.message(msg)

            if state == nmvpn.VPN_CONNECTION_STATE_ACTIVATED:
                loop.quit()

            elif state == nmvpn.VPN_CONNECTION_STATE_FAILED or state == nmvpn.VPN_CONNECTION_STATE_DISCONNECTED:
                loop.quit()
                self.exit_status = 1

        vpn_connection.proxy.connect_to_signal("StateChanged", monitor,
                                                dbus_interface=nmvpn.DBUS_INTERFACE_VPN_CONNECTION)


        loop.run()

        return self.exit_status

nmcommand.register(VpnConnectCmd)


class VpnDisconnectCmd(nmcommand.NmCommand):

    def name(self):
        return "vpn-disconnect"

    def is_basic(self):
        return 1

    def aliases(self):
        return ["vd"]

    def description_short(self):
        return "Disconnect active VPN"

    def category(self):
        return "VPN"

    def arguments(self):
        return "<VPN connection>"

    def execute(self, options_dict, non_option_args):
        if len(non_option_args) != 1:
            self.usage()

        vpn_manager = nmvpn.VpnManager()
        connection = vpn_manager.get_active_connection_by_name(non_option_args[0])
        if not connection:
            nmtalk.error("VPN connection '%s' not found." % non_option_args[0])
            return 1

        connection.disconnect()

        return 0

nmcommand.register(VpnDisconnectCmd)

import gobject
import nmcommand
import nm
import nmdevice
import nmformat
import nmtalk
import nmsettings

class DeviceListCmd(nmcommand.NmCommand):

    def name(self):
        return "device-list"

    def is_basic(self):
        return 1

    def aliases(self):
        return ["dl"]

    def description_short(self):
        return "Get device list"

    def category(self):
        return "Device"

    def execute(self, options_dict, non_option_args):
        manager = self.Manager()
        device_list = manager.get_devices()

        if len(device_list) < 1:
            nmtalk.message("No devices found.")
            return 0

        table_rows = []

        for device in device_list:
            row = (device.get_interface(), str(device), nmdevice.device_state_to_str(device.get_state()))
            table_rows.append(row)

        nmformat.tabular(("Interface", "Type", "State"), table_rows)

        return 0

nmcommand.register(DeviceListCmd)


class DeviceInfoCmd(nmcommand.NmCommand):

    def name(self):
        return "device-info"

    def is_basic(self):
        return 1

    def aliases(self):
        return ["di"]

    def description_short(self):
        return "Get device properties"

    def category(self):
        return "Device"

    def arguments(self):
        return "<device> [device] ..."

    def execute(self, options_dict, non_option_args):
        if len(non_option_args) < 1:
            self.usage()

        manager = self.Manager()
        table_headers = ("Property", "Value")

        for device_iface in non_option_args:
            device = manager.get_device_by_iface(device_iface)
            if not device:
                nmtalk.error("Invalid device %s" % device_iface)
                continue

            props = device.get_properties()
            if len(non_option_args) > 1:
                print
                print "Device %s" % device_iface
                print
            nmformat.tabular(table_headers, props)

        return 0

nmcommand.register(DeviceInfoCmd)


class DeviceIpConfigCmd(nmcommand.NmCommand):

    def name(self):
        return "device-ipconfig"

    def is_basic(self):
        return 1

    def aliases(self):
        return ["dip"]

    def description_short(self):
        return "Get active device's IP4 configuration(s)"

    def category(self):
        return "Device"

    def arguments(self):
        return "<device> [device] ..."

    def execute(self, options_dict, non_option_args):
        if len(non_option_args) < 1:
            self.usage()

        manager = self.Manager()
        table_headers = ("Property", "Value")

        for device_iface in non_option_args:
            device = manager.get_device_by_iface(device_iface)
            if not device:
                nmtalk.error("Invalid device %s" % device_iface)
                continue

            config = device.get_ip4_config()
            if not config:
                nmtalk.error("Device has no IP4 config")
                continue

            props = config.get_properties()
            if len(non_option_args) > 1:
                print
                print "Device %s" % device_iface
                print
            nmformat.tabular(table_headers, props)

        return 0

nmcommand.register(DeviceIpConfigCmd)


class DeviceActivateCmd(nmcommand.NmCommand):

    def name(self):
        return "device-activate"

    def is_basic(self):
        return 1

    def aliases(self):
        return ["da"]

    def description_short(self):
        return "Activate the device"

    def category(self):
        return "Device"

    def arguments(self):
        return "<device> <connection> [device specific arguments]"

    def local_opt_table(self):
        return [["s", "system", "", "Use connection from system connections"],
                ["u", "user",   "", "Use connection from user connections"],
                ["", "dont-wait", "" ,"Don't wait until the connection is estabilished"]]

    def local_orthogonal_opts(self):
        return [["system", "user"]]

    def execute(self, options_dict, non_option_args):
        if len(non_option_args) < 2:
            self.usage()

        manager = self.Manager()

        # Device
        device_iface = non_option_args.pop(0)
        device = manager.get_device_by_iface(device_iface)
        if not device:
            nmtalk.fatal("Invalid device %s" % device_iface)

        # Connection
        c_manager = nmsettings.ConnectionManager()
        connection_name = non_option_args.pop(0)
        if options_dict.has_key("system"):
            connection = c_manager.get_connection_by_name(nmsettings.DBUS_SERVICE_SYSTEM_SETTINGS,
                                                          connection_name)
        elif options_dict.has_key("user"):
            connection = c_manager.get_connection_by_name(nmsettings.DBUS_SERVICE_USER_SETTINGS,
                                                          connection_name)
        else:
            connection = c_manager.get_connection_by_name(nmsettings.DBUS_SERVICE_SYSTEM_SETTINGS,
                                                          connection_name)
            if not connection:
                connection = c_manager.get_connection_by_name(nmsettings.DBUS_SERVICE_USER_SETTINGS,
                                                              connection_name)

        if not connection:
            nmtalk.fatal("Invalid connection '%s'" % connection_name)

        # Specific object
        if len(non_option_args) > 0:
            specific_object = device.get_specific_object(non_option_args)
        else:
            specific_object = None

        manager.activate_device(device, connection, specific_object)

        if options_dict.has_key("dont-wait"):
            return 0

        loop = gobject.MainLoop()
        self.exit_status = 0

        def monitor(state):
            nmtalk.message("'%s': %s" % (device_iface, nmdevice.device_state_to_str(state)))
            if state == nmdevice.DEVICE_STATE_ACTIVATED:
                loop.quit()

            elif state == nmdevice.DEVICE_STATE_FAILED or state == nmdevice.DEVICE_STATE_DISCONNECTED or \
                    state == nmdevice.DEVICE_STATE_CANCELLED:
                loop.quit()
                self.exit_status = 1

        device.proxy.connect_to_signal("StateChanged", monitor,
                                       dbus_interface=nmdevice.DBUS_INTERFACE_DEVICE)


        loop.run()

        return self.exit_status

nmcommand.register(DeviceActivateCmd)


class DeviceDeactivateCmd(nmcommand.NmCommand):

    def name(self):
        return "device-deactivate"

    def is_basic(self):
        return 1

    def aliases(self):
        return ["dd"]

    def description_short(self):
        return "Deactivate the device"

    def category(self):
        return "Device"

    def arguments(self):
        return "<device>"

    def execute(self, options_dict, non_option_args):
        if len(non_option_args) != 1:
            self.usage()

        manager = self.Manager()

        device_iface = non_option_args.pop(0)
        device = manager.get_device_by_iface(device_iface)
        if not device:
            nmtalk.fatal("Invalid device %s" % device_iface)

        device.deactivate()

        return 0

nmcommand.register(DeviceDeactivateCmd)

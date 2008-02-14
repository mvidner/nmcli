import nmcommand
import nmtalk
import nmformat
import nm
import nmap
import nmdevice
import nmwirelessdevicecmds

class APListCmd(nmcommand.NmCommand):

    def name(self):
        return "ap-list"

    def is_basic(self):
        return 1

    def aliases(self):
        return ["al"]

    def description_short(self):
        return "Get wireless device's AP list"

    def category(self):
        return "AP"

    def arguments(self):
        return " [device] ..."

    def execute(self, options_dict, non_option_args):
        manager = self.Manager()
        devices = []

        if len(non_option_args) < 1:
            # Get all wireless devices
            for device in manager.get_devices():
                if isinstance(device, nmwirelessdevicecmds.WirelessDevice):
                    devices.append(device)

        else:
            for device in manager.get_devices():
                for arg in non_option_args:
                    if device.get_interface() == arg:
                        if isinstance(device, nmwirelessdevicecmds.WirelessDevice):
                            devices.append(device)
                        else:
                            nmtalk.error("Wireless device expected, got %s" % str(device))

        got_devices = len(devices)

        if got_devices < 1:
            nmtalk.error("No wireless devices found.")
            return 1

        for device in devices:
            if got_devices > 1:
                nmtalk.message("Access Points for device '%s':" % device.get_interface())

            aps = device.get_access_points()

            if not aps:
                nmtalk.message("No access points found.")
                continue

            rows = []
            active_ap = device.get_active_access_point()
            if active_ap:
                active_ssid = active_ap.get_ssid()
            else:
                active_ssid = None

            for ap in aps:
                if active_ssid == ap.get_ssid():
                    active = "*"
                else:
                    active = ""

                rows.append ((str(ap), active))

            rows.sort(lambda x,y:cmp(x[0].lower(), y[0].lower()))
            nmformat.tabular(("SSID", "Active"), rows)

        return 0

nmcommand.register(APListCmd)


class APInfoCmd(nmcommand.NmCommand):

    def name(self):
        return "ap-info"

    def is_basic(self):
        return 1

    def aliases(self):
        return ["ai"]

    def description_short(self):
        return "Get AP properties"

    def category(self):
        return "AP"

    def arguments(self):
        return "<AP> [AP] ..."

    def find_aps(self, devices, ssids):
        result = {}
        for ssid in ssids:
            result[ssid] = None

        for device in devices:
            if not isinstance(device, nmwirelessdevicecmds.WirelessDevice):
                continue

            aps = device.get_access_points()
            if not aps:
                continue

            for ssid in ssids:
                for ap in aps:
                    if str(ap) == ssid:
                        result[ssid] = ap

        return result

    def execute(self, options_dict, non_option_args):
        if len(non_option_args) < 1:
            self.usage()

        manager = self.Manager()

        aps = self.find_aps(manager.get_devices(), non_option_args)
            
        found = 0
        table_headers = ("Property", "Value")

        for ssid in non_option_args:
            ap = aps[ssid]
            if not ap:
                nmtalk.error("Can not find AP %s" % ssid)
                continue

            found += 1
            props = ap.get_properties()
            nmformat.tabular(table_headers, props)

        if found == 0:
            return 1

        return 0

nmcommand.register(APInfoCmd)

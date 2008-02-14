import nmcommand
import nmformat
import nmtalk
import nm

class NetworkEnabledCmd(nmcommand.NmCommand):

    def name(self):
        return "network-enabled"

    def is_basic(self):
        return 1

    def aliases(self):
        return ["ne"]

    def description_short(self):
        return "Query or change NetworkManager status"

    def category(self):
        return "Basic"

    def arguments(self):
        return "[on|off]"

    def execute(self, options_dict, non_option_args):
        manager = self.Manager()
        current_state = manager.get_state()

        if len(non_option_args) < 1:
            if current_state == nm.MANAGER_STATE_SLEEPING:
                print "Disabled"
            else:
                print "Enabled"

            return 0

        new_state = non_option_args[0].lower()
        if new_state == "on" or new_state == "enable" or new_state == "yes" or new_state == "1":
            if current_state == nm.MANAGER_STATE_SLEEPING:
                nmtalk.message("Enabling networking")
                manager.sleep(False)
            else:
                nmtalk.message("Networking is already enabled")
        elif new_state == "off" or new_state == "disable" or new_state == "no" or new_state == 0:
            if current_state != nm.MANAGER_STATE_SLEEPING:
                nmtalk.message("Disabling networking")
                manager.sleep(True)
            else:
                nmtalk.message("Networking is already disabled")
        else:
            nmtalk.fatal("Invalid argument '%s'. Please use 'on' or 'off'" % non_option_args[0])

        return 0


nmcommand.register(NetworkEnabledCmd)


class WirelessEnabledCmd(nmcommand.NmCommand):

    def name(self):
        return "wireless-enabled"

    def is_basic(self):
        return 1

    def aliases(self):
        return ["we"]

    def description_short(self):
        return "Query or change wireless status"

    def category(self):
        return "Basic"

    def arguments(self):
        return "[on|off]"

    def execute(self, options_dict, non_option_args):
        manager = self.Manager()
        current_state = manager.get_wireless_state()

        if len(non_option_args) < 1:
            if current_state:
                print "Enabled"
            else:
                print "Disabled"
            return 0

        new_state = non_option_args[0].lower()
        if new_state == "on" or new_state == "enable" or new_state == "yes" or new_state == "1":
            if not current_state:
                if not manager.get_wireless_hw_state():
                    nmtalk.message("Wireless hardware is disabled, can not enable wireless")
                    return 1
                nmtalk.message("Enabling wireless")
                manager.set_wireless_state(True)
            else:
                nmtalk.message("Wireless is already enabled")
        elif new_state == "off" or new_state == "disable" or new_state == "no" or new_state == 0:
            if current_state:
                nmtalk.message("Disabling wireless")
                manager.set_wireless_state(False)
            else:
                nmtalk.message("Wireless is already disabled")
        else:
            nmtalk.fatal("Invalid argument '%s'. Please use 'on' or 'off'" % non_option_args[0])

        return 0


nmcommand.register(WirelessEnabledCmd)


class ReportCmd(nmcommand.NmCommand):
    
    def name(self):
        return "report"

    def is_basic(self):
        return 1

    def aliases(self):
        return ["re"]

    def description_short(self):
        return "Get the current NetworkManager status"

    def category(self):
        return "Basic"

    def execute(self, options_dict, non_option_args):
        manager = self.Manager()

        print "State: %s" % nm.manager_state_to_str(manager.get_state())
        print "Wireless Enabled: %s" % nmformat.bool_to_str(manager.get_wireless_state())
        print "Wireless hardware enabled: %s" % nmformat.bool_to_str(manager.get_wireless_hw_state())

        #print manager.get_active_connections()

        return 0


nmcommand.register(ReportCmd)

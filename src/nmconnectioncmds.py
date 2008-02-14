import nmformat
import nmcommand
import nmtalk
import nmsettings

class ConnectionListCmd(nmcommand.NmCommand):

    def name(self):
        return "connection-list"

    def is_basic(self):
        return 1

    def aliases(self):
        return ["cl"]

    def description_short(self):
        return "List connections"

    def category(self):
        return "Connection"

    def local_opt_table(self):
        return [["s", "system", "", "Show system connections only"],
                ["u", "user",   "", "Show user connections only"],
                ["", "sort-by-name", "", "Sort by name (default)"],
                ["", "sort-by-type", "", "Sort by type"]]

    def local_orthogonal_opts(self):
        return [["system", "user"],
                ["sort-by-name", "sort-by-type"]]

    def execute(self, options_dict, non_option_args):
        manager = nmsettings.ConnectionManager()

        if options_dict.has_key("system"):
            connections = manager.get_connections(nmsettings.DBUS_SERVICE_SYSTEM_SETTINGS)
            print_service = False
        elif options_dict.has_key("user"):
            connections = manager.get_connections(nmsettings.DBUS_SERVICE_USER_SETTINGS)
            print_service = False
        else:
            connections = manager.get_connections(nmsettings.DBUS_SERVICE_SYSTEM_SETTINGS)
            connections += manager.get_connections(nmsettings.DBUS_SERVICE_USER_SETTINGS)
            print_service = True

        rows = []
        for connection in connections:
            r = [connection.get_id(), connection.get_type()]
            if print_service:
                if connection.service == nmsettings.DBUS_SERVICE_USER_SETTINGS:
                    r.append("User")
                else:
                    r.append("System")

            rows.append(r)

        if rows:
            if options_dict.has_key("sort-by-type"):
                rows.sort(lambda x,y:cmp(x[1].lower(), y[1].lower()))
            else:
                rows.sort(lambda x,y:cmp(x[0].lower(), y[0].lower()))

            headers = ["Name", "Type"]
            if print_service:
                headers.append("Service type")

            nmformat.tabular(headers, rows)
        else:
            nmtalk.message("No connections found.")

        return 0

nmcommand.register(ConnectionListCmd)


class ConnectionInfoCmd(nmcommand.NmCommand):

    def name(self):
        return "connection-info"

    def is_basic(self):
        return 1

    def aliases(self):
        return ["ci"]

    def description_short(self):
        return "Connection properties"

    def category(self):
        return "Connection"

    def arguments(self):
        return "<connection> [connection] ..."

    def execute(self, options_dict, non_option_args):
        if not non_option_args:
            self.usage()

        manager = nmsettings.ConnectionManager()

        found = 0
        for name in non_option_args:
            connection = manager.get_connection_by_name(nmsettings.DBUS_SERVICE_USER_SETTINGS, name)
            if not connection:
                nmtalk.error("Can not find connection '%s'" % name)
                continue

            found += 1
            settings = connection.get_settings()
            for setting_type in settings.keys():
                print setting_type
                setting = settings[setting_type]
                for key in setting.keys():
                    print "%s : %s" % (key, setting[key])

                print

        if found == 0:
            return 1

        return 0

nmcommand.register(ConnectionInfoCmd)

#!/usr/bin/python

###
### Copyright 2002 Ximian, Inc.
###
### This program is free software; you can redistribute it and/or modify
### it under the terms of the GNU General Public License, version 2,
### as published by the Free Software Foundation.
###
### This program is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU General Public License for more details.
###
### You should have received a copy of the GNU General Public License
### along with this program; if not, write to the Free Software
### Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
###

import sys
import string
import getpass
import os
import traceback
import dbus

import nmtalk
import nmcommand

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

nm_name = "NetworkManager Command Line Client"
nm_copyright = "Copyright (C) 2008 Novell Inc.  All Rights Reserved."
nm_version = None

def import_commands(nm_dir):
    import glob, imp
    sysdir = nm_dir + "/commands"
    sys.path.append(sysdir)

    loaded_modules = []

    # First load modules in our current directory, for developers, and then
    # out of the system dir.
    files = glob.glob("*cmds.py")
    files = files + glob.glob("%s/*cmds.py" % sysdir)
    
    for file in files:
        (path, name) = os.path.split(file)
        (name, ext) = os.path.splitext(name)
        
        if name in loaded_modules:
            continue
        
        (file, filename, data) = imp.find_module(name, [path])

        try:
            module = imp.load_module(name, file, filename, data)
        except ImportError:
            nmtalk.warning("Can't import module " + filename)
        else:
            loaded_modules.append(name)

        if file:
            file.close()

def show_exception(e):
    if nmtalk.show_verbose:
        trace = ""
        exception = ""
        exc_list = traceback.format_exception_only (sys.exc_type, sys.exc_value)
        for entry in exc_list:
            exception += entry
            tb_list = traceback.format_tb(sys.exc_info()[2])
            for entry in tb_list:
                trace += entry

        nmtalk.error(str(e))
        nmtalk.error(trace)
    else:
        nmtalk.error(str(e))

def main(ver, nm_dir):

    global local
    global nm_version

    nm_version = ver

    if os.environ.has_key("NM_DEBUG"):
        nmtalk.show_debug = 1

    import_commands(nm_dir)

    ###
    ### Grab the option list and extract the first non-option argument that
    ### looks like a command.  This could get weird if someone passes the name
    ### of a command as the argument to an option.
    ###

    argv = sys.argv[1:]

    argv = nmcommand.expand_synthetic_args(argv)

    if "--version" in argv:
        print
        print nm_name + " " + nm_version
        print nm_copyright
        print
        sys.exit(0)

    command = nmcommand.extract_command_from_argv(argv)

    if "-?" in argv or "--help" in argv:
        command.usage()
        sys.exit(0)

    # A hack to suppress extra whitespace when dumping.
    if command.name() == "dump":
        nmtalk.be_terse = 1

    argv = nmcommand.get_user_default_args(argv, command)

    opt_dict, args = command.process_argv(argv)

    ###
    ### Control verbosity
    ###

    if opt_dict.has_key("terse"):
        nmtalk.be_terse = 1

    if opt_dict.has_key("quiet"):
        nmtalk.show_messages = 0
        nmtalk.show_warnings = 0

    if opt_dict.has_key("verbose"):
        nmtalk.show_verbose = 1

    ### Whitespace is nice, so we always print a blank line before
    ### executing the command

    if not nmtalk.be_terse:
        nmtalk.message("")

    try:
        command.execute(opt_dict, args)
    except IOError, e:
        if e.errno == 13:
            nmtalk.error("You must be root to execute this command")
        else:
            show_exception(e)

        sys.exit(1)
    except Exception, e:
        show_exception(e)
        sys.exit(1)

    ### Whitespace is nice, so we always print a blank line after
    ### executing the command

    if not nmtalk.be_terse:
        nmtalk.message("")




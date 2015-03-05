#! /usr/bin/env python
import gobject
import dbus
import dbus.mainloop.glib
import subprocess
from os.path import expanduser
import signal
import sys

from pprint import pprint
from pica import next_tik_type


def active_changed_handler(*args):
    tik()
stop_handler = active_changed_handler

def signal_handler(*args):
    tik()
    sys.exit(0)


def tik():
    cmd = [
        expanduser('~/.virtualenvs/pica/bin/python'),
        expanduser('~/dev/pica/pica.py'),
        'tik',
    ]
    subprocess.call(cmd)


if __name__ == '__main__':
    # handle Unix signals
    # (SIGKILL and SIGSTOP cannot be caught, blocked, or ignored)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGINT, signal_handler) # ctrl-c
    signal.signal(signal.SIGQUIT, signal_handler) # ctrl-\
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler) # ctrl-z
    # the remaining signals are considered fatal and are left unhandledal.signal(signal.SIGTERM, sigterm_handler)

    if next_tik_type() == 'in':
        tik()

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    bus.add_signal_receiver(
        active_changed_handler,
        dbus_interface="org.gnome.ScreenSaver",
        signal_name = "ActiveChanged")
    bus.add_signal_receiver(
        active_changed_handler,
        dbus_interface="org.gnome.SessionManager.ClientPrivate",
        signal_name = "Stop")
    loop = gobject.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        sys.exit(0)

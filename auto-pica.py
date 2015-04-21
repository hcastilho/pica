#! /usr/bin/env python
# https://github.com/backloop/gendsession/blob/master/gendsession.py
import logging
import dbus
import dbus.mainloop.glib
import gobject
import os
import signal
import sys

from pica import tik, next_tik_type

logging.basicConfig(
        filename='/home/hcastilho/dev/pica/pica.log',
        level=logging.DEBUG,
        format=('{"datetime": "%(asctime)s", '
                '"level": "%(levelname)s", '
                '"message": "%(message)s"}')
        )
logger = logging.getLogger()

fname = os.path.expanduser('~/dev/pica/time.yaml')

loop = None

def active_changed_handler(*args):
    logger.info('active_changed_handler {}'.format(args))
    tik(fname)
    logger.info('done')

def stop_handler(*args):
    logger.info('stop_handler {}'.format(args))
    tik(fname)
    logger.info('done')
    logger.info('exiting 1...')
    loop.stop()
    #sys.exit(0)

# SIGHUP 1
# SIGTERM 15
def signal_handler(*args):
    logger.info('signal_handler {}'.format(args))
    tik(fname)
    logger.info('done')
    logger.info('exiting 2...')
    sys.exit(0)


if __name__ == '__main__':
    logger.info('Starting')
    # handle Unix signals
    # (SIGKILL and SIGSTOP cannot be caught, blocked, or ignored)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGINT, signal_handler) # ctrl-c
    signal.signal(signal.SIGQUIT, signal_handler) # ctrl-\
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler) # ctrl-z
    # the remaining signals are considered fatal and are left unhandledal.signal(signal.SIGTERM, sigterm_handler)

    if next_tik_type() == 'in':
        logger.info('Startup tik')
        tik(fname)
        logger.info('done...')

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    bus.add_signal_receiver(
        active_changed_handler,
        dbus_interface="org.gnome.ScreenSaver",
        signal_name = "ActiveChanged")
    bus.add_signal_receiver(
        stop_handler,
        dbus_interface="org.gnome.SessionManager.ClientPrivate",
        signal_name = "Stop")
    loop = gobject.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        logger.info('exiting 1...')
        sys.exit(0)

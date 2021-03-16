'''systemd mock template

This variant is for using on the system bus.

It implements StartUnit, StartTransientUnit and StopUnit, but without starting
or stopping anything.
'''

# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option) any
# later version.  See http://www.gnu.org/copyleft/lgpl.html for the full text
# of the license.

__author__ = 'Jonas Ådahl'
__copyright__ = '(c) 2021 Red Hat'

from dbusmock import mockobject

systemd_base = mockobject.load_module('systemd-base')

BUS_NAME = systemd_base.BUS_NAME
MAIN_OBJ = systemd_base.MAIN_OBJ
MAIN_IFACE = systemd_base.MAIN_IFACE
SYSTEM_BUS = True


def load(mock, parameters):
    systemd_base.load_base(mock, parameters)

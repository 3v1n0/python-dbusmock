'''systemd mock template base
'''

# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option) any
# later version.  See http://www.gnu.org/copyleft/lgpl.html for the full text
# of the license.

__author__ = 'Jonas Ådahl'
__copyright__ = '(c) 2021 Red Hat'

import dbus

from dbusmock import MOCK_IFACE, mockobject

BUS_PREFIX = 'org.freedesktop.systemd1'
PATH_PREFIX = '/org/freedesktop/systemd1'


BUS_NAME = BUS_PREFIX
MAIN_OBJ = PATH_PREFIX
MAIN_IFACE = BUS_PREFIX + '.Manager'
UNIT_IFACE = BUS_PREFIX + '.Unit'


def load_base(mock, _parameters):
    mock.next_job_id = 1
    mock.units = {}

    mock.AddServiceMethod(MAIN_IFACE, 'StartUnit', StartUnit)
    mock.AddServiceMethod(MAIN_IFACE, 'StartTransientUnit', StartTransientUnit)
    mock.AddServiceMethod(MAIN_IFACE, 'StopUnit', StopUnit)
    mock.AddServiceMethod(MAIN_IFACE, 'GetUnit', GetUnit)
    mock.AddProperties(MAIN_IFACE, {'Version': 'v246'})

    mock.AddServiceMethod(MOCK_IFACE, 'AddMockUnit', AddMockUnit)


def escape_unit_name(name):
    for s in ['.', '-']:
        name = name.replace(s, '_')
    return name


def emit_job_new_remove(self, job_id, job_path, name):
    self.EmitSignal(MAIN_IFACE, 'JobNew', 'uos', [job_id, job_path, name])
    self.EmitSignal(MAIN_IFACE, 'JobRemoved', 'uoss',
                    [job_id, job_path, name, 'done'])


@dbus.service.method(MAIN_IFACE, in_signature='ss', out_signature='o',
                     async_callbacks=('ok_cb', 'err_cb'))
def StartUnit(self, name, _mode, ok_cb, err_cb):
    job_id = self.next_job_id
    self.next_job_id += 1

    job_path = PATH_PREFIX + '/Job/{}'.format(job_id)

    try:
        unit_path = self.units[str(name)]
    except KeyError as e:
        err_cb(e)
    unit = mockobject.objects[unit_path]
    unit.UpdateProperties(UNIT_IFACE, {'ActiveState': 'active'})

    ok_cb(job_path)
    emit_job_new_remove(self, job_id, job_path, name)


@dbus.service.method(MAIN_IFACE, in_signature='ssa(sv)a(sa(sv))', out_signature='o',
                     async_callbacks=('ok_cb', '_err_cb'))
def StartTransientUnit(self, name, _mode, _properties, _aux, ok_cb, _err_cb):
    job_id = self.next_job_id
    self.next_job_id += 1

    job_path = PATH_PREFIX + '/Job/%d' % (job_id)
    ok_cb(job_path)
    emit_job_new_remove(self, job_id, job_path, name)


@dbus.service.method(MAIN_IFACE, in_signature='ss', out_signature='o',
                     async_callbacks=('ok_cb', 'err_cb'))
def StopUnit(self, name, _mode, ok_cb, err_cb):
    job_id = self.next_job_id
    self.next_job_id += 1

    job_path = PATH_PREFIX + '/Job/%d' % (job_id)

    try:
        unit_path = self.units[str(name)]
    except KeyError as e:
        err_cb(e)
    unit = mockobject.objects[unit_path]
    unit.UpdateProperties(UNIT_IFACE, {'ActiveState': 'inactive'})

    ok_cb(job_path)
    emit_job_new_remove(self, job_id, job_path, name)


@dbus.service.method(MAIN_IFACE, in_signature='s', out_signature='o')
def GetUnit(self, name):
    unit_path = self.units[str(name)]
    return unit_path


@dbus.service.method(MOCK_IFACE, in_signature='s')
def AddMockUnit(self, name):
    unit_path = PATH_PREFIX + '/unit/%s' % (escape_unit_name(name))
    self.units[str(name)] = unit_path
    self.AddObject(unit_path,
                   UNIT_IFACE,
                   {
                       'Id': name,
                       'Names': [name],
                       'LoadState': 'loaded',
                       'ActiveState': 'inactive',
                   },
                   [])

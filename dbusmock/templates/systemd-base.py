'''systemd mock template base
'''

# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option) any
# later version.  See http://www.gnu.org/copyleft/lgpl.html for the full text
# of the license.

__author__ = 'Jonas Ådahl'
__copyright__ = '(c) 2021 Red Hat'

from gi.repository import GLib

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

    mock.AddMethod(MAIN_IFACE,
                   'StartUnit',
                   'ss', 'o',
                   'ret = self.StartUnit(self, *args)')
    mock.AddMethod(MAIN_IFACE,
                   'StartTransientUnit',
                   'ssa(sv)a(sa(sv))', 'o',
                   'ret = self.StartTransientUnit(self, *args)')
    mock.AddMethod(MAIN_IFACE,
                   'StopUnit',
                   'ss', 'o',
                   'ret = self.StopUnit(self, *args)')
    mock.AddMethod(MAIN_IFACE,
                   'GetUnit',
                   's', 'o',
                   'ret = self.GetUnit(self, *args)')
    mock.AddProperties(MAIN_IFACE, {'Version': 'v246'})

    mock.StartUnit = StartUnit
    mock.StartTransientUnit = StartTransientUnit
    mock.StopUnit = StopUnit
    mock.GetUnit = GetUnit

    mock.AddMethod(MOCK_IFACE, 'AddMockUnit', 's', '', 'self.AddMockUnit(self, *args)')

    mock.AddMockUnit = AddMockUnit


def escape_unit_name(name):
    for s in ['.', '-']:
        name = name.replace(s, '_')
    return name


def emit_job_new_remove(self, job_id, job_path, name):
    self.EmitSignal(MAIN_IFACE, 'JobNew', 'uos', [job_id, job_path, name])
    self.EmitSignal(MAIN_IFACE, 'JobRemoved', 'uoss',
                    [job_id, job_path, name, 'done'])


def StartUnit(self, name, _mode):
    job_id = self.next_job_id
    self.next_job_id += 1

    job_path = PATH_PREFIX + '/Job/{}'.format(job_id)
    GLib.idle_add(lambda: emit_job_new_remove(self, job_id, job_path, name))

    unit_path = self.units[str(name)]
    unit = mockobject.objects[unit_path]
    unit.UpdateProperties(UNIT_IFACE, {'ActiveState': 'active'})

    return job_path


def StartTransientUnit(self, name, _mode, _properties, _aux):
    job_id = self.next_job_id
    self.next_job_id += 1

    job_path = PATH_PREFIX + '/Job/%d' % (job_id)
    GLib.idle_add(lambda: emit_job_new_remove(self, job_id, job_path, name))

    return job_path


def StopUnit(self, name, _mode):
    job_id = self.next_job_id
    self.next_job_id += 1

    job_path = PATH_PREFIX + '/Job/%d' % (job_id)
    GLib.idle_add(lambda: emit_job_new_remove(self, job_id, job_path, name))

    unit_path = self.units[str(name)]
    unit = mockobject.objects[unit_path]
    unit.UpdateProperties(UNIT_IFACE, {'ActiveState': 'inactive'})
    return job_path


def GetUnit(self, name):
    unit_path = self.units[str(name)]
    return unit_path


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

import copy
import io
from nisyscfg.component_info import ComponentInfo
from nixnetconfig import utilities
import pytest
from unittest import mock


_sysapi_data = {
    'device1_port1_mock': {
        'connects_to_link_name': 'Device1 Link',
        'expert_name': ['xnet'],
        'expert_user_alias': ['myPort1'],
        'is_device': False,
        'xnet': {
            'port_number': 1,
        },
    },

    'device1_mock': {
        'connects_to_link_name': '',
        'expert_name': ['xnet'],
        'expert_user_alias': ['Unknown'],
        'firmware_revision': '19072316',
        'is_device': True,
        'provides_link_name': 'Device1 Link',
        'product_name': 'NI PXI-8513',
        'serial_number': 'A2345678',
    },

    'chassis1_mock': {
        'expert_user_alias': ['myChassis'],
        'expert_name': [''],
        'is_chassis': True,
        'provides_link_name': 'chassis1',
        'product_name': 'NI PXI chassis',
        'serial_number': 'A8765432',
    },
}


def get_nisyscfg_resource_filter_value(resource_cache, name):
    if name == 'expert_name':
        return resource_cache['expert_name'][0]
    if name == 'user_alias':
        return resource_cache['expert_user_alias'][0]
    if name == 'serial_number':
        return resource_cache['serial_number']
    return resource_cache.get(name, None)


class ResourceMock(object):
    def __init__(self, resource_cache):
        self.__dict__['_resource_cache'] = resource_cache
        self.__dict__['_upgrade_firmware'] = mock.Mock()
        self.__dict__['_rename'] = mock.Mock()
        self.__dict__['_save_changes'] = mock.Mock()
        self.__dict__['_self_test'] = mock.Mock()
        for expert in resource_cache['expert_name']:
            self.__dict__[expert] = mock.MagicMock()
            for name, value in resource_cache.get(expert, {}).items():
                setattr(self.__dict__[expert], name, value)

    def __getattr__(self, name):
        if name in self._resource_cache:
            return self._resource_cache[name]
        if name == 'upgrade_firmware':
            return self._upgrade_firmware
        if name == 'rename':
            return self._rename
        if name == 'save_changes':
            return self._save_changes
        if name == 'self_test':
            return self._self_test
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in self._resource_cache:
            self._resource_cache[name] = value


class SessionMock(object):
    def __init__(self, sysapi_data):
        self._sysapi_cache = copy.deepcopy(sysapi_data)
        for name, resource_cache in self._sysapi_cache.items():
            setattr(self, name, ResourceMock(resource_cache))

    def __call__(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def insert_device_to_chassis(self, chassis_name='chassis1_mock', device_name='device1_mock'):
        self._sysapi_cache[device_name]['connects_to_link_name'] = self._sysapi_cache[chassis_name]['provides_link_name']

    def update_device_firmware_version(self, version, device_name='device1_mock'):
        self._sysapi_cache[device_name]['firmware_revision'] = version

    def create_filter(self, **kwargs):
        class MockFilter(dict):
            def __setattr__(self, name, value):
                self[name] = value
        return MockFilter()

    def find_hardware(self, filter={}, **kwargs):
        return (getattr(self, name)
                for name, entry in self._sysapi_cache.items()
                if all(get_nisyscfg_resource_filter_value(entry, k) == v for k, v in filter.items()))


@mock.patch('sys.stdout', new_callable=io.StringIO)
@mock.patch('nisyscfg.Session', new_callable=SessionMock({}))
def test_enumerate_xnet_devices_prints_only_my_system_when_no_xnet_devices_are_present(session_mock, stdout_mock):
    utilities.enumerate_xnet_devices()
    assert stdout_mock.getvalue() == 'My System:\n'


@mock.patch('sys.stdout', new_callable=io.StringIO)
@mock.patch('nisyscfg.Session', new_callable=SessionMock(_sysapi_data))
def test_enumerate_xnet_devices_prints_device_info_when_xnet_devices_are_present(session_mock, stdout_mock):
    utilities.enumerate_xnet_devices()
    assert 'My System:\n' in stdout_mock.getvalue()
    assert _sysapi_data['device1_mock']['product_name'] in stdout_mock.getvalue()
    assert _sysapi_data['device1_port1_mock']['expert_user_alias'][0] in stdout_mock.getvalue()


@mock.patch('sys.stdout', new_callable=io.StringIO)
@mock.patch('nisyscfg.Session', new_callable=SessionMock(_sysapi_data))
def test_enumerate_xnet_devices_prints_device_info_when_xnet_devices_has_no_firmware_version(session_mock, stdout_mock):
    session_mock.update_device_firmware_version('')
    utilities.enumerate_xnet_devices()
    assert 'My System:\n' in stdout_mock.getvalue()
    assert _sysapi_data['device1_mock']['product_name'] in stdout_mock.getvalue()
    assert _sysapi_data['device1_port1_mock']['expert_user_alias'][0] in stdout_mock.getvalue()


@mock.patch('sys.stdout', new_callable=io.StringIO)
@mock.patch('nisyscfg.Session', new_callable=SessionMock(_sysapi_data))
def test_enumerate_xnet_devices_prints_device_info_when_xnet_devices_are_present_under_chassis(session_mock, stdout_mock):
    session_mock.insert_device_to_chassis()
    utilities.enumerate_xnet_devices()
    assert 'My System:\n' in stdout_mock.getvalue()
    assert _sysapi_data['chassis1_mock']['expert_user_alias'][0] in stdout_mock.getvalue()
    assert _sysapi_data['device1_mock']['product_name'] in stdout_mock.getvalue()
    assert _sysapi_data['device1_port1_mock']['expert_user_alias'][0] in stdout_mock.getvalue()


@pytest.mark.parametrize('mode, expected_value',
                         [('off', 0),
                          ('on', 1)])
def test_blink_xnet_port_sets_blink_property_and_invokes_save_changes(mode, expected_value):
    with mock.patch('nisyscfg.Session', new_callable=SessionMock(_sysapi_data)) as session_mock:
        utilities.blink_xnet_port('myPort1', mode)
        assert session_mock.device1_port1_mock.xnet.blink == expected_value
        session_mock.device1_port1_mock.save_changes.assert_called_once_with()


@mock.patch('nisyscfg.Session', new_callable=SessionMock({}))
def test_blink_xnet_port_raises_error_when_no_xnet_devices_are_present(session_mock):
    with pytest.raises(utilities.XnetConfigError):
        utilities.blink_xnet_port('myPort1', 0)


@mock.patch('nisyscfg.Session', new_callable=SessionMock({}))
def test_blink_xnet_port_raises_error_when_an_invalid_port_name_is_supplied(session_mock):
    with pytest.raises(utilities.XnetConfigError):
        utilities.blink_xnet_port('invalid_port_name', 0)


@mock.patch('nisyscfg.Session', new_callable=SessionMock(_sysapi_data))
def test_upgrade_xnet_firmware_invokes_upgrade_firmare_on_device(session_mock):
    utilities.upgrade_xnet_firmware('A2345678')
    session_mock.device1_mock.upgrade_firmware.assert_called_once_with(version='0')


@mock.patch('nisyscfg.Session', new_callable=SessionMock(_sysapi_data))
def test_upgrade_xnet_firmware_raises_error_when_an_invalid_serial_number_is_supplied(session_mock):
    with pytest.raises(utilities.XnetConfigError):
        utilities.upgrade_xnet_firmware('invalid_serial_number')


@mock.patch('nisyscfg.Session', new_callable=SessionMock(_sysapi_data))
def test_rename_xnet_port_name_runs_when_a_valid_portname_is_supplied(session_mock):
    current_port_name, new_port_name = 'myPort1', 'myPort2'
    utilities.rename_xnet_port_name(current_port_name, new_port_name)
    session_mock.device1_port1_mock.rename.assert_called_once_with(new_port_name)


@mock.patch('nisyscfg.Session', new_callable=SessionMock(_sysapi_data))
def test_rename_xnet_port_name_report_error_when_an_invalid_port_name_is_supplied(session_mock):
    missing_port = 'invalid_port_name'
    with pytest.raises(utilities.XnetConfigError):
        utilities.rename_xnet_port_name(missing_port, 'myPort2')


@mock.patch('nisyscfg.Session', new_callable=SessionMock(_sysapi_data))
def test_self_test_xnet_device_runs_when_a_valid_serial_number_is_supplied(session_mock):
    utilities.self_test_xnet_device('A2345678')
    session_mock.device1_mock.self_test.assert_called_once_with()


@mock.patch('nisyscfg.Session', new_callable=SessionMock(_sysapi_data))
def test_self_test_xnet_device_repor_error_when_an_invalid_serial_number_is_supplied(session_mock):
    missing_serial = 'B2345678'
    with pytest.raises(utilities.XnetConfigError):
        utilities.self_test_xnet_device(missing_serial)


@mock.patch('nisyscfg.Session', new_callable=SessionMock(_sysapi_data))
def test_assign_xnet_port_name_runs_when_valid_params_are_supplied(session_mock):
    port_name = 'myPort2'
    utilities.assign_xnet_port_name('A2345678', 1, port_name)
    session_mock.device1_port1_mock.rename.assert_called_once_with(port_name)


@mock.patch('nisyscfg.Session', new_callable=SessionMock(_sysapi_data))
def test_assign_xnet_port_name_report_error_when_an_invalid_serial_number_is_supplied(session_mock):
    bad_serial_number, port_number = 'B2345679', 1
    with pytest.raises(utilities.XnetConfigError):
        utilities.assign_xnet_port_name(bad_serial_number, port_number, 'myPort2')


@mock.patch('nisyscfg.Session', new_callable=SessionMock(_sysapi_data))
def test_assign_xnet_port_name_report_error_when_an_invalid_port_number_is_supplied(session_mock):
    serial_number, bad_port_number = 'A2345678', 99
    with pytest.raises(utilities.XnetConfigError):
        utilities.assign_xnet_port_name(serial_number, bad_port_number, 'myPort2')


@mock.patch('platform.system')
@mock.patch('sys.stdout', new_callable=io.StringIO)
@mock.patch('configparser.ConfigParser')
def test_get_xnet_expert_version_prints_xnet_version_on_linux_platform(parser_mock, stdout_mock, ps_mock):
    expected_version = '1.2.3b5'
    parser = parser_mock.return_value
    parser.get.return_value = expected_version
    ps_mock.return_value = 'Linux'
    utilities.get_xnet_expert_version()
    assert 'ni-xnet {}'.format(expected_version) in stdout_mock.getvalue()


@mock.patch('platform.system')
@mock.patch('sys.stdout', new_callable=io.StringIO)
@mock.patch('nisyscfg.Session')
def test_get_xnet_expert_version_prints_xnet_version_on_windows_platform(session_mock, stdout_mock, ps_mock):
    expected_version = '1.2.3b5'
    session = session_mock.return_value
    session.__enter__.return_value = session
    session.get_installed_software_components.return_value = [
        ComponentInfo('ni-abc', '0.1.0', '', '', ''),
        ComponentInfo('ni-xnet', expected_version, '', '', ''),
    ]
    ps_mock.return_value = 'Windows'
    utilities.get_xnet_expert_version()
    assert 'ni-xnet {}'.format(expected_version) in stdout_mock.getvalue()

import io
from nixnetconfig import __main__
from nixnetconfig import parser
from nixnetconfig import utilities
import pytest
from unittest import mock


def run_nixnetconfig(*arg_string):
    __main__.main(arg_string)


@mock.patch('nixnetconfig.utilities.enumerate_xnet_devices', spec=True)
def test_enumerate_xnet_devices_runs_when_no_augments_are_specified(enumerate_xnet_devices_mock):
    run_nixnetconfig()
    enumerate_xnet_devices_mock.assert_called_once_with()


@mock.patch('nixnetconfig.utilities.enumerate_xnet_devices', spec=True)
def test_enumerate_xnet_devices_runs_when_enumerate_is_specified(enumerate_xnet_devices_mock):
    run_nixnetconfig('enumerate')
    enumerate_xnet_devices_mock.assert_called_once_with()


@pytest.mark.parametrize(
    "old_name, new_name",
    [('can1', 'can2'),
     ('CAN1', 'CAN2'),
     ('CAN1', 'CAN259'),
     ('CAN1', 'unassigned')])
@mock.patch('nixnetconfig.utilities.rename_xnet_port_name', spec=True)
def test_rename_xnet_port_name_runs_when_rename_port_are_specified(rename_xnet_port_name_mock, old_name, new_name):
    run_nixnetconfig('rename', old_name, new_name)
    rename_xnet_port_name_mock.assert_called_once_with(old_name.upper(), new_name.upper())


@mock.patch('nixnetconfig.utilities.enumerate_xnet_devices', spec=True)
@mock.patch('nixnetconfig.utilities.rename_xnet_port_name', spec=True)
def test_rename_xnet_port_name_runs_when_e_option_is_specified(rename_xnet_port_name_mock, enumerate_xnet_devices_mock):
    sequence_manager = mock.Mock()
    sequence_manager.attach_mock(rename_xnet_port_name_mock, 'rename_xnet_port_name_mock')
    sequence_manager.attach_mock(enumerate_xnet_devices_mock, 'enumerate_xnet_devices_mock')

    old_name, new_name = 'can1', 'can2'
    run_nixnetconfig('rename', old_name, new_name, '-e')
    run_nixnetconfig('rename', '-e', old_name, new_name)
    expected_calls = [
        mock.call.rename_xnet_port_name_mock(current_port_name=old_name.upper(), new_port_name=new_name.upper()),
        mock.call.enumerate_xnet_devices_mock(),
        mock.call.rename_xnet_port_name_mock(current_port_name=old_name.upper(), new_port_name=new_name.upper()),
        mock.call.enumerate_xnet_devices_mock()
    ]
    assert sequence_manager.mock_calls == expected_calls


@mock.patch('nixnetconfig.utilities.self_test_xnet_device', spec=True)
def test_self_test_xnet_device_runs_when_test_port_are_specified(self_test_xnet_device_mock):
    port_name = 'can1'
    run_nixnetconfig('test', port_name)
    self_test_xnet_device_mock.assert_called_once_with(port_name.upper())


@pytest.mark.parametrize(
    "mode",
    ['on', 'off'])
@mock.patch('nixnetconfig.utilities.blink_xnet_port', spec=True)
def test_blink_xnet_port_runs_when_blink_mode_port_are_specified(blink_xnet_port_mock, mode):
    port_name = 'can1'
    run_nixnetconfig('blink', mode, port_name)
    blink_xnet_port_mock.assert_called_once_with(port_name.upper(), mode)


@mock.patch('nixnetconfig.utilities.upgrade_xnet_firmware', spec=True)
def test_upgrade_xnet_firmware_runs_when_update_port_are_specified(upgrade_xnet_firmware_mock):
    serial_number_string = 'a2345678'
    run_nixnetconfig('update', serial_number_string)
    upgrade_xnet_firmware_mock.assert_called_once_with(serial_number_string.upper())


@mock.patch('nixnetconfig.utilities.enumerate_xnet_devices', spec=True)
@mock.patch('nixnetconfig.utilities.upgrade_xnet_firmware', spec=True)
def test_upgrade_xnet_firmware_runs_when_e_optiont_is_specified(upgrade_xnet_firmware_mock, enumerate_xnet_devices_mock):
    sequence_manager = mock.Mock()
    sequence_manager.attach_mock(upgrade_xnet_firmware_mock, 'upgrade_xnet_firmware_mock')
    sequence_manager.attach_mock(enumerate_xnet_devices_mock, 'enumerate_xnet_devices_mock')

    serial_number_string = 'a2345678'
    run_nixnetconfig('update', serial_number_string, '-e')
    run_nixnetconfig('update', '-e', serial_number_string)
    expected_calls = [
        mock.call.upgrade_xnet_firmware_mock(serial_number=serial_number_string.upper()),
        mock.call.enumerate_xnet_devices_mock(),
        mock.call.upgrade_xnet_firmware_mock(serial_number=serial_number_string.upper()),
        mock.call.enumerate_xnet_devices_mock()
    ]
    assert sequence_manager.mock_calls == expected_calls


@mock.patch('nixnetconfig.utilities.get_xnet_expert_version', spec=True)
def test_get_xnet_expert_version_runs_when_version_is_speficied(get_xnet_expert_version_mock):
    run_nixnetconfig('version')
    get_xnet_expert_version_mock.assert_called_once_with()


@mock.patch('nixnetconfig.utilities.assign_xnet_port_name', spec=True)
def test_assign_xnet_port_name_runs_when_assign_serial_number_port_name_are_specified(assign_xnet_port_name_mock):
    port_name = 'can1'
    serial_number = 'a2345678'
    port_number = '1'
    run_nixnetconfig('assign', serial_number, port_number, port_name)
    assign_xnet_port_name_mock.assert_called_once_with(serial_number.upper(), int(port_number), port_name.upper())


@mock.patch('nixnetconfig.utilities.enumerate_xnet_devices', spec=True)
@mock.patch('nixnetconfig.utilities.assign_xnet_port_name', spec=True)
def test_assign_xnet_port_name_runs_when_e_option_is_specified(assign_xnet_port_name_mock, enumerate_xnet_devices_mock):
    sequence_manager = mock.Mock()
    sequence_manager.attach_mock(assign_xnet_port_name_mock, 'assign_xnet_port_name_mock')
    sequence_manager.attach_mock(enumerate_xnet_devices_mock, 'enumerate_xnet_devices_mock')

    port_name = 'can1'
    serial_number = 'a2345678'
    port_number = '1'
    run_nixnetconfig('assign', serial_number, port_number, port_name, '-e')
    run_nixnetconfig('assign', '-e', serial_number, port_number, port_name)
    expected_calls = [
        mock.call.assign_xnet_port_name_mock(serial_number=serial_number.upper(), port_number=int(port_number), port_name=port_name.upper()),
        mock.call.enumerate_xnet_devices_mock(),
        mock.call.assign_xnet_port_name_mock(serial_number=serial_number.upper(), port_number=int(port_number), port_name=port_name.upper()),
        mock.call.enumerate_xnet_devices_mock()
    ]
    assert sequence_manager.mock_calls == expected_calls


@pytest.mark.parametrize(
    'exception', [utilities.XnetConfigError, Exception])
@pytest.mark.parametrize(
    'command, arguments, function_name',
    [
        ('enumerate', [], 'enumerate_xnet_devices'),
        ('rename', ['old_name', 'new_name'], 'rename_xnet_port_name'),
        ('test', ['port_name'], 'self_test_xnet_device'),
        ('blink', ['on', 'port_name'], 'blink_xnet_port'),
        ('version', [], 'get_xnet_expert_version'),
        ('update', ['port_name'], 'upgrade_xnet_firmware'),
        ('assign', ['12345678', '0', 'port_name'], 'assign_xnet_port_name'),
    ])
@mock.patch('sys.stderr', new_callable=io.StringIO)
def test_main_prints_to_stderr_raise_system_exit_when_command_raise_exception(stderr_mock, command, arguments, function_name, exception):
    with mock.patch('nixnetconfig.utilities.{}'.format(function_name), spec=True) as function_mock:
        function_mock.side_effect = exception('my error message')
        with pytest.raises(SystemExit):
            run_nixnetconfig(command, *arguments)
        if exception == utilities.XnetConfigError:
            assert 'my error message' in stderr_mock.getvalue()
        else:
            assert 'ERROR: Operation failed' in stderr_mock.getvalue()


@pytest.mark.parametrize('width', [60, 80, 120])
@mock.patch('shutil.get_terminal_size', spec=True)
@mock.patch('sys.stdout', new_callable=io.StringIO)
def test_main_prints_help_word_wrapped_to_console_width(stout_mock, get_terminal_size_mock, width):
    get_terminal_size_mock.return_value = (width, 20)  # (columns, rows)
    with pytest.raises(SystemExit):
        run_nixnetconfig('-h')
    summary_found = False
    for line in stout_mock.getvalue().splitlines():
        if line.startswith(parser.HELP_TEXT['summary']):
            summary_found = True
        if summary_found:
            assert len(line) <= width

import configparser
import logging
import nisyscfg2 as nisyscfg
from nixnetconfig.system import SystemTree
import platform


logger = logging.getLogger('nixnetconfig')
_XNET_EXPERT_NAME = 'xnet'


class XnetConfigError(Exception):
    def __init__(self, message=''):
        self._message = message

    @property
    def message(self):
        return self._message


class PortNotFoundError(XnetConfigError):
    def __init__(self, missing_port, custom_message=''):
        super().__init__(message=custom_message if custom_message else 'Could not find port "{}"'.format(missing_port))


class DeviceWithSerialNumberNotFoundError(XnetConfigError):
    def __init__(self, serial_number, custom_message=''):
        super().__init__(message=custom_message if custom_message else 'Could not find a device with serial number "{}"'.format(serial_number))


def enumerate_xnet_devices():
    with nisyscfg.Session() as session:
        SystemTree(_XNET_EXPERT_NAME, session).report()


def rename_xnet_port_name(current_port_name, new_port_name):
    with nisyscfg.Session() as session:
        try:
            resource = next(session.find_hardware(expert_names=_XNET_EXPERT_NAME, IsDevice=False, UserAlias=current_port_name))
            resource.rename(new_port_name)
        except StopIteration:
            raise PortNotFoundError(current_port_name)


def assign_xnet_port_name(serial_number, port_number, port_name):
    with nisyscfg.Session() as session:
        try:
            resource = next(session.find_hardware(expert_names=_XNET_EXPERT_NAME, IsDevice=True, SerialNumber=serial_number))
            for interface_resource in session.find_hardware(expert_names=_XNET_EXPERT_NAME, IsDevice=False, ConnectsToLinkName=resource.ProvidesLinkName):
                if interface_resource.xnet.port_number == port_number:
                    interface_resource.rename(port_name)
                    return
            raise PortNotFoundError(port_number, 'Device with serial number "{}" does not have port number {}'.format(serial_number, port_number))
        except StopIteration:
            raise PortNotFoundError(port_number, 'Could not find a device with serial number "{}"'.format(serial_number))


def blink_xnet_port(port_name, mode):
    with nisyscfg.Session() as session:
        try:
            resource = next(session.find_hardware(expert_names=_XNET_EXPERT_NAME, IsDevice=False, UserAlias=port_name))
            resource.xnet.blink = {'on': 1, 'off': 0}[mode]
            resource.save_changes()
            logger.info(port_name + ': blink-LED is ' + mode)
        except StopIteration:
            raise PortNotFoundError(port_name)


def upgrade_xnet_firmware(serial_number):
    with nisyscfg.Session() as session:
        try:
            resource = next(session.find_hardware(expert_names=_XNET_EXPERT_NAME, IsDevice=True, SerialNumber=serial_number))
            logger.info('Starting firmware upgrade')
            resource.upgrade_firmware(version="0")
            logger.info('Completed firmware upgrade')
        except StopIteration:
            raise DeviceWithSerialNumberNotFoundError(serial_number)


def self_test_xnet_device(serial_number):
    with nisyscfg.Session() as session:
        try:
            resource = next(session.find_hardware(expert_names=_XNET_EXPERT_NAME, IsDevice=True, SerialNumber=serial_number))
            logger.info('Starting self test')
            # TODO  xnet sysapi expert will report its error code when a function failed, include self_test,
            #       but we may need to catch LibraryError for error code that is not defined in class Status(CtypesEnum)
            resource.self_test()
            logger.info('Completed self test')
        except StopIteration:
            raise DeviceWithSerialNumberNotFoundError(serial_number)


def get_xnet_expert_version():
    if platform.system() == 'Linux':
        # nisyscfg does not support NISysCfgGetInstalledSoftwareComponents on Linux desktop systems, directly get ni-xnet version from nixntcfg.ini
        parser = configparser.ConfigParser()
        parser.read('/usr/share/ni-xnet/nixntcfg.ini')
        print("ni-xnet", parser.get('Version', 'VersionString'))
    else:
        with nisyscfg.Session() as session:
            sw = session.get_installed_software_components()
            for component in sw:
                if component['id'] == str('ni-xnet'):
                    print(component['id'], component['version'])


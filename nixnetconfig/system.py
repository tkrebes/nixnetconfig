from nisyscfg2 import Session


_LINE_INDENT = "    "


class InterfaceBranch(object):
    def __init__(self, resource, indent):
        self.name = resource.ExpertUserAlias[0]
        self.indent = _LINE_INDENT * indent

    def report(self):
        print(self.indent + "Interface:", self.name)


class DeviceBranch(object):
    def __init__(self, expert_name, session: Session, resource, indent=1):
        self.name = resource.ProductName
        self.serial_num = resource.SerialNumber
        self.firmware_revision = resource.FirmwareRevision
        self.device_link_name = resource.ProvidesLinkName
        self.interfaces = []
        self.indent = _LINE_INDENT * indent
        for interface_resource in session.find_hardware(expert_names=[expert_name], IsDevice=False, ConnectsToLinkName=self.device_link_name):
            self.interfaces.append(InterfaceBranch(interface_resource, indent + 1))

    def report(self):
        if self.firmware_revision:
            print(self.indent + "Device:", self.name, "Serial number", self.serial_num, "Firmware", self.firmware_revision)
        else:
            print(self.indent + "Device:", self.name, "Serial number", self.serial_num)
        for interface in self.interfaces:
            interface.report()


class ChassisBranch(object):
    def __init__(self, expert_name, session: Session, resource):
        self.name = resource.ExpertUserAlias[0]
        self.serial_num = resource.SerialNumber
        self.chassis_link_name = resource.ProvidesLinkName
        self.devices = []
        for device_resource in session.find_hardware(expert_names=[expert_name], IsDevice=True, ConnectsToLinkName=self.chassis_link_name):
            self.devices.append(DeviceBranch(expert_name, session, device_resource, 2))

    def report(self):
        if self.devices:
            print(_LINE_INDENT + "Chassis:", self.name, "Serial number", self.serial_num)
            for device in self.devices:
                device.report()


class SystemTree(object):
    def __init__(self, expert_name, session: Session):
        self.chassis = []
        self.devices = []
        for chassis_resource in session.find_hardware(expert_names=[], IsChassis=True):
            self.chassis.append(ChassisBranch(expert_name, session, chassis_resource))

        for device_resource in session.find_hardware(expert_names=[expert_name], IsDevice=True, ConnectsToLinkName=""):
            self.devices.append(DeviceBranch(expert_name, session, device_resource))

    def report(self):
        print("My System:")
        for device in self.devices:
            device.report()

        for a_chassis in self.chassis:
            a_chassis.report()



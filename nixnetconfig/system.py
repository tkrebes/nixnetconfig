from nisyscfg import Session


_LINE_INDENT = "    "


class InterfaceBranch(object):
    def __init__(self, resource, indent):
        self.name = resource.expert_user_alias[0]
        self.indent = _LINE_INDENT * indent

    def report(self):
        print(self.indent + "Interface:", self.name)


class DeviceBranch(object):
    def __init__(self, expert_name, session: Session, resource, indent=1):
        self.name = resource.product_name
        self.serial_num = resource.serial_number
        self.firmware_revision = resource.firmware_revision
        self.device_link_name = resource.provides_link_name
        self.interfaces = []
        self.indent = _LINE_INDENT * indent

        filter = session.create_filter()
        filter.is_device = False
        filter.connects_to_link_name = self.device_link_name
        for interface_resource in session.find_hardware(filter=filter, expert_names=[expert_name]):
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
        self.name = resource.expert_user_alias[0]
        self.serial_num = resource.serial_number
        self.chassis_link_name = resource.provides_link_name
        self.devices = []

        filter = session.create_filter()
        filter.is_device = True
        filter.connects_to_link_name = self.chassis_link_name
        for device_resource in session.find_hardware(filter=filter, expert_names=[expert_name]):
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

        chassis_filter = session.create_filter()
        chassis_filter.is_chassis = True
        for chassis_resource in session.find_hardware(filter=chassis_filter, expert_names=[]):
            self.chassis.append(ChassisBranch(expert_name, session, chassis_resource))

        device_filter = session.create_filter()
        device_filter.is_device = True
        device_filter.connects_to_link_name = ""
        for device_resource in session.find_hardware(filter=device_filter, expert_names=[expert_name]):
            self.devices.append(DeviceBranch(expert_name, session, device_resource))

    def report(self):
        print("My System:")
        for device in self.devices:
            device.report()

        for a_chassis in self.chassis:
            a_chassis.report()



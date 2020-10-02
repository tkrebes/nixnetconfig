import argparse
import nixnetconfig
import os
import shutil
import textwrap


HELP_TEXT = {
    'summary':
        'Configure NI-XNET interfaces and devices.',

    'description':
        'An NI-XNET interface name identifies a physical port (connector). The'
        ' interface name is used in the NI-XNET API to create a session for'
        ' communication. An NI-XNET device is a physical card or module that'
        ' contains ports.',

    'options': {
        'help':
            'Display this help and exit. Use "nixnetconfig <command> -h" for'
            ' command-specific help.',
        'verbose':
            'Enable verbose mode to display detailed information. The default'
            ' displays errors only.',
        'enumerate':
            'Enumerate and display all NI-XNET devices and interfaces.',
    },

    'commands': {
        'enumerate':
            'Enumerate and display all NI-XNET devices and interfaces. This is'
            ' the default if no other command is provided.',
        'rename':
            'Change the name of the current interface.',
        'test':
            'Run self-test on the device with the specified serial number.',
        'blink':
            'Turn LED blinking on or off for the interface name.',
        'version':
            'Display the NI-XNET driver version.',
        'update':
            'Update firmware onto the device of the specified serial number. The'
            ' update is distributed from installed NI-XNET software.',
        'assign':
            'Assign a new interface name using the serial number of the device'
            ' and port number of the interface.',
    },
}


def add_help_argument(parser):
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help=HELP_TEXT['options']['help'])


def add_verbose_argument(parser):
    parser.add_argument('-v', '--verbose', action='count', help=HELP_TEXT['options']['verbose'])


def add_enumerate_argument(parser):
    parser.add_argument('-e', '--enumerate', action='store_true', help=HELP_TEXT['options']['enumerate'])


def get_parser():
    class CustomFormatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):
        def _split_lines(self, text, width):
            text = self._whitespace_matcher.sub(' ', text).strip()
            return textwrap.wrap(text, width, break_on_hyphens=False)

    console_width = shutil.get_terminal_size((80, 20))[0]
    os.environ['COLUMNS'] = str(console_width)
    parser_description = '{}\n\n{}'.format(
        HELP_TEXT['summary'],
        '\n'.join(textwrap.wrap(
            HELP_TEXT['description'], console_width - 1, break_on_hyphens=False,
        )))

    parser = argparse.ArgumentParser(
        formatter_class=CustomFormatter,
        description=parser_description,
        add_help=False)

    add_help_argument(parser)
    add_verbose_argument(parser)
    # Only invoke enumerate_xnet_devices once
    parser.set_defaults(command=nixnetconfig.utilities.enumerate_xnet_devices, enumerate=False)
    subparsers = parser.add_subparsers(title="commands")

    parser_enumerate = subparsers.add_parser('enumerate', help=HELP_TEXT['commands']['enumerate'])
    parser_enumerate.set_defaults(command=nixnetconfig.utilities.enumerate_xnet_devices)
    add_verbose_argument(parser_enumerate)

    parser_rename = subparsers.add_parser('rename', help=HELP_TEXT['commands']['rename'])
    parser_rename.set_defaults(command=nixnetconfig.utilities.rename_xnet_port_name)
    parser_rename.add_argument('current_port_name', metavar='current_name', type=str.upper)
    parser_rename.add_argument('new_port_name', metavar='new_name', type=str.upper)
    add_verbose_argument(parser_rename)
    add_enumerate_argument(parser_rename)

    parser_test = subparsers.add_parser('test', help=HELP_TEXT['commands']['test'])
    parser_test.set_defaults(command=nixnetconfig.utilities.self_test_xnet_device)
    parser_test.add_argument('serial_number', type=str.upper)
    add_verbose_argument(parser_test)

    parser_blink = subparsers.add_parser('blink', help=HELP_TEXT['commands']['blink'])
    parser_blink.set_defaults(command=nixnetconfig.utilities.blink_xnet_port)
    parser_blink.add_argument('mode', choices=['on', 'off'])
    parser_blink.add_argument('port_name', metavar='interface_name', type=str.upper)
    add_verbose_argument(parser_blink)

    parser_version = subparsers.add_parser('version', help=HELP_TEXT['commands']['version'])
    parser_version.set_defaults(command=nixnetconfig.utilities.get_xnet_expert_version)
    add_verbose_argument(parser_version)

    parser_update = subparsers.add_parser('update', help=HELP_TEXT['commands']['update'])
    parser_update.set_defaults(command=nixnetconfig.utilities.upgrade_xnet_firmware)
    parser_update.add_argument('serial_number', type=str.upper)
    add_verbose_argument(parser_update)
    add_enumerate_argument(parser_update)

    parser_assign = subparsers.add_parser('assign', help=HELP_TEXT['commands']['assign'])
    parser_assign.set_defaults(command=nixnetconfig.utilities.assign_xnet_port_name)
    parser_assign.add_argument('serial_number', type=str.upper)
    parser_assign.add_argument('port_number', metavar='port', type=int)
    parser_assign.add_argument('port_name', metavar='name', type=str.upper)
    add_verbose_argument(parser_assign)
    add_enumerate_argument(parser_assign)

    return parser

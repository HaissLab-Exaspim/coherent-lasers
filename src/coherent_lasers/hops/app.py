"""
Simple cli app for sending commands to a CohrHOPS device.
"""

import click
from .lib import HOPSException, get_hops_manager, HOPSDevice


@click.command()
@click.option("--command", "-c", help="Send a commmand to all devices")
def cli(command) -> None:
    manager = get_hops_manager()
    serials = manager._handles.values()
    devices = {serial: HOPSDevice(serial) for serial in serials}
    click.echo(f"Found {len(serials)} devices:")
    for serial in serials:
        click.echo(f"  {serial}:")
    if command:
        click.echo(f"Sending command to all devices: {command}")
        for serial, device in devices.items():
            click.echo(f" {serial}: {device.send_command(command)}")
        return
    multidevice_interactive_session(devices)


def multidevice_interactive_session(devices: dict) -> None:
    EXIT = {"EXIT", "QUIT", ":Q"}
    LIST = {"LIST", "LS"}
    devices = devices
    current = [next(iter(devices.keys()))]
    click.echo(f"starting interactive session with devices: {', '.join(devices.keys())}. Type 'exit' to end.")
    while True:
        command: str = click.prompt(f"{', '.join(current)}>", prompt_suffix="")
        command_parts = command.split()
        primary_command = command_parts[0].upper()
        if primary_command in EXIT:
            break
        if primary_command in LIST:
            click.echo(f"Found {len(devices)} devices:")
            for serial in devices:
                click.echo(f"  {serial}:")
            continue
        if primary_command.startswith("SELECT"):
            if len(command_parts) < 2:
                click.echo("Please provide a device to switch to. Either by index or serial number.")
                continue
            current = parse_select_command(command, devices)
            continue
        try:
            for serial in current:
                click.echo(f"  {serial}: {devices[serial].send_command(command)}")
        except HOPSException as e:
            click.echo(f"HOPSError: {e}")


def parse_select_command(command: str, devices: dict) -> list:
    command_parts = command.upper().split()
    if "ALL" in command_parts:
        return list(devices.keys())
    selected = []
    for arg in command_parts:
        if arg.isdigit() and int(arg) <= len(devices):
            selected.append(list(devices.keys())[int(arg) - 1])
            continue
        if arg in devices:
            selected.append(arg)
            continue
    return selected


if __name__ == "__main__":
    cli()

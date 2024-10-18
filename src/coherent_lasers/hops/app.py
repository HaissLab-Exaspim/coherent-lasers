"""
Simple cli app for sending commands to a CohrHOPS device.
Two main commands are available:
- list: list serial numbers of all connected devices
- device: send a command to a specific device by serial number or interact with it in an interactive session
"""

import click
from .lib import get_hops_manager, HOPSDevice

@click.group()
def cli():
    pass

@cli.command()
def list():
    """List serial numbers of all connected devices."""
    manager = get_hops_manager()
    for device in manager.devices_connected:
        click.echo(device.serial)

@cli.command()
@click.argument("serial")
@click.argument("command")
@click.option("--interactive", "-i", is_flag=True, help="Start an interactive session with the device.")
def device(serial, command, interactive):
    """Send a command to a specific device by serial number or interact with it in an interactive session."""
    device = HOPSDevice(serial)
    if interactive:
        click.echo(f"Starting interactive session with device {serial}. Type 'exit' to end.")
        while True:
            command = click.prompt(f"{serial}>", prompt_suffix="")
            if command == "exit":
                break
            click.echo(device.send_command(command))
    else:
        click.echo(device.send_command(command))

if __name__ == "__main__":
    cli()

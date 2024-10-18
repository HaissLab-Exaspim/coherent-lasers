"""
Simple cli app for sending commands to a CohrHOPS device.
Two main commands are available:
- list: list serial numbers of all connected devices
- device: send a command to a specific device by serial number or interact with it in an interactive session
"""

import click
from .lib import HOPSException, get_hops_manager, HOPSDevice


@click.group()
def cli() -> None:
    pass


@cli.command()
def list():
    """List serial numbers of all connected devices."""
    manager = get_hops_manager()
    for serial in manager._handles.values():
        click.echo(serial)


@cli.command()
@click.argument("serial")
@click.argument("command", default="*?HID", required=False)
@click.option("--interactive", "-i", is_flag=True, help="Start an interactive session with the device.")
def device(serial, command, interactive) -> None:
    """Send a command to a specific device by serial number or interact with it in an interactive session."""
    exit = {"exit", "EXIT", "quit", "QUIT", "q", "Q"}
    device = HOPSDevice(serial)
    if interactive:
        click.echo(f"Starting interactive session with device {serial}. Type 'exit' to end.")
        while True:
            command = click.prompt(f"{serial}>", prompt_suffix="")
            if command in exit:
                break
            try:
                click.echo(device.send_command(command), nl=False)
            except HOPSException as e:
                click.echo(f"HOPSError: {e}")
    else:
        click.echo(device.send_command(command), nl=False)


if __name__ == "__main__":
    cli()

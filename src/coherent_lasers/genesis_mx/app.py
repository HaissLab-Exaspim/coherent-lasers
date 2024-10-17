import click
import time
import logging
from coherent_lasers.genesis_mx.driver import GenesisMX
from coherent_lasers.genesis_mx.commands import OperationModes

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class LaserException(Exception):
    """Custom exception for laser-related errors."""

    pass


def handle_laser_exceptions(func):
    """Decorator to handle laser-related exceptions."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except LaserException as e:
            click.echo(f"Laser error: {str(e)}", err=True)
            logger.error(f"Laser error in {func.__name__}: {str(e)}")
        except Exception as e:
            click.echo(f"An unexpected error occurred: {str(e)}", err=True)
            logger.exception(f"Unexpected error in {func.__name__}")

    return wrapper


@click.group(invoke_without_command=True)
@click.option("--serial", prompt="Laser serial number", help="Serial number of the laser to control")
@click.pass_context
def cli(ctx, serial):
    """CLI for controlling and testing Genesis MX lasers."""
    ctx.ensure_object(dict)
    try:
        ctx.obj["laser"] = GenesisMX(serial)
        if ctx.invoked_subcommand is None:
            ctx.invoke(interactive)
    except Exception as e:
        raise click.ClickException(f"Failed to initialize laser: {str(e)}")


def display_status(laser):
    """Display the current status of the laser."""
    click.echo("Laser Status:")
    click.echo(f"  Key Switch Closed: {laser.is_key_switch_closed}")
    click.echo(f"  Software Switch: {laser.is_software_switch_closed}")
    click.echo(f"  Interlock Closed: {laser.is_interlock_switch_closed}")
    click.echo(f"  Remote Control Enabled: {laser.remote_control_enable}")
    click.echo(f"  Enabled: {laser.is_enabled}")
    click.echo(f"  Power: {laser.power_mw:.2f} mW")
    click.echo(f"  Power Setpoint: {laser.power_setpoint_mw:.2f} mW")
    click.echo(f"  Temperature: {laser.temperature_c:.2f}°C")
    click.echo(f"  Mode: {laser.mode.name}")
    click.echo(f"  Alarms: {', '.join(alarm.name for alarm in laser.alarms)}")


def display_info(laser) -> None:
    """Display Laser Head information."""
    click.echo("Laser Head Information:")
    info = laser.head
    for key, value in info.items():
        click.echo(f"  {key}: {value}")


@handle_laser_exceptions
def set_laser_power(laser, command):
    """Set the laser power."""
    try:
        if command and command.split()[-1].isnumeric():
            power = float(command.split()[-1])
            laser.power_setpoint_mw = power
            click.echo(f"Power setpoint set to {power} mW.")
        else:
            click.echo(f"Current power setpoint: {laser.power_setpoint_mw} mW.")
            click.echo(f"Current power: {laser.power_mw} mW.")
    except ValueError:
        click.echo("Invalid power value. Please enter a number.")


@handle_laser_exceptions
def set_laser_mode(laser, command):
    """Set the laser operation mode."""
    if command and command.split()[-1].upper() in ["PHOTO", "CURRENT"]:
        mode = command.split()[-1].upper()
        laser.mode = OperationModes[mode]
        click.echo(f"Operation mode set to {mode}.")
    else:
        click.echo(f"Current mode: {laser.mode.name}")
        click.echo("Use 'mode PHOTO' or 'mode CURRENT' to set the mode.")


def display_help():
    """Display available commands."""
    click.echo("Available commands: status, enable, disable, power [value], mode [PHOTO/CURRENT], info, exit")


def enable_laser(laser):
    """Enable the laser."""
    laser.enable()
    click.echo("Laser enabled.")


def disable_laser(laser):
    """Disable the laser."""
    laser.disable()
    click.echo("Laser disabled.")


@cli.command()
@click.pass_context
def interactive(ctx):
    """Start an interactive session with the laser."""
    laser = ctx.obj["laser"]
    click.echo("Starting interactive session. Type 'help' for available commands or 'exit' to end.")

    command_handlers = {
        "status": lambda: display_status(laser),
        "info": lambda: display_info(laser),
        "enable": lambda: enable_laser(laser),
        "disable": lambda: disable_laser(laser),
        "power": lambda cmd: set_laser_power(laser, cmd),
        "mode": lambda cmd: set_laser_mode(laser, cmd),
        "help": display_help,
    }

    while True:
        command = click.prompt("Enter command", type=str).lower()

        if command == "exit":
            break

        handler = next((handler for cmd, handler in command_handlers.items() if command.startswith(cmd)), None)

        if handler:
            handler(command) if callable(handler) and handler.__code__.co_argcount > 0 else handler()
        else:
            click.echo("Unknown command. Type 'help' for available commands.")

    laser.disable()
    click.echo("Interactive session ended.")
    laser.close()


@cli.command()
@click.option("--duration", default=60, help="Duration of the test in seconds")
@click.option("--interval", default=1, help="Interval between readings in seconds")
@click.pass_context
@handle_laser_exceptions
def stability_test(ctx, duration, interval):
    """Run a stability test on the laser."""
    laser = ctx.obj["laser"]
    click.echo(f"Running stability test for {duration} seconds...")
    start_time = time.time()
    initial_power = laser.power_mw
    try:
        while time.time() - start_time < duration:
            current_power = laser.power_mw
            delta = abs(current_power - initial_power)
            click.echo(f"Time: {time.time() - start_time:.1f}s, Power: {current_power:.2f} mW, Delta: {delta:.2f} mW")
            time.sleep(interval)
    except KeyboardInterrupt:
        click.echo("Stability test interrupted by user.")
    finally:
        click.echo("Stability test completed.")
        laser.disable()
        laser.close()


if __name__ == "__main__":
    cli(obj={})

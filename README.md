# coherent_lasers

This repository contains python driver packages for various lasers manufactured by coherent. To facilitate
communication with the devices, the drivers utilize:

1. low level SDKs provided by coherent
2. Serial communication via `RS232` and equivalent protocols

## Supported Lasers

1. [Genesis MX](#genesis-mx-laser-series-driver)

Repository is organized by laser model. Each laser model has its own directory containing the driver code.

   ```text
   coherent_lasers/
   ├── src/
   │   ├── common/
   │   │   ├── hops/
   │   │   │   ├── CohrFTCI2C.h
   │   │   │   ├── CohrHOPS.h
   │   │   │   ├── (DLL files for each .h file)
   │   │   │   ├── manager.py
   │   │   │   └── device.py
   │   │   ├── serial/
   │   │   │   └── serial_device.py
   │   ├── genesis_mx/
   │   │   ├── genesis_mx.py
   │   │   ├── genesis_mx_voxel.py
   │   │   └── README.md
   └── setup.py
   ```

## Installation

You can install the `coherent_lasers` package directly from a GitHub release using `pip`.

```bash
coherent_version=0.1.0
pip install https://github.com/AllenNeuralDynamics/coherent_lasers/releases/download/v${coherent_version}/coherent_lasers-${coherent_version}-py3-none-any.whl
```

## Genesis MX Laser Series Driver

A minimal python driver for a Genesis MX laser

Provides two classes for controlling a Coherent Genesis MX laser.

1. The `GenesisMX` class provides a comprehensive API for controlling the laser.
2. The `GenesisMXVoxelLaser` class provides a simplified API for controlling the laser based on the requirements of the [Voxel](https://github.com/AllenNeuralDynamics/voxel/) library.

Supports connection via USB using the HOPS SDK provided by Coherent.

## Usage

Lasers such as the Genesis MX series require that the HOPS dll files are installed and configured properly. (_HOPS dependent lasers only work on Windows._)

Installing this package from the .whl file will include the necessary dependencies. Otherwise you will need to download the dll files and add them to your system path.

Once installed, you can test the driver using the following command:

```shell
cohrhops list                                   # List available HOPS devices
cohrhops device <serial_number>                 # Connect to a specific device
cohrhops device <serial_number> --interactive   # To interact with a device in a REPL
cohrhops device <serial_number> --i             # Same as above
```

For the `GenesisMX` lasers you can use a more abstracted cli by running the following command:

```shell
genesis-mx list                                   # List available Genesis MX devices
genesis-mx device <serial_number>                 # Connect to a specific Genesis MX device
genesis-mx device <serial_number> --interactive   # To interact with a Genesis MX device in a REPL
genesis-mx device <serial_number> --i             # Same as above
genesis-mx --help                                  # Show help for the genesis-mx command
```

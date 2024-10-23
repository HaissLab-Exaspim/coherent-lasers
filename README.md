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
cohrhops_version=0.1.0
pip install https://github.com/AllenNeuralDynamics/coherent_lasers/releases/download/v${cohrhops_version}/coherent_lasers-${cohrhops_version}-py3-none-any.whl
```

**Note**: Replace v0.1.0 with the tag of the release you want to install.

## Genesis MX Laser Series Driver

A minimal python driver for a Genesis MX laser

Provides two classes for controlling a Coherent Genesis MX laser.

1. The `GenesisMX` class provides a comprehensive API for controlling the laser.
2. The `GenesisMXVoxelLaser` class provides a simplified API for controlling the laser based on the requirements of the [Voxel](https://github.com/AllenNeuralDynamics/voxel/) library.

Supports connection via USB using the HOPS SDK provided by Coherent.

## Usage

For a simple command line interface to send commands to a hops device, you can run the following command:

```bash
cohrhops
```

Alternatively, run the following command to interact with connected Genesis MX lasers:

```bash
genesis-mx
```

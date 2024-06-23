# Genesis MX Laser Series Driver

A minimal python driver for a Genesis MX laser

## Overview
This package provides two classes for controlling a Coherent Genesis MX laser.   
1. The `GenesisMX` class provides a comprehensive API for controlling the laser.  
2. The `GenesisMXVoxelLaser` class provides a simplified API for controlling the laser based on the requirements of the 
[Voxel](https://github.com/AllenNeuralDynamics/voxel/) library.

## Connection Overview
Supports connection via USB or ~~RS-232~~ (not yet implemented)

### USB Connection
- USB connection requires dll files.
- Follow instructions in the [HOPS DLL Device](../common/hops/README.md) README to set up the necessary dll files.


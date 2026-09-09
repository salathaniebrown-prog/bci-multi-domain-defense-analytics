"""BCI multi-domain analytics package.

The package is simulation-first and intended for research, testing, and
non-operational analytics workflows.
"""

from .core import (
    air_kinematics,
    bci_features,
    orbital_density,
    submarine_spectrum,
)

__all__ = [
    "air_kinematics",
    "bci_features",
    "orbital_density",
    "submarine_spectrum",
]

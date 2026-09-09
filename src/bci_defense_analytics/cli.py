"""Command-line entry point for the simulation baseline."""

from __future__ import annotations

import argparse
import json

import numpy as np

from .core import (
    air_kinematics,
    bci_features,
    orbital_density,
    submarine_spectrum,
)


def build_demo(seed=7):
    """Generate deterministic simulated inputs and return analytics output."""
    rng = np.random.default_rng(seed)

    sample_rate_hz = 256.0
    t = np.arange(512) / sample_rate_hz
    bci = np.sin(2 * np.pi * 10 * t) + 0.05 * rng.normal(size=t.size)

    acoustic = np.vstack(
        [
            np.sin(2 * np.pi * 18 * t) + 0.1 * rng.normal(size=t.size),
            np.sin(2 * np.pi * 18 * t) + 0.1 * rng.normal(size=t.size),
        ]
    )

    flight_t = np.linspace(0.0, 10.0, 101)
    positions = np.column_stack(
        [
            2.0 * flight_t,
            0.5 * flight_t**2,
            0.1 * flight_t**2,
        ]
    )

    footprints = rng.normal(size=(8, 3))

    return {
        "mode": "simulation",
        "bci": bci_features(bci, sample_rate_hz),
        "subsurface": submarine_spectrum(acoustic, sample_rate_hz),
        "air": air_kinematics(positions, flight_t),
        "orbital": orbital_density(footprints),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run deterministic BCI multi-domain simulation analytics."
    )
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    print(json.dumps(build_demo(args.seed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

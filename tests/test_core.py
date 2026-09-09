import numpy as np
import pytest

from bci_defense_analytics import (
    air_kinematics,
    bci_features,
    orbital_density,
    submarine_spectrum,
)


def test_bci_features_detects_ten_hz_peak():
    sample_rate = 256.0
    t = np.arange(512) / sample_rate
    signal = np.sin(2 * np.pi * 10 * t)

    result = bci_features(signal, sample_rate)

    assert result["peak_frequency_hz"] == pytest.approx(10.0)
    assert result["rms"] == pytest.approx(2 ** -0.5, rel=1e-3)


def test_submarine_spectrum_detects_shared_frequency():
    sample_rate = 128.0
    t = np.arange(256) / sample_rate
    channels = np.vstack(
        [
            np.sin(2 * np.pi * 12 * t),
            np.sin(2 * np.pi * 12 * t),
        ]
    )

    result = submarine_spectrum(channels, sample_rate)

    assert result["channels"] == 2
    assert result["dominant_frequency_hz"] == pytest.approx(12.0)


def test_air_kinematics_constant_velocity():
    times = np.linspace(0.0, 10.0, 21)
    positions = np.column_stack([3.0 * times, np.zeros_like(times)])

    result = air_kinematics(positions, times)

    assert result["mean_speed"] == pytest.approx(3.0)
    assert result["max_abs_acceleration"] == pytest.approx(0.0, abs=1e-10)


def test_orbital_density_identity_vectors():
    result = orbital_density(np.eye(3))

    assert result["trace"] == pytest.approx(3.0)
    assert result["mean_abs_overlap"] == pytest.approx(1.0 / 3.0)


def test_rejects_non_increasing_timestamps():
    positions = np.array([[0.0], [1.0], [2.0]])

    with pytest.raises(ValueError, match="strictly increasing"):
        air_kinematics(positions, [0.0, 0.0, 1.0])

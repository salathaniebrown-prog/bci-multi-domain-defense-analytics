"""Numerical primitives for simulation-first BCI and telemetry analytics."""

from __future__ import annotations

import numpy as np


def _as_float_array(values, name):
    array = np.asarray(values, dtype=float)
    if array.size == 0:
        raise ValueError(f"{name} must not be empty")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def bci_features(samples, sample_rate_hz):
    """Return basic signal features for one simulated biosignal channel."""
    signal = _as_float_array(samples, "samples")
    if signal.ndim != 1 or signal.size < 2:
        raise ValueError("samples must be a one-dimensional array of length >= 2")
    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive")

    centered = signal - np.mean(signal)
    rms = float(np.sqrt(np.mean(centered**2)))
    spectrum = np.abs(np.fft.rfft(centered))
    frequencies = np.fft.rfftfreq(signal.size, d=1.0 / sample_rate_hz)

    if spectrum.size > 1:
        peak_index = int(np.argmax(spectrum[1:]) + 1)
    else:
        peak_index = 0

    return {
        "mean": float(np.mean(signal)),
        "rms": rms,
        "peak_frequency_hz": float(frequencies[peak_index]),
    }


def submarine_spectrum(channels, sample_rate_hz):
    """Summarize dominant FFT frequency for simulated acoustic channels."""
    matrix = _as_float_array(channels, "channels")
    if matrix.ndim != 2 or matrix.shape[1] < 2:
        raise ValueError("channels must have shape (channel_count, sample_count>=2)")
    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive")

    centered = matrix - np.mean(matrix, axis=1, keepdims=True)
    spectra = np.abs(np.fft.rfft(centered, axis=1))
    aggregate = np.mean(spectra, axis=0)
    frequencies = np.fft.rfftfreq(matrix.shape[1], d=1.0 / sample_rate_hz)

    peak_index = int(np.argmax(aggregate[1:]) + 1)
    return {
        "channels": int(matrix.shape[0]),
        "dominant_frequency_hz": float(frequencies[peak_index]),
        "spectral_energy": float(np.sum(aggregate**2)),
    }


def air_kinematics(positions, timestamps_s):
    """Compute speed and acceleration summaries from simulated positions."""
    points = _as_float_array(positions, "positions")
    times = _as_float_array(timestamps_s, "timestamps_s")

    if points.ndim != 2 or points.shape[0] < 3:
        raise ValueError("positions must have shape (sample_count>=3, dimensions)")
    if times.ndim != 1 or times.size != points.shape[0]:
        raise ValueError("timestamps_s must align with position rows")
    if np.any(np.diff(times) <= 0):
        raise ValueError("timestamps_s must be strictly increasing")

    velocity = np.gradient(points, times, axis=0)
    speed = np.linalg.norm(velocity, axis=1)
    acceleration = np.gradient(speed, times)

    return {
        "samples": int(points.shape[0]),
        "mean_speed": float(np.mean(speed)),
        "max_speed": float(np.max(speed)),
        "max_abs_acceleration": float(np.max(np.abs(acceleration))),
    }


def orbital_density(footprints):
    """Compute a normalized overlap metric for simulated footprint vectors."""
    matrix = _as_float_array(footprints, "footprints")
    if matrix.ndim != 2 or matrix.shape[0] < 1:
        raise ValueError("footprints must be a two-dimensional matrix")

    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    normalized = np.divide(
        matrix,
        norms,
        out=np.zeros_like(matrix),
        where=norms != 0,
    )
    gram = normalized @ normalized.T
    density = float(np.mean(np.abs(gram)))

    return {
        "footprints": int(matrix.shape[0]),
        "trace": float(np.trace(gram)),
        "mean_abs_overlap": density,
    }

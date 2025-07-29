import numpy as np

def electric_to_acoustic_signal(alpha_rad, omega_rad, t_sec, theta_rad):
    """
    Directional amplitude model based on alpha:
    Δp = A(α) · sin(ωt + θ)
    A(α) = 2.5 * (1 + cos(2(α - 90))) in degrees
    Gives:
      - 5 Pa at α = 30° and 150°
      - 2.5 Pa at α = 90°
    """
    alpha_deg = np.abs(np.degrees(alpha_rad))  # Ensure symmetry

    if alpha_deg > 180:
        return 0.0

    amplitude = 2.5 * (1 + np.cos(np.radians(2 * (alpha_deg - 90))))
    phase = omega_rad * t_sec + theta_rad
    delta_p = amplitude * np.sin(phase)
    return delta_p

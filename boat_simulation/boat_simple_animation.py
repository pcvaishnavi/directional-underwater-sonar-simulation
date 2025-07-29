import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Polygon, FancyArrow
from matplotlib.widgets import Button
from electric_to_acoustic_signal import electric_to_acoustic_signal

paused = False
restart_requested = False
saved_data = []


def on_key(event):
    global paused
    if event.key == 'enter':
        paused = not paused

def on_restart(event):
    global restart_requested
    restart_requested = True

def on_pause_play(event):
    global paused
    paused = not paused
    # Update button label
    pause_button.label.set_text("Play" if paused else "Pause")

def save_data_to_excel():
    df = pd.DataFrame(saved_data)
    df.to_excel("sonar_simulation_data.xlsx", index=False)
    print("Data saved to sonar_simulation_data.xlsx")

def plot_transponder(ax, x=0, z=-5000, radius=100):
    from matplotlib.patches import Circle
    circle = Circle((x, z), radius, color='red')
    ax.add_patch(circle)
    ax.text(x + 200, z, "Transponder", fontsize=9, color='red')

def simulate_boat():
    global paused, restart_requested, pause_button
    boat_length = 2000
    boat_radius = 250
    beam_angle_deg = 6
    beam_angle_rad = np.radians(beam_angle_deg)
    virtual_beam_angle_rad = np.radians(40)

    x_vals = np.linspace(-6000, 6000, 200)
    z_boat = -50
    trans_x, trans_z = 0, -5000

    fig, ax = plt.subplots()
    fig.set_size_inches(14, 6)
    fig.canvas.mpl_connect('key_press_event', on_key)

    # Add Restart button
    ax_button_restart = plt.axes([0.90, 0.80, 0.08, 0.05])
    button_restart = Button(ax_button_restart, 'Restart', color='lightgray', hovercolor='lightblue')
    button_restart.on_clicked(on_restart)

    # Add Pause/Play button
    ax_button_pause = plt.axes([0.90, 0.72, 0.08, 0.05])
    pause_button = Button(ax_button_pause, 'Pause', color='lightgray', hovercolor='lightblue')
    pause_button.on_clicked(on_pause_play)
    
    ax_save = plt.axes([0.90, 0.64, 0.08, 0.05])
    btn_save = Button(ax_save, 'Save')
    btn_save.on_clicked(lambda event: save_data_to_excel())


    # Static text fields
    text_pressure = fig.text(0.01, 0.90, "", fontsize=11, color='purple', ha='left')
    text_beam = fig.text(0.01, 0.80, "", fontsize=11, color='darkblue', ha='left')
    text_boatx = fig.text(0.01, 0.70, "", fontsize=11, color='black', ha='left')
    text_freq = fig.text(0.01, 0.60, "", fontsize=11, color='black', ha='left')
    text_range = fig.text(0.01, 0.50, "", fontsize=11, color='red', ha='left')

    direction = 1
    i = 0
    while True:
        while paused:
            plt.pause(0.1)

        if restart_requested:
            i = 0
            direction = 1
            restart_requested = False

        boat_x = x_vals[i]

        ax.clear()
        ax.set_xlim(-6000, 6000)
        ax.set_ylim(-6000, 500)
        ax.set_aspect('equal')

        xticks = ax.get_xticks()
        yticks = ax.get_yticks()
        ax.set_xticks(xticks)
        ax.set_xticklabels([str(abs(int(label))) for label in xticks])
        ax.set_yticks(yticks)
        ax.set_yticklabels([str(abs(int(label))) for label in yticks])

        ax.set_title("Boat And Beam Simulation")
        ax.set_xlabel("X (distance in meters)")
        ax.set_ylabel("Z (depth in meters)")
        ax.grid(True)

        ax.axhline(y=0, color='blue', linestyle='-', linewidth=1.5)
        ax.fill_between(np.linspace(-6000, 6000, 500), -7000, 0, color='skyblue', alpha=0.3)

        x_profile = np.linspace(-0.5 * boat_length, 0.5 * boat_length, 200)
        z_half = boat_radius * np.sqrt(1 - (x_profile / (0.5 * boat_length)) ** 2)
        x_hull = np.concatenate([x_profile, x_profile[::-1]])
        z_hull = np.concatenate([z_half, -z_half[::-1]])
        ax.fill(x_hull + boat_x, z_hull + z_boat, color='black')

        dx = boat_x - trans_x
        dz = z_boat - trans_z
        distance = np.sqrt(dx ** 2 + dz ** 2)
        beam_radius = np.tan(beam_angle_rad) * distance

        beam = Polygon([
            [trans_x, trans_z],
            [boat_x - beam_radius, z_boat],
            [boat_x + beam_radius, z_boat]
        ], closed=True, color='lightgreen', alpha=0.5)
        ax.add_patch(beam)

        arrow_dx = dx * 0.9
        arrow_dz = dz * 0.9
        ax.add_patch(FancyArrow(
            trans_x, trans_z,
            arrow_dx, arrow_dz,
            width=10, head_width=80, head_length=100,
            color='red', alpha=0.8
        ))

        arc_len = 400
        angle = np.arctan2(dz, dx)
        arc_range = np.linspace(-beam_angle_rad, beam_angle_rad, 100)
        arc_x = trans_x + arc_len * np.cos(angle + arc_range)
        arc_z = trans_z + arc_len * np.sin(angle + arc_range)
        ax.plot(arc_x, arc_z, color='darkgreen', linewidth=2)
        label_idx = len(arc_x) // 2
        ax.text(arc_x[label_idx] + 200, arc_z[label_idx] + 200, r'$\theta = 6^\circ$', fontsize=10, color='green')

        mid_x = (boat_x + trans_x) / 2
        mid_z = (z_boat + trans_z) / 2
        ax.text(mid_x, mid_z, f"R = {distance:.1f} m", fontsize=10, color='red', weight='bold')

        plot_transponder(ax, x=trans_x, z=trans_z)

        arrow_dx_dir = 700 if direction == 1 else -700
        ax.add_patch(FancyArrow(boat_x, z_boat + boat_radius + 90,
                                arrow_dx_dir, 0,
                                width=30, head_width=60, head_length=80, color='orange'))

        alpha = np.arctan2(dz, dx)
        alpha_deg = np.degrees(alpha)
        if alpha_deg < 0:
            alpha_deg += 360

        t = i / 30.0
        freq = 1.0 - 0.5 * np.sin(alpha)
        omega = 2 * np.pi * freq

        amplitude = 5 - 2.5 * np.cos(np.radians((alpha_deg - 90) * 180 / 90))
        raw_signal = amplitude * np.sin(omega * t + virtual_beam_angle_rad)
        signal = abs(raw_signal)

        arc_len_alpha = 300
        arc_range_alpha = np.linspace(0, alpha, 100)
        arc_x_alpha = trans_x + arc_len_alpha * np.cos(arc_range_alpha)
        arc_z_alpha = trans_z + arc_len_alpha * np.sin(arc_range_alpha)
        ax.plot(arc_x_alpha, arc_z_alpha, color='orange', linewidth=2)

        label_idx_alpha = len(arc_x_alpha) // 2
        ax.text(arc_x_alpha[label_idx_alpha] + 100,
                arc_z_alpha[label_idx_alpha] + 100,
                rf'$\alpha$ = {alpha_deg:.1f}°',
                fontsize=10, color='orange')

        text_pressure.set_text(f"Acoustic Pressure (Δp) = {signal:.4f}")
        text_boatx.set_text(f"Boat X Position = {abs(boat_x):.1f} m")
        text_beam.set_text(f"Beam angle (deg) = {alpha_deg:.1f}°")
        text_freq.set_text(f"Frequency f (Hz)= {freq:.2f} Hz")
        text_range.set_text(f"Range (Distance) = {distance:.1f} m")

        print(f"Step {i+1}/{len(x_vals)}:")
        print(f"    Boat X Position     : {abs(boat_x):.2f}")
        print(f"    Beam Angle α (deg)  : {alpha_deg:.2f}")
        print(f"    Frequency f (Hz)    : {freq:.2f}")
        print(f"    Amplitude A_m(α)    : {amplitude:.4f}")
        print(f"    Range (Distance)    : {distance:.2f} m")
        print(f"    Acoustic Pressure (Δp): {signal:.4f}")
        print("--------------------------------------------------")
        saved_data.append({
            "Time (s)": t,
            "Acoustic Pressure (Δp)": signal,
            "Beam Angle (°)": alpha_deg,
            "Frequency (Hz)": freq,
            "Range (m)": distance,
            "Boat X Position (m)": boat_x
            })

        plt.draw()
        plt.pause(0.01)

        if direction == 1:
            i += 1
            if i == len(x_vals) - 1:
                direction = -1
        else:
            i -= 1
            if i == 0:
                direction = 1

    plt.show()

simulate_boat()

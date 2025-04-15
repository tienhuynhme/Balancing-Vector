import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm

st.set_page_config(page_title="Cân Bằng Động", layout="centered")
st.title("📐 Phân Tích Vector Cân Bằng Động")

M = st.number_input("🔸 Lượng mất cân bằng (g.mm)", min_value=0.0, step=1.0, value=100.0)
theta = st.number_input("🔸 Góc mất cân bằng (°)", min_value=0.0, max_value=360.0, step=1.0, value=45.0)
m_max = st.number_input("🔸 Giá trị tối đa mỗi vector thành phần (g.mm)", min_value=0.1, step=1.0, value=20.0)
angle_step = st.number_input("🔸 Bước góc hợp lệ (°)", min_value=1.0, max_value=90.0, step=1.0, value=30.0)

if st.button("🚀 Phân tách & Hiển thị"):
    theta_rad = np.radians(theta)
    Mx, My = M * np.cos(theta_rad), M * np.sin(theta_rad)
    valid_angles = np.radians(np.arange(0, 360, angle_step))
    components = []

    while np.sqrt(Mx**2 + My**2) > 0.01:
        best_angle = None
        min_error = float("inf")
        for angle in valid_angles:
            vx, vy = m_max * np.cos(angle), m_max * np.sin(angle)
            error = (Mx - vx)**2 + (My - vy)**2
            if error < min_error:
                min_error = error
                best_angle = angle

        if best_angle is None:
            break
        vx, vy = m_max * np.cos(best_angle), m_max * np.sin(best_angle)
        Mx -= vx
        My -= vy
        components.append((m_max, np.degrees(best_angle)))
        if np.sqrt(Mx**2 + My**2) < m_max:
            best_angle = np.arctan2(My, Mx)
            components.append((np.sqrt(Mx**2 + My**2), np.degrees(best_angle)))
            break

    df = pd.DataFrame(components, columns=["Magnitude (g.mm)", "Angle (°)"])
    st.subheader("📋 Danh sách vector thành phần:")
    st.dataframe(df.style.format({"Magnitude (g.mm)": "{:.2f}", "Angle (°)": "{:.2f}"}))

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')
    ax.axhline(0, color='gray', lw=0.5)
    ax.axvline(0, color='gray', lw=0.5)

    theta_rad = np.radians(theta)
    ax.quiver(0, 0, M * np.cos(theta_rad), M * np.sin(theta_rad), angles='xy', scale_units='xy', scale=1, color='red', label="Vector Tổng")

    x, y = 0, 0
    colors = cm.viridis(np.linspace(0, 1, len(components)))
    for i, (m_i, angle) in enumerate(components):
        angle_rad = np.radians(angle)
        dx, dy = m_i * np.cos(angle_rad), m_i * np.sin(angle_rad)
        ax.quiver(x, y, dx, dy, angles='xy', scale_units='xy', scale=1, color=colors[i], alpha=0.7)
        x += dx
        y += dy

    ax.set_xlim(-M, M)
    ax.set_ylim(-M, M)
    ax.set_title("Biểu đồ vector thành phần")
    ax.legend()
    st.pyplot(fig)

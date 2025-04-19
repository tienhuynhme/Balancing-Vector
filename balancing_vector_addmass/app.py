import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm

st.set_page_config(page_title="Cân Bằng Động - Add Mass", layout="centered")
st.title("⚙️ Phân Tích Vector Mất Cân Bằng (Add Khối Lượng)")

# Nhập thông số đầu vào
M = st.number_input("🔸 Tổng lượng mất cân bằng M (g.mm)", min_value=0.0, value=100.0)
theta = st.number_input("🔸 Góc mất cân bằng (°)", min_value=0.0, max_value=360.0, value=45.0)
angle_step = st.number_input("🔸 Bước góc cố định (°)", min_value=1.0, max_value=180.0, value=30.0)
fixed_r = st.number_input("🔸 Bán kính cố định để add mass (mm)", min_value=1.0, value=50.0)
fixed_m = st.number_input("🔸 Khối lượng cố định mỗi vector (g)", min_value=0.01, value=5.0)

if st.button("🚀 Phân tách & Hiển thị"):
    # Tính vector mất cân bằng gốc
    theta_rad = np.radians(theta)
    Mx, My = M * np.cos(theta_rad), M * np.sin(theta_rad)

    # Tính moment từng vector thành phần
    Mi = fixed_m * fixed_r
    n_vectors = 0
    valid_angles = np.radians(np.arange(0, 360, angle_step))
    components = []

    while np.sqrt(Mx**2 + My**2) > Mi and n_vectors < 1000:
        # Chọn góc tốt nhất để giảm sai số
        best_angle = None
        min_error = float("inf")
        for angle in valid_angles:
            vx, vy = Mi * np.cos(angle), Mi * np.sin(angle)
            error = (Mx - vx)**2 + (My - vy)**2
            if error < min_error:
                min_error = error
                best_angle = angle

        if best_angle is None:
            break

        # Trừ moment vector chọn được
        vx, vy = Mi * np.cos(best_angle), Mi * np.sin(best_angle)
        Mx -= vx
        My -= vy
        components.append((fixed_m, fixed_r, np.degrees(best_angle)))
        n_vectors += 1

    # Nếu còn dư nhỏ hơn 1 vector, tạo vector cuối cùng nhỏ hơn
    remaining_moment = np.sqrt(Mx**2 + My**2)
    if remaining_moment > 0.01:
        angle = np.arctan2(My, Mx)
        m_last = remaining_moment / fixed_r
        components.append((m_last, fixed_r, np.degrees(angle)))

    # Hiển thị bảng kết quả
    df = pd.DataFrame(components, columns=["Khối lượng (g)", "Bán kính (mm)", "Góc (°)"])
    st.subheader("📋 Danh sách vector thành phần:")
    st.dataframe(df.style.format({"Khối lượng (g)": "{:.2f}", "Bán kính (mm)": "{:.1f}", "Góc (°)": "{:.1f}"}))

    # Vẽ biểu đồ mô phỏng
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')
    ax.set_xlim(-M * 1.2, M * 1.2)
    ax.set_ylim(-M * 1.2, M * 1.2)

    # Vẽ vòng tròn rotor
    circle = plt.Circle((0, 0), fixed_r, color='lightgray', fill=False, linestyle='--')
    ax.add_patch(circle)

    # Vẽ chia độ
    for deg in range(0, 360, int(angle_step)):
        rad = np.radians(deg)
        ax.plot([0, fixed_r * 1.2 * np.cos(rad)], [0, fixed_r * 1.2 * np.sin(rad)], color='lightgray', lw=0.5, linestyle='--')
        ax.text(fixed_r * 1.3 * np.cos(rad), fixed_r * 1.3 * np.sin(rad), f"{deg}°", fontsize=8, ha='center', va='center')

    # Vẽ vector mất cân bằng gốc
    ax.quiver(0, 0, M * np.cos(theta_rad), M * np.sin(theta_rad),
              angles='xy', scale_units='xy', scale=1, color='red', label="Vector Mất Cân Bằng")

    # Vẽ các vector thành phần
    x, y = 0, 0
    colors = cm.viridis(np.linspace(0, 1, len(components)))
    for i, (mass, r, angle) in enumerate(components):
        angle_rad = np.radians(angle)
        dx, dy = mass * r * np.cos(angle_rad), mass * r * np.sin(angle_rad)
        ax.quiver(x, y, dx, dy, angles='xy', scale_units='xy', scale=1, color=colors[i], alpha=0.8)
        x += dx
        y += dy

    ax.set_title("Mô phỏng vector trên rotor")
    ax.legend()
    st.pyplot(fig)


    # Kiểm tra tổng moment thành phần
    check_Mx = sum(m * r * np.cos(np.radians(a)) for m, r, a in components)
    check_My = sum(m * r * np.sin(np.radians(a)) for m, r, a in components)
    total_moment = np.sqrt(check_Mx**2 + check_My**2)
    original_moment = M
    error = abs(total_moment - original_moment)

    st.markdown("### ✅ Kiểm tra tổng moment")
    st.write(f"• Tổng moment thành phần: {total_moment:.2f} g.mm")
    st.write(f"• Moment gốc nhập vào: {original_moment:.2f} g.mm")
    st.write(f"• Sai số còn lại: {error:.4f} g.mm")


    # Cho phép người dùng chọn số vector có thể thực hiện được
    st.markdown("### 🔧 Thực tế bạn chỉ có thể thực hiện bao nhiêu vector?")
    usable_count = st.slider("Chọn số vector có thể gắn được", min_value=1, max_value=len(components), value=len(components), step=1)

    partial_components = components[:usable_count]
    res_x = sum(m * r * np.cos(np.radians(a)) for m, r, a in partial_components)
    res_y = sum(m * r * np.sin(np.radians(a)) for m, r, a in partial_components)
    residual_moment = np.sqrt((M * np.cos(theta_rad) - res_x)**2 + (M * np.sin(theta_rad) - res_y)**2)

    st.markdown("### 📉 Sai số mất cân bằng còn lại nếu chỉ gắn được một phần:")
    st.write(f"• Số vector lý tưởng cần dùng: {len(components)}")
    st.write(f"• Số vector bạn có thể thực hiện: {usable_count}")
    st.write(f"• Moment còn dư sau khi cân bằng một phần: {residual_moment:.2f} g.mm")

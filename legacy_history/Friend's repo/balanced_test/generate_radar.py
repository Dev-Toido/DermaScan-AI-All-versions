import matplotlib.pyplot as plt
import numpy as np
import os

# Data
categories = ['Accuracy', 'Malignant Sensitivity', 'Inference Speed', 'Explainability', 'Multi-Modal', 'Offline']
N = len(categories)

# Values (scaled 0-5)
# Model A:
# Accuracy: 0.6775 * 5 = 3.39
# Malignant Sens: (0.48+0.60+0.56)/3 * 5 = 0.546 * 5 = 2.73
# Speed: let's use 1 / (time * 2) -> max cap at 5. (1 / (0.1115 * 2)) = 4.48
# Explainability: 5
# Multi-Modal: 5
# Offline: 5
values_A = [3.39, 2.73, 4.48, 5.0, 5.0, 5.0]

# Model B:
# Accuracy: 0.54 * 5 = 2.70
# Malignant Sens: (0.42+0.58+0.0)/3 * 5 = 0.333 * 5 = 1.67
# Speed: 1 / (0.1600 * 2) = 3.125
# Explainability: 0
# Multi-Modal: 0
# Offline: 0
values_B = [2.70, 1.67, 3.13, 0.0, 0.0, 0.0]

# Repeat first value to close the circle
values_A += values_A[:1]
values_B += values_B[:1]

angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

# Set dark background
plt.style.use('dark_background')

# Plot
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
fig.patch.set_facecolor('#111111')
ax.set_facecolor('#111111')

# Draw one axe per variable and add labels
plt.xticks(angles[:-1], categories, color='white', size=12)

# Draw ylabels
ax.set_rlabel_position(0)
plt.yticks([1, 2, 3, 4, 5], ["1", "2", "3", "4", "5"], color="grey", size=10)
plt.ylim(0, 5)

# Plot Model A
ax.plot(angles, values_A, linewidth=2, linestyle='solid', label='DermaScan AI V3 (Model A)', color='#00ffcc')
ax.fill(angles, values_A, '#00ffcc', alpha=0.25)

# Plot Model B
ax.plot(angles, values_B, linewidth=2, linestyle='solid', label="Friend's Model (Model B)", color='#ff3366')
ax.fill(angles, values_B, '#ff3366', alpha=0.25)

# Add legend
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), facecolor='#222222', edgecolor='none', labelcolor='white')

# Title
plt.title('DermaScan AI V3 vs Friend\'s Model', size=16, color='white', y=1.1)

# Save
save_path = os.path.join(os.path.dirname(__file__), 'comparison_radar.png')
plt.savefig(save_path, facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=300)
print(f"Saved radar chart to {save_path}")

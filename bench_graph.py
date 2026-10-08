import re
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

# Color Configuration
COLOR_MOJO = '#e06d53'
COLOR_PILLOW = '#2b5c8f'
PILLOW_ALPHA = 0.85
COLOR_GRID = '--'

# Parse the log file including errors
data = []
current_file = None
mojo_time = None
pillow_time = None
mojo_error = None
pillow_error = None

with open('log.txt', 'r', encoding='utf-8') as f:
  for line in f:
    file_match = re.search(r'Processing file:\s+(.+)', line)
    if file_match:
      if current_file is not None:
        data.append({
            'File': current_file,
            'Mojo': mojo_time,
            'Pillow': pillow_time,
            'MojoError': mojo_error,
            'PillowError': pillow_error,
        })
      current_file = file_match.group(1).strip()
      mojo_time = None
      pillow_time = None
      mojo_error = None
      pillow_error = None

    mojo_match = re.search(r'Mojo Median:\s+([\d.]+)\s+ms', line)
    if mojo_match:
      mojo_time = float(mojo_match.group(1))

    mojo_err_match = re.search(r'Error during Mojo benchmark:\s+(.+)', line)
    if mojo_err_match:
      mojo_error = mojo_err_match.group(1).strip()

    pillow_match = re.search(r'Pillow Median:\s+([\d.]+)\s+ms', line)
    if pillow_match:
      pillow_time = float(pillow_match.group(1))

    pillow_err_match = re.search(r'Error during Pillow benchmark:\s+(.+)', line)
    if pillow_err_match:
      pillow_error = pillow_err_match.group(1).strip()

# Append the last item
if current_file is not None:
  data.append({
      'File': current_file,
      'Mojo': mojo_time,
      'Pillow': pillow_time,
      'MojoError': mojo_error,
      'PillowError': pillow_error,
  })

df = pd.DataFrame(data)

# Extract format category (BMP, GIF, JPG, PNG) and short file name
df['Format'] = df['File'].apply(lambda x: x.split('/')[1].upper())
df['ShortName'] = df['File'].apply(lambda x: x.split('/')[-1])

# Create a 2x2 grid of subplots for each format
formats = sorted(df['Format'].unique())
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
axes = axes.flatten()

for i, fmt in enumerate(formats):
  ax = axes[i]
  sub_df = df[df['Format'] == fmt].sort_values('ShortName').reset_index(drop=True)

  y_pos = np.arange(len(sub_df))
  bar_height = 0.35

  # Track max value to adjust right x-limit dynamically with margin
  max_val = 0
  for idx, row in sub_df.iterrows():
    if not pd.isna(row['Mojo']):
      max_val = max(max_val, row['Mojo'])
    if not pd.isna(row['Pillow']):
      max_val = max(max_val, row['Pillow'])

  # Draw bars and text individually to handle errors and empty scales cleanly
  for idx, row in sub_df.iterrows():
    y = y_pos[idx]

    # --- Mojo Bar & Logic ---
    if not pd.isna(row['Mojo']):
      w = row['Mojo']
      ax.barh(y - bar_height / 2, w, bar_height, color=COLOR_MOJO)
      ax.text(
          w * 1.12,
          y - bar_height / 2,
          f'{w:.2f} ms',
          va='center',
          ha='left',
          fontsize=9,
          color=COLOR_MOJO,
          weight='bold',
      )
    elif row['MojoError'] is not None:
      ax.text(
          0.03,
          y - bar_height / 2,
          'Not Supported',
          transform=ax.get_yaxis_transform(),
          va='center',
          ha='left',
          fontsize=9,
          color=COLOR_MOJO,
          style='italic',
      )

    # --- Pillow Bar & Logic ---
    if not pd.isna(row['Pillow']):
      w = row['Pillow']
      ax.barh(y + bar_height / 2, w, bar_height, color=COLOR_PILLOW, alpha=PILLOW_ALPHA)
      ax.text(
          w * 1.12,
          y + bar_height / 2,
          f'{w:.2f} ms',
          va='center',
          ha='left',
          fontsize=9,
          color=COLOR_PILLOW,
          weight='bold',
      )
    elif row['PillowError'] is not None:
      ax.text(
          0.03,
          y + bar_height / 2,
          'Not Supported',
          transform=ax.get_yaxis_transform(),
          va='center',
          ha='left',
          fontsize=9,
          color=COLOR_PILLOW,
          style='italic',
      )

  # Subplot styling
  ax.set_title(f'Format: {fmt}', fontsize=13, weight='bold', pad=10)
  ax.set_yticks(y_pos)
  ax.set_yticklabels(sub_df['ShortName'], fontsize=10)
  ax.invert_yaxis()  # Top-down order

  ax.set_xscale('log')
  if max_val > 0:
    current_xmin = ax.get_xlim()[0]
    ax.set_xlim(left=current_xmin, right=max_val * 1.45)

  ax.xaxis.grid(True, which='both', linestyle=COLOR_GRID, alpha=0.5)
  ax.set_axisbelow(True)

  # Custom legend
  legend_elements = [
      Patch(facecolor=COLOR_MOJO, label='Mojo'),
      Patch(facecolor=COLOR_PILLOW, alpha=PILLOW_ALPHA, label='Pillow'),
  ]
  ax.legend(handles=legend_elements, fontsize=10, loc='lower right')

# Overall figure layout
plt.suptitle(
    'Performance Comparison: Mojo vs Pillow by Format (Lower is Better)',
    fontsize=16,
    weight='bold',
    y=0.98,
)
plt.tight_layout()

# Save plot to file without automatically opening it
plt.savefig('benchmark_comparison.png', dpi=150)
print(
    'Benchmark plot successfully saved to benchmark_comparison.png'
)
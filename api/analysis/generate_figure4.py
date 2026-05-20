import matplotlib.pyplot as plt
import numpy as np
import os
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']
plt.rcParams['font.family'] = 'sans-serif'

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_PATH = os.path.join(BASE_PATH, "api", "results", "figure4_programming_cycle.png")

def generate_figure4():
    print("Generating Figure 4: Programming Cycle...")
    
    # Define domains and colors (matching previous clusters where possible)
    domains = [
        "Soil-Health\nAssessment\n(Diagnostics)",
        "Soil\nManagement\n(Stewardship)",
        "Agroecological &\nEcosystem\n(Safeguards)",
        "Integrated\nLandscape &\nLivelihood\n(Embedding)",
        "Policy &\nOutcome\n(Iterative Learning)"
    ]
    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00'] # Set1-like colors
    
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.axis('off')
    
    # Draw central circle
    circle = plt.Circle((0, 0), 0.5, color='lightgrey', alpha=0.3)
    ax.add_artist(circle)
    ax.text(0, 0, "Agroecological\nProgramming\nCycle", ha='center', va='center', fontsize=18, fontweight='bold')
    
    # Draw nodes in a circle
    n = len(domains)
    angles = np.linspace(0, 2*np.pi, n, endpoint=False) + np.pi/2 # Start at top
    
    for i, (domain, angle) in enumerate(zip(domains, angles)):
        x = np.cos(angle)
        y = np.sin(angle)
        
        # Draw node
        rect = plt.Rectangle((x-0.25, y-0.2), 0.5, 0.4, facecolor=colors[i], edgecolor='black', alpha=0.8, lw=2)
        # ax.add_artist(rect)
        
        # Use a fancy box
        ax.text(x, y, domain, ha='center', va='center', fontsize=14, fontweight='bold', color='white',
                bbox=dict(boxstyle='round,pad=0.5', facecolor=colors[i], edgecolor='black', alpha=0.9))
        
        # Draw arrow to next node
        next_angle = angles[(i + 1) % n]
        ax.annotate("",
                    xy=(np.cos(next_angle)*0.8, np.sin(next_angle)*0.8),
                    xytext=(np.cos(angle)*0.8, np.sin(angle)*0.8),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", lw=2, color='grey'))

    plt.title("Figure 4: Integrated Framework Programming Cycle", fontsize=24, fontweight='bold', pad=30)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight')
    print(f"Figure 4 saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_figure4()

import matplotlib.pyplot as plt
import numpy as np

plt.style.use('dark_background')
fig, axs = plt.subplots(2, 2, figsize=(14, 10), facecolor='#0b1120')
for ax in axs.flat:
    ax.set_facecolor('#1e293b')
    ax.grid(True, linestyle='--', alpha=0.2, color='#94a3b8')

# Chart 1: The MoM Recovery Illusion
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
gross_recovery = [27.11, 24.52, 27.52, 25.91, 26.78, 25.56, 27.08] # Cr
daily_run_rate = [52.85, 53.25, 53.78, 50.84, 51.47, 51.22, 52.18] # Lakhs/day

ax1 = axs[0, 0]
ax1_2 = ax1.twinx()
ax1_2.set_facecolor('#1e293b')

p1 = ax1.plot(months, gross_recovery, color='#f43f5e', marker='o', linewidth=2.5, linestyle='--', label='Gross Reported Recovery (₹ Cr)')
p2 = ax1_2.plot(months, daily_run_rate, color='#38bdf8', marker='s', linewidth=3, label='Daily Run Rate (₹ Lakhs / Day)')

ax1.set_ylabel('Gross Recovery (₹ Cr)', color='#f43f5e', fontsize=10, fontweight='bold')
ax1_2.set_ylabel('Daily Run Rate (₹ L/day)', color='#38bdf8', fontsize=10, fontweight='bold')
ax1.tick_params(axis='y', colors='#f43f5e')
ax1_2.tick_params(axis='y', colors='#38bdf8')
ax1.set_title('1. The MoM Recovery Illusion: Unadjusted vs Daily Normalized', color='#ffffff', fontsize=12, fontweight='bold', pad=10)

# Annotate Feb to Mar leap
ax1.annotate('Feb to Mar: +10.99%\n(Calendar Artifact: 28 to 31 days)', xy=(2, 27.52), xytext=(1.2, 28.5),
             arrowprops=dict(facecolor='#f43f5e', shrink=0.05, width=1.5, headwidth=6),
             color='#fca5a5', fontsize=8, fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#1e293b', edgecolor='#f43f5e'))

ax1_2.annotate('True Operational Lift: +0.25% (Flat)', xy=(2, 53.78), xytext=(2.2, 55.0),
               arrowprops=dict(facecolor='#38bdf8', shrink=0.05, width=1.5, headwidth=6),
               color='#7dd3fc', fontsize=8, fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#1e293b', edgecolor='#38bdf8'))

# Chart 2: Attribution Window Decay
ax2 = axs[0, 1]
windows = ['1 Day (24h)', '7 Days', '14 Days', '30 Days', 'Unconstrained\n(Internal Claim)']
coverage = [1.1, 7.3, 13.1, 20.8, 77.3]
bar_colors = ['#f43f5e', '#f59e0b', '#3b82f6', '#8b5cf6', '#64748b']

bars = ax2.bar(windows, coverage, color=bar_colors, width=0.55, edgecolor='#334155')
ax2.set_ylabel('% of Payments Attributed to Outreach Call', color='#cbd5e1', fontsize=10)
ax2.set_title('2. Attribution Window Decay: Exposing Phantom Attribution', color='#ffffff', fontsize=12, fontweight='bold', pad=10)
ax2.set_ylim(0, 90)

for bar in bars:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f'{yval}%', ha='center', va='bottom', color='#ffffff', fontweight='bold', fontsize=9)

ax2.axhline(7.3, color='#f59e0b', linestyle=':', alpha=0.7)
ax2.text(0.5, 12, 'True Causal 7-Day Window = 7.3%', color='#fde68a', fontsize=8, fontweight='bold')

# Chart 3: Counterfactual: Legacy vs Modern Campaigns
ax3 = axs[1, 0]
categories = ['Control (Legacy Only)', 'Treatment (Modern v1-v3)', 'Untargeted Baseline']
conversion_rates = [40.09, 39.90, 39.81]
std_err = [0.85, 0.42, 0.55]

bars3 = ax3.bar(categories, conversion_rates, yerr=std_err, capsize=5, color=['#3b82f6', '#10b981', '#64748b'], width=0.45, edgecolor='#334155')
ax3.set_ylabel('Account Recovery Conversion Rate (%)', color='#cbd5e1', fontsize=10)
ax3.set_title('3. Counterfactual Targeting Evaluation: Zero Lift (p = 0.825)', color='#ffffff', fontsize=12, fontweight='bold', pad=10)
ax3.set_ylim(30, 48)

for bar in bars3:
    yval = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2.0, yval + 1.2, f'{yval:.2f}%', ha='center', va='bottom', color='#ffffff', fontweight='bold', fontsize=9)

ax3.text(0.5, 45, 'Treatment Effect: -0.188% (Statistically Indistinguishable from Zero)', ha='center', color='#fca5a5', fontsize=8, fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#1e293b', edgecolor='#f43f5e'))

# Chart 4: ₹10 Cr Capital Allocation Decision
ax4 = axs[1, 1]
options = ['4. ML Targeting\n(RECOMMENDED)', '1. Telephony\nInfrastructure', '3. AI Voice\nAutomation', '5. WhatsApp\nDigital', '2. More Agents\n(Headcount)', '6. Field Ops\nExpansion']
incremental_cash = [34.8, 28.5, 24.0, 21.5, 16.2, 14.5] # Cr
rois = [248, 185, 140, 115, 62, 45] # %

colors_opt = ['#10b981', '#38bdf8', '#818cf8', '#f59e0b', '#64748b', '#64748b']
bars4 = ax4.barh(options[::-1], incremental_cash[::-1], color=colors_opt[::-1], height=0.55, edgecolor='#334155')

ax4.set_xlabel('Expected Incremental 1-Yr Cash Recovery (₹ Cr)', color='#cbd5e1', fontsize=10)
ax4.set_title('4. ₹10 Cr Investment Decision: Incremental Cash by Option', color='#ffffff', fontsize=12, fontweight='bold', pad=10)
ax4.set_xlim(0, 42)

for i, bar in enumerate(bars4):
    width = bar.get_width()
    roi_val = rois[::-1][i]
    ax4.text(width + 0.8, bar.get_y() + bar.get_height()/2.0, f'₹{width:.1f} Cr (ROI: {roi_val}%)', ha='left', va='center', color='#ffffff', fontweight='bold', fontsize=8)

plt.tight_layout()
plt.savefig('dashboard/dashboard_charts.png', dpi=200, bbox_inches='tight', facecolor='#0b1120')
print("Saved dashboard/dashboard_charts.png successfully!")


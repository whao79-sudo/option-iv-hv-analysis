#!/usr/bin/env python3
"""
创业板ETF购12月1450 - 2024年8-9月 IV/HV 专项分析
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json, os

# ============================================================================
# 加载数据
# ============================================================================
analysis = pd.read_csv('data/analysis_data.csv')
analysis['date'] = pd.to_datetime(analysis['date'])

# 筛选 2024-08-01 到 2024-09-30
sub = analysis[(analysis['date'] >= '2024-08-01') & (analysis['date'] <= '2024-09-30')].copy().reset_index(drop=True)

print(f"8~9月数据: {len(sub)} 条交易日记录")
print(f"IV 有效: {sub['iv'].notna().sum()}/{len(sub)}")
print(f"HV20 有效: {sub['hv_20'].notna().sum()}/{len(sub)}")

# ============================================================================
# 生成图表
# ============================================================================
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
fig.suptitle('创业板 ETF 购 12 月 1450 — 2024 年 8-9 月 IV/HV 专项分析', fontsize=15, fontweight='bold')

# 图 1: 期权价格 + ETF 价格
ax1 = axes[0]
color1, color2 = 'red', 'blue'
ax1_twin = ax1.twinx()
ax1.plot(sub['date'], sub['option_close'], color=color1, linewidth=1.5, marker='.', markersize=4, label='期权价格')
ax1_twin.plot(sub['date'], sub['etf_close'], color=color2, linewidth=1.5, linestyle='--', alpha=0.7, label='ETF (159915)')
ax1.set_ylabel('期权价格 (元)', color=color1, fontsize=11)
ax1_twin.set_ylabel('ETF 价格 (元)', color=color2, fontsize=11)
ax1.set_title('期权价格 vs 标的资产价格', fontsize=12, fontweight='bold')

# 合并图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1_twin.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
ax1.grid(True, alpha=0.3)

# 图 2: IV vs HV20/HV60
ax2 = axes[1]
valid_iv = sub[sub['iv'].notna()]
valid_hv20 = sub[sub['hv_20'].notna()]
valid_hv60 = sub[sub['hv_60'].notna()]

ax2.plot(valid_iv['date'], valid_iv['iv'], color='red', linewidth=1.5, marker='.', markersize=4, label='IV (隐含波动率)')
ax2.plot(valid_hv20['date'], valid_hv20['hv_20'], color='green', linewidth=1.5, linestyle='--', label='HV20')
ax2.plot(valid_hv60['date'], valid_hv60['hv_60'], color='orange', linewidth=1.5, linestyle='-.', label='HV60')
ax2.set_ylabel('波动率 (%)', fontsize=11)
ax2.set_title('IV vs HV20 / HV60', fontsize=12, fontweight='bold')
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)
ax2.set_ylim(bottom=0)

# 图 3: IV-HV 差值
ax3 = axes[2]
valid_diff20 = sub[sub['iv_hv20_diff'].notna()]
valid_diff60 = sub[sub['iv_hv60_diff'].notna()]

ax3.fill_between(valid_diff20['date'], valid_diff20['iv_hv20_diff'], alpha=0.3, color='purple')
ax3.plot(valid_diff20['date'], valid_diff20['iv_hv20_diff'], color='purple', linewidth=1.5, marker='.', markersize=3, label='IV - HV20')
ax3.plot(valid_diff60['date'], valid_diff60['iv_hv60_diff'], color='brown', linewidth=1.5, linestyle='--', marker='.', markersize=3, label='IV - HV60')
ax3.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
ax3.fill_between(valid_diff20['date'], valid_diff20['iv_hv20_diff'], 0, where=(valid_diff20['iv_hv20_diff'] > 0), color='green', alpha=0.1)
ax3.fill_between(valid_diff20['date'], valid_diff20['iv_hv20_diff'], 0, where=(valid_diff20['iv_hv20_diff'] < 0), color='red', alpha=0.1)
ax3.set_ylabel('差值 (%)', fontsize=11)
ax3.set_xlabel('日期', fontsize=11)
ax3.set_title('IV - HV 差值（溢价/折价）', fontsize=12, fontweight='bold')
ax3.legend(loc='upper left')
ax3.grid(True, alpha=0.3)

# 日期格式
for ax in axes:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()

chart_path = 'charts/option_iv_hv_aug_sep.png'
plt.savefig(chart_path, dpi=150, bbox_inches='tight')
print(f"图表已保存到 {chart_path}")
plt.close()

# ============================================================================
# 统计摘要
# ============================================================================
summary = {
    "分析周期": "2024-08-01 至 2024-09-30",
    "交易日数": len(sub),
    "ETF 价格范围": f"{sub['etf_close'].min():.3f} ~ {sub['etf_close'].max():.3f}",
    "期权价格范围": f"{sub['option_close'].min():.4f} ~ {sub['option_close'].max():.4f}",
    "IV 有效天数": f"{sub['iv'].notna().sum()}/{len(sub)}",
    "IV 范围": f"{sub['iv'].min():.2f}% ~ {sub['iv'].max():.2f}%",
    "IV 均值": f"{sub['iv'].mean():.2f}%" if sub['iv'].notna().any() else "N/A",
    "HV20 范围": f"{sub['hv_20'].min():.2f}% ~ {sub['hv_20'].max():.2f}%",
    "HV20 均值": f"{sub['hv_20'].mean():.2f}%",
    "HV60 范围": f"{sub['hv_60'].min():.2f}% ~ {sub['hv_60'].max():.2f}%",
    "HV60 均值": f"{sub['hv_60'].mean():.2f}%",
    "IV-HV20 均值": f"{sub['iv_hv20_diff'].mean():.2f}%",
    "IV-HV60 均值": f"{sub['iv_hv60_diff'].mean():.2f}%",
}

print("\n=== 统计摘要 ===")
for k, v in summary.items():
    print(f"{k}: {v}")

with open('data/summary_aug_sep.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print("\n统计摘要已保存到 data/summary_aug_sep.json")

# ============================================================================
# 打印详细数据
# ============================================================================
print("\n=== 详细数据 (8/1 - 9/30) ===")
print(f"{'日期':<12} {'ETF':>6} {'期权':>7} {'IV':>7} {'HV20':>7} {'HV60':>7} {'IV-HV20':>8} {'IV-HV60':>8}")
print("-" * 70)
for _, r in sub.iterrows():
    iv = f"{r['iv']:.2f}%" if not pd.isna(r['iv']) else "NaN"
    hv20 = f"{r['hv_20']:.2f}%" if not pd.isna(r['hv_20']) else "NaN"
    hv60 = f"{r['hv_60']:.2f}%" if not pd.isna(r['hv_60']) else "NaN"
    d20 = f"{r['iv_hv20_diff']:.2f}%" if not pd.isna(r['iv_hv20_diff']) else "NaN"
    d60 = f"{r['iv_hv60_diff']:.2f}%" if not pd.isna(r['iv_hv60_diff']) else "NaN"
    print(f"{r['date'].strftime('%m-%d'):<12} {r['etf_close']:>6.3f} {r['option_close']:>7.4f} {iv:>7} {hv20:>7} {hv60:>7} {d20:>8} {d60:>8}")
EOF

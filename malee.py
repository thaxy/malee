import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks


def export(frames):
    for key, value in frames.items():
        path = key.replace(' ', '_').lower()
        if not path.endswith('.csv'):
            path += '.csv'
        value.to_csv(path_or_buf=path, sep=' ')


def main():
    df = pd.read_csv(
        filepath_or_buffer='stability-NMC2a-g_190806.txt',
        sep=' ',
        names=['time', 'voltage'],
        skiprows=1,
        comment='L'
    )
    df.drop_duplicates(subset='time', keep='first', inplace=True)

    lows, _ = find_peaks(df['voltage'] * -1, height=0)
    cycles = []
    last_index = 0
    for low in lows:
        df_complete_cycle = df[last_index:low]
        df_complete_cycle = df_complete_cycle[df_complete_cycle['voltage'] >= 0]
        df_cycle_peak = df_complete_cycle[::-1]['voltage'].idxmax()
        df_discharge_cycle = df_complete_cycle.loc[df_cycle_peak:]
        df_cycle_low = df_discharge_cycle[::-1]['voltage'].idxmin()

        at = df_complete_cycle.loc[df_cycle_peak]['time']
        bt = df_complete_cycle.loc[df_cycle_low]['time']
        av = df_complete_cycle.loc[df_cycle_peak]['voltage']
        bv = df_complete_cycle.loc[df_cycle_low]['voltage']
        spec_cap = 2 * (bt - at) / (av - bv)

        cycles.append((df_cycle_peak, df_cycle_low, spec_cap))
        last_index = low

    cycle_peaks = [peak for peak, _, _ in cycles]
    cycle_lows = [low for _, low, _ in cycles]
    df_global_maxima_and_minima = pd.concat(
        [df.iloc[lows], df.loc[cycle_peaks], df.loc[cycle_lows]]
    ).sort_values('time')
    df_global_maxima_and_minima.reset_index(inplace=True, drop=True)

    for i, j in df.iloc[lows].iterrows():
        plt.axvline(x=j['time'], linestyle='--', linewidth=0.2, color='gray')
    plt.axhline(y=0, linestyle='--', linewidth=0.2, color='gray')
    plt.plot('time', 'voltage', 'o', label='Measurements', data=df, markersize=1.5, linestyle='dashed', linewidth=0.8)
    plt.plot('time', 'voltage', 'x', label='Maxima and Minima / Cycle', data=df_global_maxima_and_minima)
    plt.title(f'MTEC-Co, {lows.size} Cycles')
    plt.ylabel('Voltage (V)')
    plt.xlabel('Time (s)')
    plt.legend(loc='lower right')

    df_spec_cap = pd.DataFrame(cycles, columns=['max', 'min', 'spec_cap']).reset_index()
    ax = df_spec_cap.plot.scatter(x='index', y='spec_cap', title='MTEC-Co', marker='2')
    ax.set_ylabel('Capacitance (F/g)')
    ax.set_xlabel('Cycles')

    plt.show()

    # export({'export.csv': df_spec_cap})


if __name__ == '__main__':
    main()

# See docs here:
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html

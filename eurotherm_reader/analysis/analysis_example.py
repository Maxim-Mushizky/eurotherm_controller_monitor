from eurotherm_reader.analysis.cal_analysis import ThermocoupleStatistics
import numpy as np

if __name__ == '__main__':
    ### EXAMPLE ###
    dir1 = r"C:\Maxim TEMP\TC calibration\FirstTC run" # Template- use your own files!!!!
    dir2 = r"C:\Maxim TEMP\TC calibration\SecondTC run" # Template- use your own files!!!!
    test = ThermocoupleStatistics.from_folders(dir2)

    print(test.unit_names)
    maxes = ["max1", "max2"]
    test.tc_names = maxes
    print(test.tc_names)
    test.concat_channels(5)

    # start_date = str(test.merged_df["datetime1"].iloc[0])
    start_date = "2020-09-23 00:00:00"
    end_date = "2020-09-24 06:00:00"

    test.quick_filter(5, start_date, end_date, date_sort=True)
    # Example of the add statistics dictionary
    new_stats = {
        'median': np.median,
        'peak to peak': np.ptp
    }

    ret_val = test.cal_summary(to_csv=True, suffixes=test.tc_names, add_statistics=new_stats)
    print(test.merged_df)
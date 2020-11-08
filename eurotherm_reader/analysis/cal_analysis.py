# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from numbers import Number
import os
from datetime import datetime

class ThermocoupleStatistics:

    @classmethod
    def from_folders(cls,
                   path: "str",
                   unit1_name: "str" = 'unit 1',
                   unit2_name: "str" = 'unit 2',
                   time_col: "str" = "datetime",
                   old_time_col: "str" = "time",
                   ftype: "str" = ".csv"
                     )->("ThermocoupleStatistics", "list"):

        """
        from_folders class method
        =========================

        PURPOSE
        =======
            This method provides a quick way to convert all TCReader's generated thermocouple data (in csv format)
            into pandas.dataframe object using only the folders containing these data.
            Because the dual version of TCReader is intended to be used only with 2 TC's simultaneously, both
            TC units names is required, or else the analysis will not be performed.
            TODO- could be generalized to handle any amount of input from TC

        Args:
            path: (*str)- relative or direct path to the desired measurement datasets
            unit1_name: (*str)- name of the of first TC/CK-unit
            unit2_name: (*str)- name of the of second TC/CK-unit
            time_col: (*str)- name of the new date+ time column in a YYYY-MM-DD HH:MM:ss format
            old_time_col: (*str)- name of the current time column (can be adjusted if the output csv's are changed)
            ftype: (*str)- file type where the data is TCReader generated is stored (default csv- won't work with others)

        Returns:
            ThermocoupleStatistics object
        """

        devices_params = []
        unit_df1 = []
        unit_df2 = []

        for file in os.listdir(path):
            if file.endswith(ftype):
                device_params = {}
                get_data = file.split("-")
                unit = get_data[0]
                _date = file.split(" ")[-1].split(".")[0]

                try:
                    device_params["ck_unit"] = get_data[0]
                    device_params["date"] = _date

                    if len(get_data) == 6:
                        device_params["port"] = get_data[1]
                        device_params["tc_name"] = get_data[2]
                except Exception as e:
                    print(f"An error has occurred:\n{e}")

                devices_params.append(device_params)

                if unit == unit1_name:
                    _path = os.path.join(path, file)
                    df1 = pd.read_csv(_path, engine = "c")
                    df1[time_col] = df1[old_time_col].apply(lambda row: row + f" {_date}")
                    df1[time_col] = pd.to_datetime(df1[time_col])
                    unit_df1.append(df1)

                elif unit == unit2_name:
                    _path = os.path.join(path, file)
                    df2 = pd.read_csv(_path, engine = "c")
                    df2[time_col] = df2[old_time_col].apply(lambda row: row + f" {_date}")
                    df2[time_col] = pd.to_datetime(df2[time_col])
                    unit_df2.append(df2)

        tc_df1 = pd.concat(unit_df1)  # first df
        tc_df2 = pd.concat(unit_df2)  # Second df

        return cls(tc_df1,tc_df2, *devices_params)

    def __init__(self, tc1_df, tc2_df, *device_params):

        self.tc1_df = tc1_df
        self.tc2_df = tc2_df
        self._merged_df = pd.DataFrame()

        self._params = device_params

        self._test_setpoints = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1150]

        # try to get tc names

        try:
            self._tc_names = {unit["tc_name"] for unit in self._params}
        except KeyError:
            self._tc_names = set(['TC1','TC2'])

    def concat_channels(self,
                        test_period: "int",
                        heat_time: "int" = 60,
                        col_names: "list" = ['temperature1', 'datetime1', 'temperature2', 'datetime2'],
                        date_sort: "bool" = False,
                        **pdkwargs
                        ):
        """
        PURPOSE
        =======
            Concatenate both thermocouple channels according to the time to a new dataframe.
            Additionally, add a cumulative time sums columns in seconds.
            New dataframe is named merged_df and is a property of the ThermocoupleStatistics instance.

        Args:
            test_period: (*int)- the tested temperature period in minutes
            heat_time: (*int)- the heating period (ramp period) for each temperature preset
            col_names: (*list)- list of the new column names arranged in a format of:
            ['temp_tc1', 'datetime_tc1','temp_tc2', 'datetime_tc2'].
            Can change column names but should maintain this kind of naming convention to avoid confusion.
            date_sort: (*bool)- sort merge_df according to date and time (default -False)

        Return:
            None
        """

        # Creating a merged dataframe
        self._merged_df = pd.DataFrame(**pdkwargs)
        self._merged_df = pd.concat([self.tc1_df, self.tc2_df], axis=1)

        # fixing the dataframe
        self._merged_df.pop('time')
        self._merged_df.pop('event')
        self._merged_df.reset_index(drop=True, inplace=True)
        self._merged_df.columns = col_names

        # sort according the first datetime column
        if date_sort:
            self._merged_df = self._merged_df.sort_values(col_names[1])

        test_period = test_period * 60  # convert to seconds
        heat_time = heat_time * 60  # convert to seconds
        total_setpoint_time = heat_time + test_period

        datetime1 = col_names[1]
        datetime2 = col_names[3]

        time_offset1 = time_offset2 = self._merged_df[datetime1].loc[0]

        time_cumsum1 = []
        time_cumsum2 = []

        for index, row in self._merged_df.iterrows():
            sec_counter1 = (row[datetime1] - time_offset1).seconds
            sec_counter2 = (row[datetime2] - time_offset2).seconds
            time_cumsum1.append(sec_counter1)
            time_cumsum2.append(sec_counter2)
            if sec_counter1 >= total_setpoint_time:
                time_offset1 = row[datetime1]
            if sec_counter2 >= total_setpoint_time:
                time_offset2 = row[datetime2]

        self._merged_df["time1_cumsum"] = time_cumsum1
        self._merged_df["time2_cumsum"] = time_cumsum2


    def test_statistics(self,
                        temp_column: "str",
                        temp_range: "float" = 5.0,
                        mean_std: "bool" = True,
                        max_min: "bool" =False,
                        add_stats: "dict" = {}) -> "list":

        """
        PURPOSE
        =======
            Calculate simple test statistics- finding maximum, minimum values and mean/stdev.
            Additional statistics could be easily added into this method using numpy and the add_stats dict.

        Args:
            temp_column: (*str)- name of the tested temperature column
            mean_std: (*bool)- add mean and standard deviation calculations of each temperature bin (default -True)
            max_min: (*bool)- add maximum and minimum measurements of each temperature bin (default -False)
            temp_range: (*float)- temperature range for the bins used to evaluate the statistics (default- 5.0)
            add_stats: (*dict)- additional statistics dictionary. The dict format has to be {"function_name": function object}.
                                For instance- {"median": np.median} (no closing braces).
                                Calling it has to be in the format: add_stats["median"](array_like object).


        Returns:
            test_stat: (*dict)- dict in the {'mean': [], 'std': [], 'min': [], 'max': []} format
        """

        _iterindex = 0
        temp_bins = [[]]
        test_stats = {'mean': [], 'std': [], 'min': [], 'max': []}

        temp0 = self._merged_df[temp_column].iloc[0]  # get first temp meas in the dataframe

        for index, row in self._merged_df.iterrows():
            if (row[temp_column] <= (temp0 + temp_range)) and (row[temp_column] > (temp0 - temp_range)):
                temp_bins[_iterindex].append(row[temp_column])
            else:
                temp0 = row[temp_column]
                _iterindex += 1
                temp_bins.append([])

        if mean_std:
            for tempRange in temp_bins:
                tempRange = np.array(tempRange)
                if mean_std:
                    temp_mean = tempRange.mean()
                    temp_std  = tempRange.std()
                    # fill dictionary
                    test_stats['mean'].append(temp_mean)
                    test_stats['std'].append(temp_std)

                if max_min:
                    temp_min = tempRange.min()
                    temp_max = tempRange.max()
                    # fill dictionary
                    test_stats['min'].append(temp_min)
                    test_stats['max'].append(temp_max)

                try:
                    for key in add_stats.keys():
                        res = add_stats[key](tempRange)

                        try:
                            test_stats[key].append(res)
                        except Exception:
                            test_stats[key] = []
                            test_stats[key].append(res)

                except AttributeError:
                    pass
                except Exception:
                    pass
                    pass

        return test_stats

    def filterTest_data_only(self, test_period: "int",
                             inplace: "bool" = False,
                             time_col:"str" = "time1_cumsum"):
        """
        PURPOSE
        =======
            Filter the TC generated data, stored in the merged dataframe to only relevant test data.

        EXPLANATION
        ===========
            For the TC calibration lab, the current (30/09/2020) setup is a temperature ramp to
            a setpoint and than a dwell period of a fixed time (test_period).

        Args:
            test_period: (*int)- the tested temperature period in minutes
            inplace: (*bool)- replace the current merged_df dataframe with the filtered one
            time_col: (*str)- name of the time column

        Return:
            fil_df- (*DataFrame)- the filtered data

        """
        test_period *= 60 # convert into seconds
        fil_df = self._merged_df[(self._merged_df[time_col] <= test_period) & (self._merged_df[time_col] > 0)]

        if inplace:
            try:
                self._merged_df = fil_df
            except Exception as e:
                print(f"{type(e)}:{e}\nDataFrame was not updated")

        return fil_df

    def filterTest_by_date(self,
                           start_date: "str",
                           end_date: "str",
                           time_column: "str" = "datetime1",
                           inplace: "bool"= False
                           ) -> "pandas.core.frame.DataFrame":
        try:
            df = self._merged_df[(self._merged_df[time_column] < end_date) & (self._merged_df[time_column] > start_date)]
        except Exception as e:
            print(e.args)
            df[time_column] = pd.to_datetime(self._merged_df[time_column])
            df = self._merged_df[(self._merged_df[time_column] < end_date) & (self._merged_df[time_column] > start_date)]

        if inplace:
            self._merged_df = df

        return df

    @property
    def merged_df(self):
        return self._merged_df

    @property
    def unit_names(self):
        self._units = {unit["ck_unit"] for unit in self._params}
        return self._units

    @property
    def tc_names(self):
        return self._tc_names

    @tc_names.setter
    def tc_names(self, names):
        self._tc_names = set(f"_{name}" for name in names)

    @property
    def test_setpoints(self):
        """
        test_setpoints: (*array_type)- the calibration temperature presets in a list
        """
        return self._test_setpoints

    @test_setpoints.setter
    def test_setpoints(self, setpoints):
        if isinstance(setpoints, (list, tuple)):
            if all(isinstance(x, (Number)) for x in setpoints):
                self._test_setpoints = setpoints
            else:
                raise ValueError("The Test Presets file contains none numeric values.\n"
                                 "Please change the values or the default set points will be used")
        else:
            raise AttributeError("Not an array type object ")


    def cal_summary(self,
                    temp1_col: "int" = 0,
                    temp2_col: "int" = 2,
                    temp_range: "float" = 20.0,
                    suffixes: "tuple" = ('_TC1', '_TC2'),
                    add_statistics: "dict" = {},
                    to_csv: "bool" = False,
                    mean_std = True,
                    max_min = True,
                    save_dir: "str" = os.getcwd(),
                    file_name: "str" = "test_statistics.csv",
                    time_strf_format = "%Y-%m-%d %H-%M"
                    )->"DataFrame":
        """
        PURPOSE
        =======
            Get a summary of the test statistics for both thermocouples
            Optional- save data to a csv file.

        Args:
            temp1_col: (*int) - index of the columns.values list for the first TC temperature measurements
            temp2_col: (*int) - index of the columns.values list for the second TC temperature measurements
            temp_range: (*float)- temperature range for the bins used to evaluate the statistics (default- 20.0)
            suffixes: (*tuple)- suffixes of the merged dataframe for each thermocouple.
            add_statistics: (*dict)- additional statistics dictionary. The dict format has to be {"function_name": function object}.
                       For instance- {"median": np.median} (no closing braces)
            to_csv: (*bool)- save calibration summary into csv

        Returns:
            summary dataframe

        """
        tc_stats = []
        col_names = self._merged_df.columns.values
        tc_temps = [col_names[temp1_col],col_names[temp2_col]]


        for temp in tc_temps:
            tc_stat = self.test_statistics(temp_column=temp,
                                           temp_range=temp_range,
                                           add_stats=add_statistics,
                                           mean_std = mean_std,
                                           max_min=max_min
                                           )
            tc_stat_df = pd.DataFrame(tc_stat, index=self.test_setpoints)
            tc_stats.append(tc_stat_df)

        summary = pd.merge(*tc_stats, left_index=True, right_index=True, suffixes = suffixes)

        if to_csv:
            today = datetime.now()
            today = today.strftime(time_strf_format)
            tc_names = list(self.tc_names)
            prefix_file_name = f"{tc_names[0]}-{tc_names[1]}-{today}"
            file_name = "-".join([prefix_file_name, file_name])
            _saved_path = os.path.join(save_dir, file_name)
            summary.to_csv(_saved_path)

        return summary

    def quick_filter(self, test_period: "int",
                     start_date: "str",
                     end_date: "str",
                     date_sort: "bool" = True,
                     inplace: "bool" = True)->"dict":

        """
        PURPOSE
        =======
            Allow quick and dirty filtering of the data according to specific test time period and duration.
            Note- This method may not work on several conditions, so it's better to use each method independently.

        Args:
            test_period: (*int)- the tested temperature period in minutes
            start_date: (*str)- start date for analysis and time in a YYYY-MM-DD HH:MM:ss format
            end_date: (*str)- end date for analysis and time in a YYYY-MM-DD HH:MM:ss format
            date_sort: (*bool)- sort merge_df according to date and time (default -True)
            inplace: (*bool)- apply all filters on merged_df (default -True)

        Return:
            None
        """

        self.concat_channels(test_period=test_period, date_sort = date_sort)
        self.filterTest_by_date(start_date=start_date, end_date = end_date, inplace=inplace)
        self.filterTest_data_only(test_period= test_period, inplace=inplace)


if __name__ == '__main__':
    ### EXAMPLE ### 
    dir1 = r"R:\Maxim TEMP\TC calibration\FirstTC run"
    dir2 = r"R:\Maxim TEMP\TC calibration\SecondTC run"
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


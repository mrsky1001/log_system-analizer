import csv
import subprocess

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import rrdtool
import tempfile
import re, xmljson
import os
from tabulate import tabulate
from pandas.io import json

from RRD import RRD


class MenuItem:
    def __init__(self, name, function):
        self.id = 0
        self.name = name
        self.function = function


class RRDFactory:
    def __init__(self, folder, start_point, end_point, type_command, height, width):
        self.list_menu = []
        self.start_point = start_point
        self.end_point = end_point
        self.type_command = type_command
        self.height = height
        self.width = width
        self.folder = folder
        self.list_all_params = []
        self.list_rrd = []
        self.parse_all_rrd()

        self.set_menu()

    def parse_all_rrd(self):
        print("\n---- RRD FACTORY. Load params from rrd-files ----")
        p1 = subprocess.Popen(["perl", "parsengraph.pl"], stdout=subprocess.PIPE)
        print(p1.communicate())
        p1.stdout.close()
        p1.terminate()

        descriptions = []

        with open("csv/table_description_params_rrd.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                descriptions.append(row)

        for root, dirs, files in os.walk(self.folder):
            for filename in files:
                if filename.endswith(".rrd"):
                    try:
                        rrdtool.info(root + "/" + filename)

                        # name = re.findall("[^/]*\w+$", root)[0]
                        name = ""
                        description = ""

                        for item in descriptions:
                            if filename.lower() in item[2].lower():
                                name = item[0]
                                description = item[1]
                                break

                        rrd = RRD(name_host=name,
                                  description=description,
                                  folder=root,
                                  file_name=filename,
                                  start_point=self.start_point,
                                  end_point=self.end_point,
                                  type_command=self.type_command,
                                  height=self.height,
                                  width=self.width)

                        list_ds = rrd.parse_ds
                        self.list_rrd.append(rrd)

                        for ds in list_ds:
                            self.list_all_params.append(str(rrd.name_host) + "." + str(ds))
                    except Exception as e:
                        print(e)

        return self.list_all_params

    def set_menu(self):
        self.list_menu.append(MenuItem("Display params", self.display_params))
        self.list_menu.append(MenuItem("Display list rrd-files", self.display_list_rrd_files))
        self.list_menu.append(MenuItem("Load RRD-file", str("")))
        self.list_menu.append(MenuItem("Parase to csv all rrd-files", self.csv_all_rrd))

        i = 0
        for item in self.list_menu:
            i += 1
            item.id = str(i)

    def display_params(self):
        print("\n---- RRD FACTORY. Params ----")
        print("start_point = " + str(self.start_point))
        print("end_point = " + str(self.end_point))
        print("type_command = " + str(self.type_command))
        print("height = " + str(self.height))
        print("width = " + str(self.width))
        print("folder = " + str(self.folder))

    def display_menu(self):
        print("\n---- RRD FACTORY. Menu ----")

        for item in self.list_menu:
            print(str(item.id) + str(". " + item.name))

        ans = input("Selection: ")

        try:
            for item in self.list_menu:
                if item.id == ans:
                    item.function()
                    break
        except Exception as e:
            print("Error: ")
            print(e)

        self.display_menu()

    def display_list_rrd_files(self):
        print("\n---- RRD FACTORY. List rrd-files ----")
        list_headers = ["name", "description", "file"]
        list_rows = []

        for rrd in self.list_rrd:
            list_rows.append([rrd.name_host, rrd.description, re.findall("[^/]*\w+$", rrd.folder)[0] + rrd.file_name])

        table = tabulate(list_rows, headers=list_headers, tablefmt='orgtbl')
        print(table)

    def csv_all_rrd(self):
        print("\n---- RRD FACTORY. Generate CSV from all rrd ----")
        path_csv = "csv/params_from_all_rrd.csv"
        self.csv_concat()
        # with open(path_csv, 'w') as the_file:
        #     list_headers = []
        #     list_rows = []
        #
        # for rrd in self.list_rrd:
        #     print(rrd.csv_export())
            #
            #     list_columns = res_xport['meta']['legend']
            #     list_headers += list_columns
            #     data = res_xport['data']
            #     list_rows += (data)
            #     i = 0
            #     for column in list_columns:
            #         i += 1
            #         line = re.sub("\"", "", column)
            #         if i < len(list_columns):
            #             line += ","
            #
            #         the_file.write(line)
            #     the_file.write(", ")
            # the_file.write("\n")
            # print(list_headers)
            # print(list_rows)
            # print("-------------------------")
            # i = 0
            #
            # for row in list_rows:
            #     for row2 in list_rows:
            #         index = i
            #         line = ""
            #
            #         if len(row2) < i:
            #             index = i % len(row2)
            #         line = str((0 if row2[index] is None else row2[index]))
            #         line += ","
            #         the_file.write(line)
            #     i += 1
            #     the_file.write("\n")
            #     if i == 3: break

            #

            #
            # for rrd in self.list_rrd:
            #     res_xport = rrd.xport()
            #
            #     list_columns = res_xport['meta']['legend']
            #     data = res_xport['data']
            #
            #     for head in list_columns:
            #
            #
            #     for row in data:
            #         i = 0
            #             i += 1
            #
            #             line = str((0 if column is None else column))
            #             if i < len(list_columns):
            #                 line += ","
            #             the_file.write(line)
            #     the_file.write("\n")
    def csv_concat(self):
        # the file names
        f1 = "csv/ap-11.2ff9e22d6acd301b0278263734ad875c.rrd.csv"
        f2 = "csv/asa-1.41d842d4b40b01b40903f21f77cda881.rrd.csv"
        out_f = "out.csv"

        # read the files
        df1 = pd.read_csv(f1)
        df2 = pd.read_csv(f2)

        # get the keys
        keys1 = list(df1)
        keys2 = list(df2)

        # merge both files
        for idx, row in df2.iterrows():
            data = df1[df1['timestamp'] == row['timestamp']]
            print(data)
            # if row with such id does not exist, add the whole row
            if data.empty:
                next_idx = len(df1)
                for key in keys2:
                    df1.at[next_idx, key] = df2.at[idx, key]

            # if row with such id exists, add only the missing keys with their values
            else:
                i = int(data.index[0])
                for key in keys2:
                    print(key)
                    # if key not in keys1:
                        # df1.at[i, key] = df2.at[idx, key]
        # print(df1)
        # save the merged files
        # df1.to_csv(out_f, index=False, encoding='utf-8', quotechar="", quoting=csv.QUOTE_NONE)

    def correlation_all_matrix(self):
        data = pd.read_csv(self.rrd.csv_export())
        corrmat = data.corr()

        f, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(corrmat, mask=sns.np.zeros_like(corrmat, dtype=sns.np.bool),
                    cmap=sns.diverging_palette(220, 10, as_cmap=True), square=True, ax=ax)
        plt.savefig('graphs/correlation_matrix.png')
        plt.show()


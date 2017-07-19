# -*- coding: utf8 -*-

import csv

import matplotlib.pyplot as plt
import numpy as np


nameList = []
valueList = []
BAR_WIDTH = 0.5
NUM_GROUP = 34


def read_data():
    fin = csv.reader(open("coef_full.csv"))
    for row in fin:
        nameList.append(row[0])
        valueList.append(float(row[1]))


def show_fig():
    ax = plt.figure().add_subplot(111)
    plt.yscale('log')
    index = np.arange(NUM_GROUP)
    rects = plt.bar(index[:10], valueList[:10], BAR_WIDTH, color='b')
    plt.xticks(index[:10] + BAR_WIDTH - 0.5, nameList[:10], fontsize=12)

    for (a, b) in zip(index[:10], valueList[:10]):
        plt.text(a, b, '%.6f' % b, ha='center', va='bottom')

    plt.show()


def main():
    read_data()
    show_fig()


if __name__ == "__main__":
    main()

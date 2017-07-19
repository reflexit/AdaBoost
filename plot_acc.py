# -*- coding: utf8 -*-

import csv
from datetime import datetime

import matplotlib.dates as m_dates
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


dates = []
accu = []


def read_data():
    fin = csv.reader(open("acc_full.csv"))
    for row in fin:
        if row[0][-4:] >= "2013":
            break
        dates.append(row[0])
        accu.append(float(row[1]))


def show_fig():
    xs = [datetime.strptime(d, '%m/%d/%Y').date() for d in dates]
    x_major_locator = MultipleLocator(30)
    
    plt.gca().xaxis.set_major_formatter(m_dates.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(x_major_locator)

    plt.plot(xs, accu, color='c')
    plt.xlim([xs[0], xs[-1]])
    plt.ylim([0.0, 1.0])
    plt.gca().fill_between(xs, 0, accu, color='c')
    plt.gcf().autofmt_xdate()
    plt.show()


def main():
    read_data()
    show_fig()


if __name__ == "__main__":
    main()

# -*- coding: utf8 -*-

# Training data row format:
# [0]~[44]      original data
# [45]          classifier
# [46]          weight

import csv
import math

from sklearn import linear_model


# constants and global variables
temp = []   # temporary data
train = []  # training data
test = []   # test data
date = "20120104"
thresh_train = 0.3   # training data selection threshold
NUM_ROUND = 20   # number of training rounds
regr_list = []
alpha_list = []
coef_list = []
accuracy = 0.0


def training_process():
    global train, regr_list, alpha_list, coef_list

    coef_list = [0.0] * 34
    
    # evaluate factors
    for idx in range(9, 43):
        train.sort(key=lambda x: float(x[idx]), reverse=True)
        for i in range(len(train)):
            train[i][idx] = eval(train[i][idx])     # float(i + 1) / len(train)
    
    # initialize weight
    for i in range(len(train)):
        train[i].append(1.0 / len(train))
    
    for rnd in range(NUM_ROUND):
        # generate data for fitting
        xs = []
        ys = []
        ws = []
        for row in train:
            xs.append(row[9:43])
            ys.append(0 if (row[45] == -1) else 1)
            ws.append(row[46])

        regr = linear_model.LogisticRegression()
        regr.fit(xs, ys, ws)
        regr_list.append(regr)
        coefs = regr.coef_
        # print coefs

        # calculate error
        w_error = 0.0
        y_verify = regr.predict(xs)
        for i in range(len(train)):
            if not ((y_verify[i] == 1 and train[i][45] == 1) or (y_verify[i] == 0 and train[i][45] == -1)):
                w_error += train[i][46]
        # print w_error
        if w_error <= 1.0e-7:
            break

        # calculate alpha
        alpha = 0.5 * math.log((1.0 - w_error) / w_error)
        alpha_list.append(alpha)

        # calculate coef
        for i in range(len(coef_list)):
            coef_list[i] += alpha * coefs[0][i]
        
        # adjust weights
        w_sum = 0.0
        for i in range(len(train)):
            if (y_verify[i] == 1 and train[i][45] == 1) or (y_verify[i] == 0 and train[i][45] == -1):
                # hypothesis correct
                train[i][46] *= math.exp(-alpha_list[-1])
            else:
                # hypothesis wrong
                train[i][46] *= math.exp(alpha_list[-1])
            w_sum += train[i][46]

        # normalize weights
        for row in train:
            row[46] /= w_sum


def prediction():
    global test, accuracy
    
    # evaluate factors
    for idx in range(9, 43):
        test.sort(key=lambda x: float(x[idx]), reverse=True)
        for i in range(len(test)):
            test[i][idx] = eval(test[i][idx])   # float(i + 1) / len(test)

    # apply prediction models
    test.sort(key=lambda x: int(x[1][0:6]))
    for row in test:
        p_sum = 0.0
        for i in range(len(alpha_list)):
            p1 = regr_list[i].predict([row[9:43]])[0]
            if p1 == 1:
                p_sum += alpha_list[i]
            elif p1 == 0:
                p_sum -= alpha_list[i]
            else:
                raise ValueError("Invalid prediction: %s" % p1)
        row.append(p_sum)
        # print row[1], row[46]

    # evaluation
    cnt_past = 0
    # cntFuture = 0
    for row in test:
        # if (float(row[43]) >= 0.0 and row[46] >= 0.0 or float(row[43]) < 0.0 and row[46] < 0.0):
        #     cntFuture += 1
        if row[45] * row[46] > 0.0:
            cnt_past += 1
    accuracy = float(cnt_past) / len(test)
    # print "Future accuracy: %.4f" % (float(cntFuture) / len(test))


def main():
    global temp, train, test, date, regr_list, alpha_list, coef_list

    facc = open("acc.csv", "wb")
    wacc = csv.writer(facc)

    fcoef = open("coef.csv", "wb")
    wcoef = csv.writer(fcoef)
    
    fout = open("out.csv", "wb")
    writer = csv.writer(fout)
    
    # read in data
    fin = csv.reader(open("f.csv"))
    rows = [row1 for row1 in fin]
        
    for row1 in rows:
        if date >= "20130101":
            break
        if row1[2][0] != "2" or row1[7] != "0" or row1[8] != "0":   # eliminate st & new stocks
            continue
        if row1[2] < date:
            continue
        if row1[2] == date:
            temp.append(row1)
            continue
        else:
            print date, len(temp),
            
            # select training & test data
            temp.sort(key=lambda x: float(x[44]), reverse=True)    # [44]: train return5; [43]: train future5
            for i in range(len(temp)):
                if i < len(temp) * thresh_train:
                    temp[i].append(1)
                elif i < len(temp) * (1.0 - thresh_train):
                    temp[i].append(0)
                else:
                    temp[i].append(-1)
            temp = filter(lambda x: x[45] != 0, temp)  # only retain stocks that are strong or weak enough
            test = filter(lambda x: int(x[1][0:6]) % 5 == 0, temp)     # ~20%
            train = filter(lambda x: int(x[1][0:6]) % 5 != 0, temp)    # ~80%
            
            training_process()
            prediction()

            print "%.4f" % accuracy
            
            for row in test:
                writer.writerow([row[1], row[2], row[43], row[44], row[45], row[46]])

            wacc.writerow(["%s/%s/%s" % (date[4:6], date[6:8], date[0:4]), accuracy])
            coef_list.insert(0, "%s/%s/%s" % (date[4:6], date[6:8], date[0:4]))
            wcoef.writerow(coef_list)
            
            del temp[:]
            del train[:]
            del test[:]
            del regr_list[:]
            del alpha_list[:]
            del coef_list[:]
            date = row1[2]
            temp.append(row1)


if __name__ == "__main__":
    main()

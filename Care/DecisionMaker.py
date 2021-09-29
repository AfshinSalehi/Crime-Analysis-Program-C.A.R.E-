from collections import OrderedDict

def radialStat(input):
    counter = OrderedDict()
    for a, b in input:
        t = (a, b)
        counter[t] = counter.get(t, 0) + 1


    final = [[a, b, v] for (a, b), v in counter.items()]

    finalNoAvg = sorted(final, key=lambda final: final[2],
                        reverse=True)  # lambda just search for index number 2 instead of whole 3 items of each inner list  (reversed)


    finalNoAvgZipped = zip(*finalNoAvg)

    average = sum(finalNoAvgZipped[2]) / len(finalNoAvgZipped[2])
    finalwAvg = []

    # check whether count index is bigger than average or not
    for i in finalNoAvg:
        if i[2] > average:
            finalwAvg.append(i)
        else:
            continue
    IO = open('workfile.txt', 'w')
    IO.write(str(finalwAvg))
    return finalwAvg



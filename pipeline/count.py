def count_nums(a:list, value:float, i:int):
    if 99.9 <= value < 100.0:
        a[0][i] += 1
    elif 100.0 <= value < 100.1:
        a[1][i] += 1
    elif 100.1 <= value < 100.2:
        a[2][i] += 1
    elif 100.2 <= value < 100.3:
        a[3][i] += 1
    elif 100.3 <= value < 100.4:
        a[4][i] += 1
    elif 100.4 <= value < 100.5:
        a[5][i] += 1

        
import numpy as np

def moving_average(x, weight, number_of_points):
    size = len(x)
    output = [0]*size
    weights=[weight/number_of_points for i in range(0, number_of_points)]

    for i in range(0,size):
        current_index = i
        j = 0
        while current_index - 1 >= 0 and j < len(weights):
            output[i] += weights[j]*x[current_index]
            j += 1
            current_index -= 1
    return output

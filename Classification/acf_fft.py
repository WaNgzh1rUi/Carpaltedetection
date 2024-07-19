import numpy as np
import matplotlib.pyplot as plt

def segment_periodicity_detection(time_series):
    n = len(time_series)
    best_period = 0
    max_matches = 0

    for p in range(1, n // 2 + 1):
        shifted_series = np.roll(time_series, p)
        matches = np.sum(time_series == shifted_series)

        if matches > max_matches:
            max_matches = matches
            best_period = p

    return best_period

# Example usage
time_series = np.array([177,139,166,167,164,81,184,188,149,164,56,104,180,148,172,173,176,76,183,195,147])
plt.plot(time_series)
period = segment_periodicity_detection(time_series)
print(f"The detected period is: {period}")
plt.show()


import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

# Updated dataset to ensure curves meet at $30 for the first time
lowest_prices = [5, 10, 3, 10, 5, 12, 150, 3.99, 5, 5, 5, 10, 10,10, 5, 10, 10, 10, 5, 5, 5]
highest_prices = [100, 40, 12, 50, 60, 24, 300, 11.99, 10, 15, 10, 30, 30, 30, 30, 40 , 50 ,50 , 60 , 70, 50]

#getting the size of the dataset
n_lowest_prices = len(lowest_prices)
n_highest_prices = len(highest_prices)

print(n_lowest_prices)
print(n_highest_prices)

# Kernel Density Estimation for smooth PDF curves
lowest_kde = gaussian_kde(lowest_prices)
highest_kde = gaussian_kde(highest_prices)

# Generating range for the x-axis
x_range = np.linspace(min(lowest_prices + highest_prices) - 10,
                      max(lowest_prices + highest_prices) + 10, 1000)

# Evaluating KDE for both sets of prices
lowest_pdf = lowest_kde(x_range)
highest_pdf = highest_kde(x_range)

#find the intersection points of the two curves
intersection_points = []
for i in range(len(lowest_pdf)):
    if lowest_pdf[i] == highest_pdf[i]:
        intersection_points.append(x_range[i])
        
print(intersection_points)

# Plotting the updated PDF curves
plt.figure(figsize=(10, 6))
plt.plot(x_range, lowest_pdf, label="Lowest Prices", lw=2)
plt.plot(x_range, highest_pdf, label="Highest Prices", lw=2, linestyle='--')
plt.title("Updated Smooth PDF Curves for Lowest and Highest Prices")
plt.xlabel("Price (per month)")
plt.ylabel("Density")
plt.legend()
plt.grid()
plt.show()

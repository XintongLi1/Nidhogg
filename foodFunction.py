from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt


# define type of function to search
def model_func(x, a, k, b):
    return a * np.exp(-k * x) + b


# sample data
x = np.array([5, 10, 15, 20, 30, 50, 60, 80, 90, 99])
y = np.array([1.7, 1.3, 1, 0.8, 0.5, 0.3, 0.22, 0.16, 0.14, 0.1])

# curve fit
p0 = (1., 1.e-5, 1.)  # starting search koefs
opt, pcov = curve_fit(model_func, x, y, p0)
a, k, b = opt
# test result
x2 = np.linspace(1, 100, 1)
y2 = model_func(x2, a, k, b)
fig, ax = plt.subplots()
ax.plot(x2, y2, color='r', label='Fit. func: $f(x) = %.3f e^{%.3f x} %+.3f$' % (a, k, b))
ax.plot(x, y, 'bo', label='data with noise')
ax.legend(loc='best')
plt.show()

"""
Thoughts on Improvement:

Use reinforcement learning to figure out the best coefficients
    - Food function
    - Guess rival's strategy
    - Weight on Corners
    - Weight on area around rival snakes
    - level of DFS
    
"""



#  Tutorial youtube: https://www.youtube.com/watch?v=DAQNHzOcO5A
import matplotlib.pyplot as plt
import numpy as np
import seaborn
import pandas as pd

# x = [0, 1, 2, 3, 4]
# y = [0, 2, 4, 6, 8]
#
# # Resize graph
# plt.figure(figsize=(16, 9), dpi=100)
#
# # Use shorthand notation
# plt.plot(x, y, 'b^--', label='2x')
#
# # Line number 2
# x2 = np.arange(0, 4.5, 0.5)
# plt.plot(x2[:6], x2[:6] ** 2, 'r', label='x^2')
# plt.plot(x2[5:], x2[5:] ** 2, 'r--')
#
# plt.title('First graph', fontdict={'fontname': 'Comic Sans MS', 'fontsize': 20})
# plt.xlabel('X Axis')
# plt.ylabel('Y Axis')
#
# plt.xticks([0, 1, 2, 3, 4])
#
# plt.legend()
#
# plt.savefig('mygraph.png', dpi=300)
#
# plt.show()


seaborn.set(style='ticks')

x = np.linspace(0.2,10,100)
fig, ax = plt.subplots()
ax.plot(x, 1/x)
ax.plot(x, np.log(x))
ax.set_aspect('equal')
ax.grid(True, which='both')
seaborn.despine(ax=ax, offset=0) # the important part here

plt.show()
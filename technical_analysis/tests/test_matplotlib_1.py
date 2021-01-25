import matplotlib.pyplot as plt

# x = list(range(0, 10))
# y = list(range(-10, 0))
#
# plt.plot(x, y)
# plt.show()

a = [0, -100, 25, 67, -323]
b = [0, 3, 7, 3, 9]

# plt.axis([-50, 80, 2, 8])
# plt.title('Triangle')
# plt.xlabel("Array A")
# plt.ylabel("Array B")
#
# plt.xticks((-40, -20, 0, 20, 40, 60, 80), ('h', 'e', 'l', 'l', 'o', 'o', 'o'))

# plt.plot(a, b, color='red')
plt.hist(a)
plt.show()
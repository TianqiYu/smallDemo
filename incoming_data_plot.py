import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
plt.style.use('ggplot')
plt.clf()

x = np.arange(0, 2*np.pi, 0.1)
y = np.sin(x)

fig, axes = plt.subplots(nrows=2)

styles = ['r-', 'g-']
def plot(ax, style):
    return ax.plot(x, y, style, animated=True)[0]
lines = [plot(ax, style) for ax, style in zip(axes, styles)]

def animate(i):
    for j, line in enumerate(lines, start=1):
        line.set_ydata(np.sin(j*x + i/10.0))
    return lines

# We'd normally specify a reasonable "interval" here...
ani = animation.FuncAnimation(fig, animate, xrange(1, 200), 
                              interval=0, blit=True)
plt.show()
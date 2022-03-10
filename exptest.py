import matplotlib.pyplot as plt

fig = plt.figure()
ax=fig.add_subplot(111)
plt.plot([0,5],[0,6], alpha=0)
plt.xlim([-1,6])
plt.ylim([-1,6])

for i in range(6):
    for j in range(6):
        an = plt.annotate("Kill me",xy=(j,i), picker=5)


def onclick(event):
    event.artist.set_text("I'm killed")
    event.artist.set_color("g")
    event.artist.set_rotation(20)
    # really kill the text (but too boring for this example;-) )
    #event.artist.set_visible(False)
    # or really REALLY kill it with:
    #event.artist.remove()
    fig.canvas.draw()


cid = fig.canvas.mpl_connect('pick_event', onclick)

plt.show()
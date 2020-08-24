import matplotlib.pyplot as plt


tools = ['sciscore', 'limitation-recognizer', 'oddpub', 'barzooka', 'jetfighter', 'trial-identifier']
vals = []
with open('performance-data/data.csv', 'r') as f:
    for line in f:
        vals.append([int(val) for val in line.replace('\n', '').split(',')])

sciscore = [val[0] for val in vals]
limitation = [val[1] for val in vals]
oddpub = [val[2] for val in vals]
barzooka = [val[3] for val in vals]
jetfighter = [val[4] for val in vals]
trial = [val[5] for val in vals]

plt.plot(sciscore, label='sciscore')
plt.plot(limitation, label='limitation-recognizer')
plt.plot(oddpub, label='oddpub')
plt.plot(barzooka, label='barzooka')
plt.plot(jetfighter, label='jetfighter')
plt.plot(trial, label='trial-identifier')
plt.plot()
plt.legend()

plt.show()
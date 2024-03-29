# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 23:55:55 2020

@author: sammy
"""


# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 16:56:48 2019
@author: Sam
"""
import csv
from operator import itemgetter
import numpy as np
import matplotlib.pyplot as plt
import settings

#League info and how many seasons to simulate
totWeeks = 13
teams = settings.teams
sims = 100#00000

with open('oldgames.txt') as f:
    reader = csv.reader(f, delimiter='\t')
    games = list(reader)
   
#Find out how many weeks have been played
weeks = int(games[0][0])

m = 3
#Find your team names
records = [[0] * m for i in range(teams)]
recordsSim = [[0] * m for i in range(teams)]
names = [None]*teams
for i in range(0, teams):
    records[i][0] = games[i][1]
    recordsSim[i][0] = games[i][1]
    names[i] = games[i][1]

#Find the number of wins for each team and their average score
for i in range(0, teams*weeks):
    score = float(games[i][3])
    records[i%teams][2] += score/weeks
    oppo = games[i][2]
    index = names.index(oppo)
    oppoScore = float(games[(i//teams)*teams + index][3])
    if(score > oppoScore):
        records[i%teams][1] += 1

mini = 65
#Find the number of wins for each team and their average score
for i in range(0, teams*weeks):
    score = float(games[i][3])
    recordsSim[i%teams][2] += max(score, mini)/weeks
    oppo = games[i][2]
    index = names.index(oppo)
    oppoScore = float(games[(i//teams)*teams + index][3])
    if(score > oppoScore):
        recordsSim[i%teams][1] += 1

#Find the standard deviation in scores, used to simulate games
devs = np.zeros(teams)
for i in range(0, teams*weeks):
    score = max(float(games[i][3]), mini)
    devs[i%teams] += score**2
devs = devs/weeks

for i in range(0, teams):
    devs[i] = devs[i] - (recordsSim[i][2])**2
scoreDev = np.mean(np.sqrt(devs))
print(names)
print(np.sqrt(devs))
print(scoreDev)

sortDs = np.argsort(np.sqrt(devs))
namessort = np.array(names)[sortDs]

index = 1.5*np.arange(teams)
bar_width = 0.8

rects1 = plt.barh(index, np.sqrt(devs)[sortDs], bar_width)
plt.xlabel('Score Std. Dev.')
plt.yticks(index, namessort)
plt.show()

#Also keep track of the total score, good for cross validation as this is what 
#Yahoo does
recs = sorted(records, key=itemgetter(2), reverse=True)
recs = sorted(recs, key=itemgetter(1), reverse=True)
for i in range(0, teams):
    recs[i][2] *= weeks
    recordsSim[i][2] *= weeks
print(recs)

#Open the file with the list of upcoming game info
with open('futureGames.txt') as f:
    reader = csv.reader(f, delimiter='\t')
    future = list(reader)
    
#Use the average score for each team to simulate the remainder of the season once
def makePred(records, teams, totWeeks, weeks, scoreDev, names):
    for i in range(0, teams*(totWeeks - weeks)):
        future[i][3] = np.random.normal(records[i%teams][2]/weeks, scoreDev)
    
    m = 3
    subRecords = [[0] * m for i in range(teams)]
    
    for i in range(0,teams*(totWeeks - weeks)):
        score = float(future[i][3])
        subRecords[i%teams][2] += score
        oppo = future[i][2]
        index = names.index(oppo)
        oppoScore = float(future[(i//teams)*teams + index][3])
        if(score > oppoScore):
            subRecords[i%teams][1] += 1
    for i in range(0, teams):
        subRecords[i][0] = names[i]
    return subRecords

#Simulate a season a number of times and keep track of outcomes,
#Assumung the top 2 teams get byes and the top 5 make the playoffs
#With the 6th seed determined by total points from teams 6-12
#Change that if your league is a different format
byes = np.zeros(teams)
play = np.zeros(teams)
punish = np.zeros(teams)
six = np.zeros(teams)
for i in range(0, sims):
    if(i%1000 == 0):
        print(100.0*i/sims)
    m = 3
    recTemp = [[0] * m for j in range(teams)]
    recSim = [[0] * m for j in range(teams)]
    for p in range(0, m):
        for q in range(0, teams):
            recTemp[q][p] = records[q][p]
            recSim[q][p] = recordsSim[q][p]
    for i in range(0, teams):
        recSim[i][2] += np.random.normal(0, scoreDev*np.sqrt(weeks))
    subRs = makePred(recSim, teams, totWeeks, weeks, scoreDev, names)
    #print(subRs)
    for j in range(0, teams):
        recTemp[j][1] += subRs[j][1]
        recTemp[j][2] += subRs[j][2]
    ranks = sorted(recTemp, key=itemgetter(2), reverse=True)
    ranks = sorted(ranks, key=itemgetter(1), reverse=True)
    #print(ranks)
    byes[names.index(ranks[0][0])] += 1
    byes[names.index(ranks[1][0])] += 1
    play[names.index(ranks[0][0])] += 1
    play[names.index(ranks[1][0])] += 1
    play[names.index(ranks[2][0])] += 1
    play[names.index(ranks[3][0])] += 1
    play[names.index(ranks[4][0])] += 1
    maxi = 0
    name = ''
    ind = -1
    for j in range(5, teams):
        if(ranks[j][2] > maxi):
            ind = j
            maxi = ranks[j][2]
            name = ranks[j][0]
    play[names.index(name)] += 1
    six[names.index(name)] += 1
    punish[names.index(ranks[teams-1][0])] += 1
print(byes/sims)
print(play/sims)
print(punish/sims)
print(names)

# data to plot
n_groups = teams
m1 = byes/sims
m2 = play/sims
m3 = punish/sims
m4 = six/sims

index = 1.5*np.arange(n_groups)
bar_width = 0.35
opacity = 0.8


rects1 = plt.barh(index, m1, bar_width,
alpha=opacity,
color='b',
label='Bye Prob')

rects2 = plt.barh(index + bar_width, m2, bar_width,
alpha=opacity,
color='g',
label='POff Prob')

rects20 = plt.barh(index + bar_width, m4, bar_width,
alpha=opacity,
color='yellow',
label='6 Seed Prob')

rects3 = plt.barh(index + 2*bar_width, m3, bar_width,
alpha=opacity,
color='r',
label='Punish Prob')

plt.xlabel('Probability')
plt.title('Probabilities for Each Team')
plt.yticks(index + bar_width, names)
plt.legend(loc = 'best')

plt.tight_layout()
plt.savefig('sim.png')
plt.show()

sorty = np.argsort(m2)

rects1 = plt.barh(index, m1[sorty], bar_width,
alpha=opacity,
color='b',
label='Bye Prob')

rects2 = plt.barh(index + bar_width, m2[sorty], bar_width,
alpha=opacity,
color='g',
label='POff Prob')

rects20 = plt.barh(index + bar_width, m4[sorty], bar_width,
alpha=opacity,
color='yellow',
label='6 Seed Prob')

rects3 = plt.barh(index + 2*bar_width, m3[sorty], bar_width,
alpha=opacity,
color='r',
label='Punish Prob')

namessort = np.array(names)[sorty]
plt.xlabel('Probability')
plt.title('Probabilities for Each Team')
plt.yticks(index + bar_width, namessort)
plt.legend(loc = 'best')

plt.tight_layout()
plt.savefig('simSort.png')
plt.show()
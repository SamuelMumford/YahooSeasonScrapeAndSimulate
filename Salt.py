# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 23:55:55 2020

@author: sammy
"""

import csv
from operator import itemgetter
import numpy as np
import matplotlib.pyplot as plt
import settings
import seaborn as sns
import copy
import matplotlib.cm as cm

teams = settings.teams

with open('oldgames.txt') as f:
    reader = csv.reader(f, delimiter='\t')
    games = list(reader)
   
#Find out how many weeks have been played
weeks = int(games[0][0])

m = 4
#Find your team names
records = [[0] * m for i in range(teams)]
runningSalt = [[0] * (weeks+1) for i in range(teams)]
names = [None]*teams
for i in range(0, teams):
    records[i][0] = games[i][1]
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
        runningSalt[i%teams][i//teams] -= 1
        
#Find the expected wins for each team
expWins = [0]*teams
vals = np.linspace(0, 1, teams)
score_list = [float(item[3]) for item in games]
for i in range(0, weeks):
    scores = score_list[teams*i:teams*(i+1)]
    sorty = np.argsort(scores)
    for j in range(0, teams):
        expWins[sorty[j]] += vals[j]
        runningSalt[sorty[j]][i] += vals[j]
for i in range(0, teams):
    records[i][3] = expWins[i]
exp = np.array(expWins)
wins = np.array([float(item[1]) for item in records])
salt = exp - wins

for i in range(0, teams):
    for j in range(0, weeks-1):
        runningSalt[i][weeks-j-2] += runningSalt[i][weeks-j-1]
    runningSalt[i][:] = runningSalt[i][::-1]
#print(runningSalt)

sortWins = np.argsort(exp)
namessort = np.array(names)[sortWins]

sortSalt = np.argsort(salt)
namesSalt = np.array(names)[sortSalt]

index = 1.5*np.arange(teams)
bar_width = 0.8

colors = cm.jet(np.linspace(1, 0, teams))#sns.color_palette("husl", n_colors = teams)
for i in range(0, teams):
    plt.plot(runningSalt[sortSalt[teams-i-1]][:], label = names[sortSalt[teams-i-1]], color = colors[i])
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xlabel('Weeks')
plt.ylabel('Salt')
plt.show()

maxi = max(exp)
lines = int(np.round(2*maxi))
for i in range(0, lines+1):
    plt.vlines(.5*i, min(index)-1, max(index)+1, alpha=0.25)
rects1 = plt.barh(index, exp[sortWins], bar_width)
plt.xlabel('Expected Wins')
plt.yticks(index, namessort)
plt.show()

rects1 = plt.barh(index, salt[sortSalt], bar_width)
maxi = max(salt)
lines = int(np.round(2*maxi))
for i in range(0, lines+1):
    plt.vlines(.5*i, min(index)-1, max(index)+1, alpha=0.25)
mini = min(salt)
lines = int(np.round(2*np.abs(mini)))
for i in range(0, lines+1):
    plt.vlines(-.5*i, min(index)-1, max(index)+1, alpha=0.25)
plt.vlines(0, min(index)-1, max(index)+1)
plt.xlabel('Salt')
plt.yticks(index, namesSalt)
plt.show()

#Also keep track of the total score, good for cross validation as this is what 
#Yahoo does
recs = sorted(records, key=itemgetter(2), reverse=True)
recs = sorted(recs, key=itemgetter(1), reverse=True)
for i in range(0, teams):
    recs[i][2] *= weeks

ranks = sorted(records, key=itemgetter(2), reverse=True)
ranks = sorted(ranks, key=itemgetter(1), reverse=True)
print(ranks)

SupRecs = copy.deepcopy(records)
for i in range(0, teams):
    loser = 1
    for j in range(0, teams):
        if(i != j):
            if(exp[i] < exp[j] and (np.abs(exp[i] - exp[j]) > .01)):
                loser += 1
            if(np.abs(exp[i] - exp[j]) < .01):
                loser += .5
    SupRecs[i].append(loser)
    SupRecs[i].append(0)
    SupRecs[i].append(0)
SupRecs = sorted(SupRecs, key=itemgetter(2), reverse=True)
SupRecs = sorted(SupRecs, key=itemgetter(1), reverse=True)
for i in range(0, teams):
    SupRecs[i][5] = i + 1
    SupRecs[i][6] = i + 1 - SupRecs[i][4]
SaltRecs = sorted(SupRecs, key=itemgetter(6), reverse=True)
print(SaltRecs)

def column(matrix, i):
    return [row[i] for row in matrix]

SaltRs = column(SaltRecs, 6)[::-1]
rects1 = plt.barh(index, SaltRs, bar_width)
maxi = max(SaltRs)
lines = int(np.round(maxi))
for i in range(0, lines+1):
    plt.vlines(i, min(index)-1, max(index)+1, alpha=0.25)
mini = min(SaltRs)
lines = int(np.round(np.abs(mini)))
for i in range(0, lines+1):
    plt.vlines(-i, min(index)-1, max(index)+1, alpha=0.25)
plt.xlabel('League Standings Salt')
plt.yticks(index, column(SaltRecs, 0)[::-1])
plt.show()
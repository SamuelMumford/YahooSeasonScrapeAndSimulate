# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 22:01:09 2019
@author: Sam
"""

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import numpy as np
import settings
import re

LOGIN_TIME = 30
SLEEP_SECONDS = 2
END_WEEK = 18
PAGES_PER_WEEK = 4
YAHOO_RESULTS_PER_PAGE = 25 # Static but used to calculate offsets for loading new pages
teams = settings.teams

#Give the username and password info
#You may end up bypassing this and just typing in things yourself,
#Yahoo has a lot of login options and they change based on how many times
#You have logged in
def login(driver):
    driver.get("https://login.yahoo.com/")

    username = driver.find_element_by_name('username')
    username.send_keys(settings.YAHOO_USERNAME + '\n')

    time.sleep(LOGIN_TIME)

#Get information from the currently displayed week's games    
def getInfo(bs, week, teams):
    #The locations of each team in the league changes each week.
    #Find each team's location this week.
    baseref = 'https://football.fantasysports.yahoo.com/f1/' + str(settings.YAHOO_LEAGUEID) + '/'
    names = [None]*teams
    ordNames =[None]*teams
    index = 0
    #Find all the listed teams on the page in order
    for a in bs.findAll('a',href=True, attrs={'class':'F-link'}):
        for i in range(1,teams+1):
            ref = a.get('href')
            j = i
            if(i == 9):
                j = 12
            #print(ref)
            #print(baseref + str(j))
            if(ref == baseref + str(j)):
                names[i-1] = a.text 
                ordNames[index] = a.text
                index += 1
    #Find the scores for each team this week
    scores = [None]*teams
    #Write the info from the yahoo page out line by line
    with open("output1.html", "w", encoding='utf-8') as file:
        file.write(str(bs))
    with open ("output1.html", "r", encoding='utf-8') as myfile:
        data=myfile.readlines()
    #Search the line by line info for each team's score
    index = 0
    for i in range(0, len(data)):
        tempstr = str(data[i])
        #Find all numbers in the score box 'i', then store the score of the 'i'th listed team for this week
        #in the location corresponding to the appropirate team when the random matchup dependent team ordering
        #is unscrambled
        if(tempstr.count("Fz-lg Ptop-lg Phone") > 0 or tempstr.count("Fz-lg Fw-b Ptop") > 0):
            num = re.findall("\d+\.\d+", tempstr)
            loc = names.index(ordNames[index])
            score = num[0]
            scores[loc] = float(score)
            index += 1
    
    #Now find out which team each team played this week
    index = 0
    Look = False
    Team1 = False
    tempName = ''
    OppoOrder = [None]*teams
    #You can click on each team, so search through the links
    possible_links = bs.find_all('a')
    for link in possible_links:
        if (link.has_attr('href')):
            ref = link.attrs['href']
            #Check that the link text is one of your teamnames
            if(Look == True and link.text != tempName and link.text in names):
                #The links appear in the order team A, then team A's opponent.
                #Use the order team names appear to determine who played who
                if(Team1 == True):
                    OppoOrder[index] = link.text
                    index = index + 1
                    Look = False
                    Team1 = False
                else:
                    OppoOrder[index] = link.text
                    tempName = link.text
                    Team1 = True
                    index = index + 1
            #Only start looking at teams after seeing the "View Matchup" point in the page
            #To get rid of "team of the week" type things
            if(link.text == "View Matchup"):
                Look = True
    SortOppo = [None]*teams
    for i in range(0, teams//2):
        t1 = OppoOrder[2*i]
        t2 = OppoOrder[2*i + 1]
        SortOppo[names.index(t2)] = t1
        SortOppo[names.index(t1)] = t2
    
    #Write output, a list of the week, team A, the opponent of team A, and team A's score
    #For each week and team
    m = 4
    allList = [[None] * m for i in range(teams)]
    for i in range(0, teams):
        allList[i][0] = week
        allList[i][1] = names[i]
        allList[i][2] = SortOppo[i]
        allList[i][3] = scores[i]
        
    return allList

#Get information from the currently displayed week's games    
def liveInfo(bs, week, teams):
    #The locations of each team in the league changes each week.
    #Find each team's location this week.
    baseref = 'https://football.fantasysports.yahoo.com/f1/' + str(settings.YAHOO_LEAGUEID) + '/'
    names = [None]*teams
    ordNames =[None]*teams
    index = 0
    #Find all the listed teams on the page in order
    for a in bs.findAll('a',href=True, attrs={'class':'F-link'}):
        for i in range(1,teams+1):
            ref = a.get('href')
            j = i
            if(i == 9):
                j = 12
            #print(ref)
            #print(baseref + str(j))
            if(ref == baseref + str(j)):
                names[i-1] = a.text 
                ordNames[index] = a.text
                index += 1
    #Find the scores for each team this week
    scores = [None]*teams
    #Write the info from the yahoo page out line by line
    with open("output1.html", "w", encoding='utf-8') as file:
        file.write(str(bs))
    with open ("output1.html", "r", encoding='utf-8') as myfile:
        data=myfile.readlines()
    #Search the line by line info for each team's score
    index = 0
    for i in range(0, len(data)):
        tempstr = str(data[i])
        #Find all numbers in the score box 'i', then store the score of the 'i'th listed team for this week
        #in the location corresponding to the appropirate team when the random matchup dependent team ordering
        #is unscrambled
        if(tempstr.count("F-shade Italic F-positive") > 0 or tempstr.count("F-shade Italic F-negative") > 0):
            num = re.findall("\d+\.\d+", tempstr)
            #print(num)
            loc = names.index(ordNames[index])
            score = num[1]
            scores[loc] = float(score)
            index += 1
    #Now find out which team each team played this week
    index = 0
    Look = False
    Team1 = False
    tempName = ''
    OppoOrder = [None]*teams
    #You can click on each team, so search through the links
    possible_links = bs.find_all('a')
    for link in possible_links:
        if (link.has_attr('href')):
            ref = link.attrs['href']
            #Check that the link text is one of your teamnames
            if(Look == True and link.text != tempName and link.text in names):
                #The links appear in the order team A, then team A's opponent.
                #Use the order team names appear to determine who played who
                if(Team1 == True):
                    OppoOrder[index] = link.text
                    index = index + 1
                    Look = False
                    Team1 = False
                else:
                    OppoOrder[index] = link.text
                    tempName = link.text
                    Team1 = True
                    index = index + 1
            #Only start looking at teams after seeing the "View Matchup" point in the page
            #To get rid of "team of the week" type things
            if(link.text == "View Matchup"):
                Look = True
    SortOppo = [None]*teams
    for i in range(0, teams//2):
        t1 = OppoOrder[2*i]
        t2 = OppoOrder[2*i + 1]
        SortOppo[names.index(t2)] = t1
        SortOppo[names.index(t1)] = t2
    
    #Write output, a list of the week, team A, the opponent of team A, and team A's score
    #For each week and team
    m = 4
    allList = [[None] * m for i in range(teams)]
    for i in range(0, teams):
        allList[i][0] = week
        allList[i][1] = names[i]
        allList[i][2] = SortOppo[i]
        allList[i][3] = scores[i]
    return allList

options = webdriver.ChromeOptions()
options.binary_location = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
#All the arguments added for chromium to work on selenium
options.add_argument("--no-sandbox") #This make Chromium reachable
options.add_argument("--no-default-browser-check") #Overrides default choices
options.add_argument("--no-first-run")
options.add_argument("--disable-default-apps") 
driver = webdriver.Chrome(chrome_options=options)  # Optional argument, if not specified will search path.

#Log in to your league yahoo account
print("logging in")
login(driver)
#Load the main league page
print("loading league")
IDnum = settings.YAHOO_LEAGUEID
ad1 = "https://football.fantasysports.yahoo.com/f1/" + str(IDnum)
driver.get(ad1)
time.sleep(SLEEP_SECONDS)
print("data?")
#Find the button to click back week by week
#python_button = driver.find_elements_by_xpath("/html/body/div[1]/div[2]/div[2]/div[2]/div/div/div[2]/div[2]/section[1]/div/div/div[3]/section[2]/header/div/span/a[1]/span")[0]
python_button = driver.find_elements_by_xpath("/html/body/div[1]/div[2]/div[2]/div[2]/div/div/div[2]/div[2]/section[1]/div/div/div[3]/section[2]/header/div/span/a[1]/span")[0]
#If the game showing is a game that has been played, don't click away yet
SP = settings.ShowingPlayed
print(SP)
if(not SP):
    python_button.click()
    time.sleep(SLEEP_SECONDS)
#Get the page info from the most recently played week
content = driver.page_source
bs = BeautifulSoup(content, features="html.parser")

#Get the page info for each week, then click to the previous week until hitting week 1
startWeek = settings.SW
print(startWeek)
Writer = [None]*0
live = settings.liveNow
for i in range(0, startWeek):
    #Process the page info to get week, team A, opponent, score of team A
    #For each team
    if(i == 0 and live == True):
        allL = liveInfo(bs, startWeek-i, teams)
    else:
        allL = getInfo(bs, startWeek-i, teams)
    python_button.click()
    time.sleep(SLEEP_SECONDS)
    if(i == 0):
        Writer = allL
    else:
        Writer = np.concatenate((Writer, allL), axis = 0)
    content = driver.page_source
    bs = BeautifulSoup(content, features="html.parser")
#Write the data for each week. Saves time when simulating seasons because you don't have to reload the pages
with open('oldGames.txt', 'w') as file:
    file.writelines('\t'.join(str(j) for j in i) + '\n' for i in Writer)
    
#Go back to the current week to get the future game info
driver.get(ad1)
time.sleep(SLEEP_SECONDS)
#Now click forward if the initially displayed game has already been played
python_button = driver.find_elements_by_xpath("/html/body/div[1]/div[2]/div[2]/div[2]/div/div/div[2]/div[2]/section[1]/div/div/div[3]/section[2]/header/div/span/a[3]/span")[0]
#python_button = driver.find_elements_by_xpath("/html/body/div[1]/div[2]/div[2]/div[2]/div/div/div[2]/div[2]/section[1]/div/div/div[3]/section[6]/header/div/span/a[3]/span")[0]
if(SP):
    python_button.click()
    time.sleep(SLEEP_SECONDS)
    print('pre-clicked')
content = driver.page_source
bs = BeautifulSoup(content, features="html.parser")
gamesLeft = END_WEEK-4-startWeek

#Get the page info for each week, then click to the next week until hitting week 13
Writer = [None]*0
for i in range(0, gamesLeft):
    allL = getInfo(bs, startWeek+i + 1, teams)
    python_button.click()
    time.sleep(SLEEP_SECONDS)
    if(i == 0):
        Writer = allL
    else:
        Writer = np.concatenate((allL, Writer), axis = 0)
    content = driver.page_source
    bs = BeautifulSoup(content, features="html.parser")

print(Writer)
#Write the data for each future week in a second file.
with open('futureGames.txt', 'w') as file:
    file.writelines('\t'.join(str(j) for j in i) + '\n' for i in Writer)

driver.quit()
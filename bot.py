import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

client = commands.Bot(command_prefix='$')
#token = 'discord-token' //I used a discord bot token
#PATH ='path to chromedriver.exe'
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")


def check_line_no(line):
    line = line.upper()
    ok = 1
    if line[0] != 'N' and line[-1] != 'B':
        try:
            test = int(line)
            if (test < 0):
                raise
        except:
            ok = 0
    elif line[0] == 'N':
        try:
            test = int(line[1:])
            if (test < 0):
                raise
        except:
            ok = 0
    elif line[-1] == 'B':
        try:
            test = int(line[:-1])
            if (test < 0):
                raise
        except:
            ok = 0
    return line, ok


def get_buttons(url):
    page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, "html.parser")
    buttons = soup.findAll('a', {'id': "A_1"})
    return buttons


def get_list_of_stations(buttons, line, checkTur, checkRetur):
    message = 'Link: '
    ok = 0
    for button in buttons:
        a = button.getText().strip()
        if a == line:
            message += button['href'] + '\n```'
            newUrl = button['href']
            driver = webdriver.Chrome(PATH, options=chrome_options)
            driver.get(newUrl)
            try:
                scheduleButton = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'buttonShowTimetable')))
                scheduleButton.click()
            except:
                pass
            try:
                orarBody = driver.find_element(By.CLASS_NAME, 'orarBody')
                if checkTur == True:
                    turDirection = orarBody.find_element(By.ID, 'turDirectionName')
                    tur = turDirection.text
                if checkRetur == True:
                    returDirection = orarBody.find_element(By.ID, 'returDirectionName')
                    retur = returDirection.text
                turReturButtons = driver.find_elements(By.CLASS_NAME, 'subtitleButton')
                for trButton in turReturButtons:
                    if checkTur == True and trButton.text == "Tur (directia):":
                        message += f'I. Heading towards {tur}\n\n'
                        trButton.click()
                        listTurHeader = driver.find_element(By.ID, 'listaStatiiTur')
                        list = []
                        listTur = listTurHeader.find_elements(By.CLASS_NAME, 'itemStopOrar')
                        for elem in listTur:
                            stopName = elem.find_element(By.CLASS_NAME, 'itemContainerOrar') \
                                .find_element(By.CLASS_NAME, 'descriptionContOrar') \
                                .find_element(By.CLASS_NAME, 'nameDivOrar').text
                            list = list + [stopName]
                        i = 1
                        for item in list:
                            message += f"{i}. {item}\n"
                            i = i + 1
                        message += "\n\n"
                    elif checkRetur == True and trButton.text == "Retur (directia):":
                        message += f'II. Heading towards {retur}\n\n'
                        trButton.click()
                        listReturHeader = driver.find_element(By.ID, 'listaStatiiRetur')
                        list = []
                        listRetur = listReturHeader.find_elements(By.CLASS_NAME, 'itemStopOrar')
                        for elem in listRetur:
                            stopName = elem.find_element(By.CLASS_NAME, 'itemContainerOrar') \
                                .find_element(By.CLASS_NAME, 'descriptionContOrar') \
                                .find_element(By.CLASS_NAME, 'nameDivOrar').text
                            list = list + [stopName]
                        i = 1
                        for item in list:
                            message += f"{i}. {item}\n"
                            i = i + 1
                message += '```'
            except:
                pass
            driver.close()
            ok = 1
            break
    if (ok == 0):
        message = "This line does not exist"
    return message


def get_schedule(number, buttons, line, checkTur, checkRetur):
    message = 'Link: '
    ok = 0
    for button in buttons:
        a = button.getText().strip()
        if a == line:
            message += button['href'] + '\n```'
            newUrl = button['href']
            driver = webdriver.Chrome(PATH, options=chrome_options)
            driver.get(newUrl)
            try:
                scheduleButton = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'buttonShowTimetable')))
                scheduleButton.click()
            except:
                pass
            try:
                orarBody = driver.find_element(By.CLASS_NAME, 'orarBody')
                if checkTur == True:
                    turDirection = orarBody.find_element(By.ID, 'turDirectionName')
                    tur = turDirection.text
                if checkRetur == True:
                    returDirection = orarBody.find_element(By.ID, 'turDirectionName')
                    retur = returDirection.text
                turReturButtons = driver.find_elements(By.CLASS_NAME, 'subtitleButton')
                for trButton in turReturButtons:
                    if checkTur == True and trButton.text == "Tur (directia):":
                        trButton.click()
                        listTurHeader = driver.find_element(By.ID, 'listaStatiiTur')
                        listTur = listTurHeader.find_elements(By.CLASS_NAME, 'itemStopOrar')
                        if number > len(listTur):
                            message = "The number given as the third parameter is higher than the number of stops"
                            raise
                        elem = listTur[number - 1]
                        container = elem.find_element(By.CLASS_NAME, 'itemContainerOrar')
                        stopName = container.find_element(By.CLASS_NAME, 'descriptionContOrar') \
                            .find_element(By.CLASS_NAME, 'nameDivOrar').text

                        WebDriverWait(container, 20).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, 'stb-down'))).click()
                        time.sleep(1)
                        schedule = elem.find_element(By.CLASS_NAME, 'orarDivOrar') \
                            .find_element(By.CLASS_NAME, 'timetable') \
                            .find_element(By.TAG_NAME, 'tbody')
                        scheduleItems = schedule.find_elements(By.TAG_NAME, 'tr')
                        message += f'Heading towards {tur} \nStop name: {stopName}\n\nOra Minute\n'
                        for item in scheduleItems[1:]:
                            numbers = item.find_elements(By.TAG_NAME, 'td')
                            message += numbers[0].text
                            message += '  '
                            message += numbers[1].text
                            message += '\n'
                        message += '```'
                    elif checkRetur == True and trButton.text == "Retur (directia):":
                        trButton.click()
                        listReturHeader = driver.find_element(By.ID, 'listaStatiiRetur')
                        listRetur = listReturHeader.find_elements(By.CLASS_NAME, 'itemStopOrar')
                        if number > len(listRetur):
                            message = "The number given as the third parameter is higher than the number of stops"
                            raise
                        elem = listRetur[number - 1]
                        container = elem.find_element(By.CLASS_NAME, 'itemContainerOrar')
                        stopName = container.find_element(By.CLASS_NAME, 'descriptionContOrar') \
                            .find_element(By.CLASS_NAME, 'nameDivOrar').text
                        WebDriverWait(container, 20).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, 'stb-down'))).click()
                        time.sleep(1)
                        schedule = elem.find_element(By.CLASS_NAME, 'orarDivOrar') \
                            .find_element(By.CLASS_NAME, 'timetable') \
                            .find_element(By.TAG_NAME, 'tbody')
                        scheduleItems = schedule.find_elements(By.TAG_NAME, 'tr')
                        message += f'Heading towards {retur} \nStop name: {stopName}\n\nOra Minute\n'
                        for item in scheduleItems[1:]:
                            numbers = item.find_elements(By.TAG_NAME, 'td')
                            message += numbers[0].text
                            message += '  '
                            message += numbers[1].text
                            message += '\n'
                        message += '```'
            except:
                pass
            driver.close()
            ok = 1
            break
    if ok == 0:
        message = "This line does not exist"
    return message


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.command()
async def stb(ctx, *args):
    url = "https://www.stbsa.ro/index"

    if len(args) == 0:
        await ctx.send("```You want to find out about a stb route. Formulate your command like this:\n"
                       "-> $stb line_number heading_direction stop_number in order to see the schedule for a given "
                       "line, in a given direction, for a given stop.\n "
                       "-> $stb line_number for further instructions regarding the heading direction and stop\n"
                       "-> $stb line_number heading_direction for further instructions regarding the stop\n"
                       "Example: $stb 96 I 10\n"
                       "The heading direction is either I or II\n"
                       "The stop number is assigned based on the order of stops in a heading direction```")
    elif len(args) == 1:
        try:
            line, check = check_line_no(args[0])
            if check == False:
                raise
            buttons = get_buttons(url)
            message = get_list_of_stations(buttons, line, True, True)
            await ctx.send(message)
        except:
            await ctx.send("Invalid line number. It has to be a positive integer, or a positive integer beginning "
                           "with N or ending with B.")
    elif len(args) == 2:
        if args[1] == 'I':
            try:
                line, check = check_line_no(args[0])
                if check == False:
                    raise
                buttons = get_buttons(url)
                message = get_list_of_stations(buttons, line, True, False)
                await ctx.send(message)
            except:
                await ctx.send("Invalid line number. It has to be a positive integer.")
        elif args[1] == 'II':
            try:
                line, check = check_line_no(args[0])
                if check == False:
                    raise
                buttons = get_buttons(url)
                message = get_list_of_stations(buttons, line, False, True)
                await ctx.send(message)
            except:
                await ctx.send("Invalid line number. It has to be a positive integer.")
        else:
            await ctx.send("Unknown heading direction... Options are I and II")
    elif (len(args) == 3):
        try:
            number = int(args[2])
            if number < 1:
                raise
            if args[1] == 'I':
                try:
                    line, check = check_line_no(args[0])
                    if check == False:
                        raise
                    buttons = get_buttons(url)
                    message = get_schedule(number, buttons, line, True, False)
                    await ctx.send(message)
                except:
                    await ctx.send("Invalid line number. It has to be a positive integer.")
            elif args[1] == 'II':
                try:
                    line, check = check_line_no(args[0])
                    if check == False:
                        raise
                    buttons = get_buttons(url)
                    message = get_schedule(number, buttons, line, False, True)
                    await ctx.send(message)
                except:
                    await ctx.send("Invalid line number. It has to be a positive integer.")
            else:
                await ctx.send("Unknown heading direction... Options are I and II")
        except:
            await ctx.send("The third parameter must be an integer greater than 0")
    else:
        await ctx.send("Incorrect number of parameters")


client.run(token)

import flask
from flask import request, jsonify
import json 
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import time
from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
import asyncio
from threading import Thread
import pyppeteer
import nest_asyncio


nest_asyncio.apply()


async def if_open(classnum):
    # session = AsyncHTMLSession()
    ua = UserAgent()
    url = f'https://webapp4.asu.edu/catalog/classlist?t=2227&k={classnum}&e=all'
    print(url)
    with AsyncHTMLSession() as s:
        browser = await pyppeteer.launch({ 
            'ignoreHTTPSErrors':True, 
            'headless':True, 
            'handleSIGINT':False, 
            'handleSIGTERM':False, 
            'handleSIGHUP':False
        })
        s._browser = browser
        r = await s.get(url,headers={
            "User-Agent": ua.random, "Connection": "keep-alive"})			
        await r.html.arender()
        soup = BeautifulSoup(r.html.raw_html, "html.parser")
        availableSeatsColumnValue = soup.find_all('td', class_='availableSeatsColumnValue')
        classNbrColumnValue = soup.find_all('td', class_='classNbrColumnValue')
        seatsOpen = []
        classNumber = []
        for i in availableSeatsColumnValue:
            seatsOpen.append(i.text.strip().replace('\n','').replace('of',' of '))
        for i in classNbrColumnValue:
            classNumber.append(i.text.strip())
        for i in range(len(seatsOpen)):
            print(seatsOpen[i])
            print(classNumber[i])
            print(seatsOpen[i].partition(' of ')[0])
            return int(seatsOpen[i].partition(' of ')[0])

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/api/v1/numSeats', methods=['GET'])
async def numSeats():
    classnum = request.args.get('classnum')
    if classnum == None:
        return jsonify({'error': 'No class number provided'})
    else:
        # openSeats = await if_open(classnum)
        loop = asyncio.get_event_loop()
        openSeats = loop.run_until_complete(if_open(classnum))
        # print(openSeats)
        if openSeats > 0:
            return jsonify({'classnum': classnum, 'open': True, 'seats': openSeats})
        else:
            return jsonify({'classnum': classnum, 'open': False})

app.run()





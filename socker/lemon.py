#import pandas as pd
import numpy as np
import requests
import re
from collections import defaultdict
import os
import json
import threading
import logging
import joblib
import random
import sys
import time
import hashlib
import urllib3
import datetime
import shutil
#from lxml import etree
		
def get_league_html():
    
    league_info_url = 'http://zq.win007.com/jsData/infoHeader.js'
    #league_info_text = requests.get(league_info_url,headers=header,proxies = proxies,timeout=5).text
    league_info_text = ''
    while league_info_text == '':
        try:
            league_info_text = requests.get(league_info_url,headers=header,timeout=5).text
        except:
            logging.warning('InfoHeader Error: - - - - Try to Capture InfoHeader Again - - - - ')
            time.sleep(5)
            continue
    pattern = re.compile('\d+,\w+,\d,\d,[\d+-?\d+?]+')
    league_info = pattern.findall(league_info_text)
    league_info = [ls.split(',') for ls in league_info]
    print('Total Leagues: {}'.format(len(league_info)))
    #print('League info sample: {}'.format(league_info[0]))
    
    league_htmls = defaultdict(list)
    for league in league_info:
        #'http://zq.win007.com/cn/SubLeague/37.html'
        (league_id,league_name,league_type,league_rank), seasons = league[:4], league[4:]
        #htmls = []
        #for season in seasons:
        #    league_html = ''
        #    if league_type == '1':
        #        if league_rank == '0':  
        #            league_html = 'http://zq.win007.com/cn'+'/League/'+season+'/'+league_id+'.html'
        #        else:
        #            league_html = 'http://zq.win007.com/cn'+'/SubLeague/'+season+'/'+league_id+'.html'
        #    elif league_type == '2':
        #            league_html = 'http://zq.win007.com/cn'+'/CupMatch/'+season+'/'+league_id+'.html'
        #    htmls.append(league_html)
        if league_type == '1':
            if league_rank == '0':  
                league_html = 'http://zq.win007.com/cn'+'/League/'+league_id+'.html'
            else:
                league_html = 'http://zq.win007.com/cn'+'/SubLeague/'+league_id+'.html'
        elif league_type == '2':
                league_html = 'http://zq.win007.com/cn'+'/CupMatch/'+league_id+'.html'
        league_htmls[league_name].append(int(league_type+league_rank))
        league_htmls[league_name].append(league_html)
        league_htmls[league_name] += list(seasons)
    return league_htmls
	
def tree():
    return defaultdict(tree)
	
def get_league_season_js(league_htmls:dict,leagues,mode=1,season_num=10):
    #pattern = re.compile('/jsData/matchResult/2019-2020/s36.js?version=2020010910')
    pattern = re.compile('/jsData/matchResult/\d+-?\d+?(/\w\d+_?\d*\.js\?version=\d+)')
    leagues_seasons_js = defaultdict(list)
    #index_tree = tree()
    if isinstance(leagues,str):
		
        htmls_len = len(league_htmls[leagues])-2
        seasons = []
        
        if isinstance(season_num,int):
            if season_num >= htmls_len: season_num = htmls_len
            elif season_num < 0: season_num = 1        
            if mode == 1:           #1: Continous Capturing
                seasons = league_htmls[leagues][2:2+season_num]            
            elif mode == 0:         #0: Discrete Capturing
                seasons = [league_htmls[leagues][2+season_num-1]]
        elif isinstance(season_num,list):
            season_num = sorted(season_num)
            if mode == 1:
                if season_num[-1] >= htmls_len: 
                    season_num = htmls_len
                    seasons = league_htmls[leagues][2+season_num[0]-1:2+htmls_len]
                else:
                    seasons = league_htmls[leagues][2+season_num[0]-1:2+season_num[-1]]
            elif mode == 0:
                for num in season_num:
                    if num < 0: num = 1
                    elif num >= htmls_len: season_num.remove(num)
                    seasons.append(league_htmls[leagues][2+num-1])
           
        print('\rLeague: {} - Season: {}'.format(leagues,seasons),end='')    
        print()
        html = league_htmls[leagues][1]
        print('html: {}'.format(html))
        js_version = ''
        while js_version == '':
            try:
                html_content = requests.get(html,headers=header,timeout=5).text
                js_version = pattern.findall(html_content)[0]
                if len(html_content) > 9: break
            except:
                logging.warning('JSVersion Error: - - - {} - - - - Try to Visit {} Again - - - - '.format(html_content,html))
                time.sleep(5)
                continue                
        for season in seasons:
            js_url = 'http://zq.win007.com/jsData/matchResult/'+season+js_version
            leagues_seasons_js[leagues].append(js_url)
            #index_tree[leagues][season]
    elif isinstance(leagues,list):
        for i,league in enumerate(leagues):
            htmls_len = len(league_htmls[league])-2
            seasons = []
            
            if isinstance(season_num,int):
                if season_num >= htmls_len: season_num = htmls_len
                elif season_num < 0: season_num = 1        
                if mode == 1:           #1: Continous Capturing
                    seasons = league_htmls[league][2:2+season_num]            
                elif mode == 0:         #0: Discrete Capturing
                    seasons = [league_htmls[league][2+season_num-1]]
            elif isinstance(season_num,list):
                season_num = sorted(season_num)
                if mode == 1:
                    if season_num[-1] >= htmls_len: 
                        season_num = htmls_len
                        seasons = league_htmls[league][2+season_num[0]-1:2+htmls_len]
                    else:
                        seasons = league_htmls[league][2+season_num[0]-1:2+season_num[-1]]
                elif mode == 0:
                    for num in season_num:
                        if num < 0: num = 1
                        elif num >= htmls_len: season_num.remove(num)
                        seasons.append(league_htmls[league][2+num-1])           
                    
            print('\rLeague: {}/{} - {} - Season: {}'.format(i+1,len(leagues),league,seasons),end='')
            html = league_htmls[league][1]
            js_version = ''
            while js_version == '':
                try:
                    html_content = requests.get(html,headers=header,timeout=5).text
                    js_version = pattern.findall(html_content)[0]
                    if len(html_content) > 9: break
                except:
                    logging.warning('JSVersion Error: - - - {} - - - - Try to Visit {} Again - - - - '.format(html_content,html))
                    time.sleep(5)
                    continue
            for season in seasons:
                js_url = 'http://zq.win007.com/jsData/matchResult/'+season+js_version
                leagues_seasons_js[league].append(js_url)
                #index_tree[league][season]
        print()
    #return leagues_seasons_js,index_tree
    return leagues_seasons_js
	
def get_teams(season_round_content):
    #19,'��ɭ��','����ū','Arsenal','����ū','images/2013121220126.png',0
    pattern = re.compile('(\d+),\'(\w+)\',\'\w+\',\'.+?\',\'\w+\',\'images/\d+.\w+\',\d')
    team_info = pattern.findall(season_round_content)
    team_info = {team_id:team_name for team_id,team_name in team_info}
    #team_info = [info.split(',') for info in team_info]
    return team_info
	
def get_round_info(season_round_content):
    #1720912,36,-1,'2019-08-10 03:00',25,34,'4-1','4-0','2','Ӣ��1',2.25,1,'3/3.5','1/1.5',1,1,1,1,0,0,'','2','ENG LCH-1'
    pattern = re.compile('\[(\d+),\d+,(-?\d),(.+?),(\d+),(\d+),(.+?),.+?,(.+?),(.+?),.*?,.*?,.+?,.+?,\d,\d,\d,\d,\d,\d,.*?,.+?,.+?\]')
    round_info = pattern.findall(season_round_content)
    return round_info
	
def get_match_info(round_info:list,league,season,teams,phase=-1):
#def get_match_info(round_info:list,teams,phase=-1):
    pattern = re.compile('"\d+\|(\d+)\|.+?\|(.+?)\|(\d)\|\d"')
    match_info = []
    #round_len = len(teams)/2
    N = 0
    for i,info in enumerate(round_info):
        match_id,match_state,match_date,r1,r2,score,host_rank,guest_rank = info
        #http://1x2d.win007.com/1721891.js
        #round_matches = len(teams)/2
        #Round = int(i//round_matches)+1
        #match = r1+'-'+r2        
        if int(match_state) == phase:
            if phase == 0 and days_interval(match_date) > 5: break
            url = 'http://1x2d.win007.com/'+match_id+'.js'
            #js_text = ''
            result = []
            while not result:
                try:
                    js_text = requests.get(url,headers=header,timeout=5).text
                    result = pattern.findall(js_text)
                    if len(js_text) > 9: break
                except:
                    logging.warning('MatchInfo Error:- - - Try to Visit Match: {}-{} JS: {} Again - - -'.format(teams[r1],teams[r2],match_id))
                    time.sleep(3)
                    continue
            if result:
                ids_companys = [(r[0],r[1].split('|')[-1]) for r in result if int(r[2]) == 1]     
                match_info.append([teams[r1],teams[r2],ids_companys,match_date,score_2_310(score,match_state)])
                N = N + 1
                #print('\rMatch: {}-{} JS: {} State: {} Total: {}/{}'.format(teams[r1],teams[r2],match_id,match_state,N,len(round_info)),end='')
                print('\r{}-{}: {}/{} State: {}'.format(league,season,N,len(round_info),'END' if phase==-1 else 'NEW'),end='')
            else: 
                match_info.append('')
        else:
            match_info.append('')
    print()
    return match_info

def days_interval(match_date):
    nowaday = datetime.date.isoformat(datetime.date.today())
    match_date = match_date.strip('\'')
    date1=datetime.datetime.strptime(nowaday[0:10],"%Y-%m-%d")
    date2=datetime.datetime.strptime(match_date[0:10],"%Y-%m-%d")
    days=(date2-date1).days
    return days

def score_2_310(score,match_state):
    if int(match_state) == -1:
        left_score, right_score = [int(s) for s in score.strip('\'').split('-')]
        #left_score, right_score = int(left_score), int(right_score) 
        if left_score > right_score:
            return 2
        elif left_score == right_score:
            return 1
        else:
            return 0
    else:
        return ''
        
def get_odds(odds_text):
    entry = re.compile('<title>.+VS.+</title>')
    pageRight = bool(entry.search(odds_text))
    odds = []
    if pageRight:
        #pattern = re.compile('<font\scolor=\w*>(\d\d?.\d\d?)</font>')
        pattern = re.compile('color=\w*>(\d+\.\d+).+?color=\w*>(\d+\.\d+).+?color=\w*>(\d+\.\d+).+?&nbsp;\s(\d+-\d+\s\d+\:\d+)')
        odd_ps = pattern.findall(odds_text)
        #print(len(odd_ps))
        odds = odds_process(odd_ps)
    return np.array(odds),pageRight 
	
def odds_process(odd_ps):
    odds = []
    l = len(odd_ps)
    #for i in range(l//3-1,-1,-1):
    #    odds.append([float(odd_ps[i*3]),float(odd_ps[i*3+1]),float(odd_ps[i*3+2])])  
    for i in range(l):
        odds.append([float(odd_ps[l-1-i][0]),float(odd_ps[l-1-i][1]),float(odd_ps[l-1-i][2]),odd_ps[l-1-i][3]])
    return odds    
	
def odds_factory(league,season,Round,id,r1,r2,company):
    param = {
        'id' : id,
        'r1' : r1,
        'r2' : r2,
        'Company': company
        
    }
    odd_url = 'http://op1.win007.com/OddsHistory.aspx'
    odds = np.array([])
    odds_text = ''
    delay = 5
    reroll = False
    global flow_num
    global task_num
    global flow_time
    while odds.shape[0] == 0:
        try:
            #odds_text = requests.get(odd_url,params=param,headers=header,timeout=5).text
            odds_text = requests.get(odd_url,params=param,headers=header).text
            #rsp = requests.get(odd_url,params=param,headers=header,timeout=5)
            #if len(odds_text) < 20:
            #    time.sleep(delay)
            #    odds_text = requests.get(odd_url, headers=header_x, proxies=proxy, verify=False, allow_redirects=False,timeout=10).text
            #    reroll = True
            if len(odds_text) < 10:
                time.sleep(delay)
                #odds_text = requests.get(odd_url, params=param, headers=header, proxies=proxy, timeout=5).text
                odds_text = requests.get(odd_url, params=param, headers=header, proxies=proxy).text
                reroll = True
            #rsp = requests.get(odd_url, headers=header, proxies=proxy, timeout=10)
            #rsp_code = rsp.status_code
            #odds_text = rsp.text           
            #print('\r* Task Processed: {}/{} * LINK_INFO:- - - - -{}-Fetch: {}-{}-{}-{}-{}-{}'.format(task_num,flows,len(odds_text) if len(odds_text) > 20 else odds_text,league,season,Round,r1,r2,company),end='')
            print('\r* Task Processed: {}/{} Time: {} * LINK_INFO:- - - - -{}-Fetch: {}-{}-{}-{}-{}-{}'.format(task_num,flows,flow_time,len(odds_text) if len(odds_text) > 20 else odds_text,league,season,Round,r1,r2,company),end='')
            #print('\r* Task Processed: {}/{} * LINK_INFO:- - - - -{}-Fetch: {}-{}-{}-{}-{}-{}'.format(task_num,flows,rsp_code,league,season,Round,r1,r2,company),end='')
            #print('\r* Task Processed: {}/{} * LINK_INFO:- - - - -{}-Fetch: {}-{}-{}-{}-{}-{}'.format(flow_num,flows,len(odds_text) if len(odds_text) > 20 else odds_text,league,season,Round,r1,r2,company),end='')
            #print('\r* Task Processed: {}/{} * LINK_INFO:- - - - -{}-Fetch: {}-{}-{}-{}-{}-{}'.format(task_num,flow_num,link_info,league,season,Round,r1,r2,company),end='')
            odds, pageRight = get_odds(odds_text)
            if pageRight: break
            #link_file = 'link_' + str(len(odds_text)) + '_' + str(rsp_code) + '.html'
            #if not os.path.isfile(link_file) and odds.shape[0] == 0:
            #    with open(link_file,'w',encoding='UTF-8') as f:
            #        f.writelines(odds_text)
            #if len(odds_text) > 200 or reroll: break
            time.sleep(delay)
        except:
            #print('\rCompanyOdds Error:- - - {} - - - Try to Capture: {}-{}-{}-{}-{}-{} Odds Again - - -'.format(odds_text,league,season,Round,r1,r2,company),end='')
            #print('\r* Task Processed: {}/{} * CompanyOdds Error:-{}-Fetch: {}-{}-{}-{}-{}-{}'.format(task_num,flows,odds_text if len(odds_text) < 20 else len(odds_text),league,season,Round,r1,r2,company),end='')
            #rsp_code = rsp.status_code
            #print('\r* Task Processed: {}/{} * CompanyOdds Error:-{}-Fetch: {}-{}-{}-{}-{}-{}'.format(task_num,flows,rsp_code,league,season,Round,r1,r2,company),end='')
            print('\r* Task Processed: {}/{} Time: {} * CompanyOdds Error:-{}-Fetch: {}-{}-{}-{}-{}-{}'.format(task_num,flow_num,flow_time,odds_text if len(odds_text) < 20 else len(odds_text),league,season,Round,r1,r2,company),end='')
            #print('\r* Task Processed: {}/{} * CompanyOdds Error:-{}-Fetch: {}-{}-{}-{}-{}-{}'.format(flow_num,flows,odds_text if len(odds_text) < 20 else len(odds_text),league,season,Round,r1,r2,company),end='')
            #print('\r* Task Processed: {}/{} * CompanyOdds Error:-{}-Fetch: {}-{}-{}-{}-{}-{}'.format(flow_num,flows,odds_text if len(odds_text) < 20 else len(odds_text),league,season,Round,r1,r2,company),end='')
            #print('\r**** Task Processed: {}/{} **** CompanyOdds Error:- {} -'.format(task_num,flows,odds_text if len(odds_text) < 20 else len(odds_text)),end='')
            #logging.warning('Text Content -- {}'.format(odds_text if len(odds_text) < 40 else len(odds_text)))
            
            #delay += 10
            #random_time = random.randint(3,10)
            time.sleep(delay)
            continue
             
            
    return odds,len(odds_text) if len(odds_text) > 20 else odds_text
	
def catch_datasets(leagues,season_num,mode=1,phase=-1):
    #Dev_sets
    league_htmls = get_league_html()
    #leagues_seasons_js, index_tree = get_league_season_js(league_htmls,leagues,season_num) 
    leagues_seasons_js = get_league_season_js(league_htmls,leagues,mode=mode,season_num=season_num) 
    
    def clock(start):
        global flow_time
        global ONFLOW
        while ONFLOW:       
            now = time.time()       
            runtime = now-start
            runhours = round((runtime)/3600,1)
            runminutes = round((runtime)/60,1)
            if runtime < 60:
                flow_time = str(int(runtime)) + ' s'
            elif runhours >= 1:
                flow_time = str(runhours) + ' h'
            else: 
                flow_time = str(runminutes) + ' m'
                          
    def odds_flow(league,season,Round,match,id,r1,r2,company,company_pkl):
        #odds = np.array([])
        #while odds.shape[0] == 0:
        global task_num
        global flow_num
        global flow_time
        odds,link_info = odds_factory(league,season,Round,id,r1,r2,company)
        lock.acquire()
        #odds,link_info = odds_factory(league,season,Round,id,r1,r2,company)
        if odds.shape[0] != 0: 
            joblib.dump(odds,company_pkl)
            task_num += 1
            #print('\r* Task Processed: {}/{} * LINK_INFO:- - - - -{}-Fetch: {}-{}-{}-{}-{}-{}'.format(task_num,flows,link_info,league,season,Round,r1,r2,company),end='')
        flow_num += 1
        #print('\r* Task Processed: {}/{} *'.format(task_num,flows),end='')
        #print('\r* Task Processed: {}/{} Time: {} * TASK_INFO:- - - - -{}-Fetch: {}-{}-{}-{}-{}-{}'.format(task_num,flows,flow_time,link_info,league,season,Round,r1,r2,company),end='')
        lock.release()
        #index_tree[league][season][Round][match][company] = odds
        #print('\r* Task Processed: {}/{} * LINK_INFO:- - - - -{}-Fetch: {}-{}-{}-{}-{}-{}'.format(task_num,flow_num,link_info,league,season,Round,r1,r2,company),end='')
        #print('\r* Task Processed: {}/{} * LINK_INFO:- - - - -{}-Fetch: {}-{}-{}-{}-{}-{}'.format(task_num,flow_num,link_info,league,season,Round,r1,r2,company),end='')
        
        
    #root = 'predirs'
    root = 'pres'
    if phase == 0:
        if os.path.isdir(root): 
            try:
                shutil.rmtree(root)
            except OSError:
                shutil.rmtree(root)
    odds_threads = []

    for league,js_urls in leagues_seasons_js.items():           
        #if phase == -1:
        #js_threads = []
        for url in js_urls:
            #'http://zq.win007.com/jsData/matchResult/2019-2020/s8.js?version=2020011718'
            season = url.split('/')[5]
            season_round_content = ''
            while season_round_content == '':
                try:
                    season_round_content = requests.get(url,headers=header,timeout=5).text
                except:
                    print('\rSeasonRound Error: - - - Try to Visit {} Again - - -'.format(url),end='')
                    #time.sleep(5)
                    continue
            teams = get_teams(season_round_content)
            round_matches = len(teams)/2
            round_info = get_round_info(season_round_content)
            #match_info = get_match_info(round_info,teams,phase=phase)
            match_info = get_match_info(round_info,league,season,teams,phase=phase)
            #print(round_info)
            #print(match_info)
            if match_info:
                for i,info in enumerate(match_info):
                    if info:
                        r1,r2,ids_companys,match_date,toz = info
                        Round = int(i//round_matches)+1
                        match = r1+'-'+r2
                        match_order = int(i%round_matches)+1
                        #index_tree[league][season][Round][match]['DATE'] = match_date
                        #index_tree[league][season][Round][match]['TOZ'] = toz
                        for j,(id,company) in enumerate(ids_companys):
                            #print('\rLeague: {}  Season: {}  Round: {}  Match: {} - {}/{}  Comapany: {} - {}/{} - - - - {}/{}'.format(league,season,Round,match,match_order,round_matches,company,j+1,len(ids_companys),i+1,len(match_info)),end='')
                            #odds = np.array([])
                            #while odds.shape[0] == 0:
                            #    odds = odds_factory(id,r1,r2,company)
                            #index_tree[league][season][Round][match][company] = odds 
                            #t = threading.Thread(target=odds_flow,args=(league,season,Round,match,id,r1,r2,company))
                            #odds_threads.append(t)              
                            rdy, company_pkl = odds_ready(league,season,Round,match,company,match_date,toz,phase=phase)
                            if rdy:
                            #if company in ['威廉希尔(英国)','立博(英国)','伟德(直布罗陀)'] and rdy:
                                print('\rLeague: {}  Season: {}  Round: {}  Match: {} - {}/{}  Comapany: {} - {}/{} - - - - {}/{}'.format(league,season,Round,match,match_order,round_matches,company,j+1,len(ids_companys),i+1,len(match_info)),end='')
                                t = threading.Thread(target=odds_flow,args=(league,season,Round,match,id,r1,r2,company,company_pkl))
                                odds_threads.append(t)
                            #t.start()
                            #t.join()
                            #time.sleep(1)
        print()
        logging.warning('{} is Finished!'.format(league))
    print('Total {}  flows'.format(len(odds_threads)))
    global flows
    global ONFLOW
    flows = len(odds_threads)
    if odds_threads:
        flow_start = time.time()
        time_flow = threading.Thread(target=clock,args=(flow_start,))
        ONFLOW = True
        time_flow.start()
        for i,t in enumerate(odds_threads):
            t.start()
            #t.join()
            #print('\r{}/{} is starting!!'.format(i+1,flows),end='')
        #print()
        for t in odds_threads:
            t.join()
        #    print('\r{}/{} is joining in!!'.format(i+1,flows),end='')
        #print()
        #print('\r**** Task Processed: {}/{} ****'.format(task_num+1,len(odds_threads)),end='')
    print()
    ONFLOW = False
    logging.warning('**** Odds Capture Is Finished! ****')    
    #return index_tree

def odds_ready(league,season,Round,match,company,match_date,toz,phase=-1):
    root = ''
    if phase == -1:
        #root = 'devdirs'
        root = 'devs'
    elif phase == 0:
        #root = 'predirs'  
        root = 'pres'  
    if not os.path.isdir(root): os.makedirs(root)
    league_path = os.path.join(root,league)
    if not os.path.isdir(league_path): os.makedirs(league_path)
    season_path = os.path.join(league_path,season)
    if not os.path.isdir(season_path): os.makedirs(season_path)
    round_path = os.path.join(season_path,str(Round))
    if not os.path.isdir(round_path): os.makedirs(round_path)
    match_path = os.path.join(round_path,match)
    if not os.path.isdir(match_path): os.makedirs(match_path)
    company_pkl = os.path.join(match_path,company+'.pkl')
    date_pkl = os.path.join(match_path,'date.pkl')
    if not os.path.isfile(date_pkl): joblib.dump(match_date,date_pkl)
    if phase == -1:
        toz_pkl = os.path.join(match_path,'toz.pkl')
        if not os.path.isfile(toz_pkl): joblib.dump(toz,toz_pkl)
        #joblib.dump(toz,toz_pkl)
    #elif phase == 0:        
    return not os.path.isfile(company_pkl), company_pkl
	
def dump_odds(odds_tree):
	root = 'odds_root'
	if not os.path.isdir(root): os.makedirs(root)
	leagues = None
	if odds_tree: leagues = odds_tree.keys()
	for league in leagues:
		league_path = os.path.join(root,league)
		if not os.path.isdir(league_path): os.makedirs(league_path)
		seasons = odds_tree[league].keys()
		for season in seasons:
			season_path = os.path.join(league_path,season)
			if not os.path.isdir(season_path): os.makedirs(season_path)
			rounds = odds_tree[league][season].keys()
			for rnd in rounds:
				round_path = os.path.join(season_path,str(rnd))
				if not os.path.isdir(round_path): os.makedirs(round_path)
				matches = odds_tree[league][season][rnd].keys()
				for match in matches:
					match_path = os.path.join(round_path,match)
					if not os.path.isdir(match_path): os.makedirs(match_path)
					odds_file = os.path.join(match_path,'odds.pkl')
					if not os.path.isfile(odds_file):
						attrs = odds_tree[league][season][rnd][match].keys()
						#odds = {company: odds_tree[league][season][rnd][match][company] for company in companys if company in ['威廉希尔(英国)','立博','韦德']}
						odds = {company: odds_tree[league][season][rnd][match][company] for company in attrs if company not in ['DATE','TOZ']}
						date = odds_tree[league][season][rnd][match]['DATE']
						toz = odds_tree[league][season][rnd][match]['TOZ']
						data = {
							'ODDS': odds,
							'DATE': date,
							'TOZ': toz
						}
						joblib.dump(data,odds_file)
					#return None
	
	
if __name__ == "__main__":

    host = 'zq.titan007.com'
    odd_host = '1x2d.titan007.com'
    odd_root = 'https://1x2.titan007.com'
    root = 'https://' + host
    root_cn = os.path.join(root, 'cn').replace('\\', '/')
    referer = root
    # league_js_rpath = 'jsData/infoHeader.js'
    league_info_url = os.path.join(root, 'jsData/infoHeader.js').replace('\\', '/')
    lea_sea_js_dir = os.path.join(root, 'jsData/matchResult/').replace('\\', '/')
    odd_list_dir = os.path.join(odd_root, 'oddslist/').replace('\\', '/')
    odd_aspx = os.path.join(odd_root, 'OddsHistory.aspx').replace('\\', '/')

    #odd_url = 'http://op1.win007.com/OddsHistory.aspx'

    header = {
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        # 'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
        # 'Referer': 'http://op1.win007.com/oddslist/1721891.htm',
        # 'Host': 'op1.win007.com',
        'referer': referer,
        # 'Cookie': 'ASP.NET_SessionId=xfoi3pdoemlbl4ayxvd0l2mz'
    }
    
    ###########蜻蜓代理#########
    #proxy_host = 'dyn.horocn.com'
    #proxy_port = 50000
    #proxy_username = 'RKQ81659043392907839'
    #proxy_pwd = "hNMLyNmG4yxp"
    #
    #proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    #    "host": proxy_host,
    #    "port": proxy_port,
    #    "user": proxy_username,
    #    "pass": proxy_pwd,
    #}
    #
    #proxy = {
    #    'http': proxyMeta,
    #    'https': proxyMeta,
    #}
    
    
    ONFLOW = False
    task_num = 0
    flow_num = 0
    flows = 0
    flow_time = float(0)
    lock = threading.Lock()		
    start = time.time()
    #dev_sets = catch_datasets('英超',1)
    #mode = 0 散列
    #mode = 1 连续
    catch_datasets('德甲',10,mode=1,phase=-1)
    end = time.time()
    
    runtime = end-start
    runhours = round((end-start)/3600,1)
    runminutes = round((end-start)/60,1)
    if runhours >= 1:
        logging.warning('Wall Time: {} hours !'.format(runhours))
    else:
        logging.warning('Wall Time: {} minutes !'.format(runminutes))
    #index_file = 'index_tree.pkl'
    #data = {'dev_sets': dev_sets}
    #joblib.dump(data,index_file)
    #dump_odds(dev_sets)
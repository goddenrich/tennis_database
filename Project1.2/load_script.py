# -*- coding: utf-8 -*-

import sys
import numpy as np
import pandas as pd
import random
import datetime	
from dateutil.relativedelta import relativedelta
from faker import Factory
from faker import Faker
from faker import providers
import math

def hash1(temp):
	return (hash(temp) % 10**9)

def load_csv(tourney_year):
	#temp = np.genfromtxt('./data/tennis_atp-master/atp_matches_' + tourney_year + '.csv', delimiter=',')
	#print(temp)

	df = pd.read_csv('./data/tennis_atp-master/atp_matches_' + tourney_year + '.csv', sep = ',', dtype=object)
	df = df[~df['tourney_name'].astype(str).str.contains('Davis')]
	df = df[~df['match_num'].isnull()]

	##generate ID's here
	df['complex_ID'] = df['tourney_name'].apply(hash1)
	df['match_ID'] = (df['tourney_id'] + df['match_num'].map(str)).apply(hash1)
	df['tourney_date'] = pd.to_datetime(df['tourney_date'])
	df_max = df['match_num'].max()
	df['match_date'] = df['tourney_date'] + (np.floor(pd.to_numeric(df['match_num'])/float(df_max) *14)).apply(datetime.timedelta)
	#print df['match_date']
	df['x'] = np.random.randint(1,11, size=df.shape[0])
	df['court_ID'] = (df['tourney_id'] + df['x'].astype(str)).apply(hash1)
	#print(df.iloc[0,0])
	#print(df.iloc[0])
	print(df.shape)
	return df


def to_csv(df, name):
	df.to_csv('./results_2017/' + name +'.csv', sep=',', index=False)

def Tournaments(df):
	t = pd.DataFrame(df[['tourney_id', 'tourney_name', 'tourney_date']])
	t = t.drop_duplicates()
	#print(t.shape)
	t.columns = ['tournament_ID', 'name', 'start_date']
	#t['start_date'] = df['tourney_date']
	#end time plus 14 days
	t['end_date'] = t['start_date'] + datetime.timedelta(14)
	t['complex_ID'] = df['complex_ID']
	to_csv(t,'Tournaments')

def Matches(df):
	m = pd.DataFrame()
	m['match_ID'] = df['match_ID']
	m['best_of'] = df['best_of']
	m['round_num'] = df['round']
	m['tournament_ID'] = df['tourney_id']
	m = m.drop_duplicates('match_ID')
	#print(t.shape)
	to_csv(m,'Matches')


def Played_On(df):
	p = pd.DataFrame()
	p['court_ID'] = df['court_ID']
	p['match_ID'] = df['match_ID']
	#random decimal for date 
	#z = np.random.choice(5, s p=[0.0,0.2,0.4,0.3,0.1])
	p['start_dt'] = df['match_date'].apply(lambda x: x + datetime.timedelta(4*np.random.choice(5, p=[0.0,0.2,0.4,0.3,0.1])/24.0))
	p['end_dt'] = p['start_dt'].apply(lambda x: x + datetime.timedelta(np.random.choice(5, p=[0.0,0.2,0.4,0.3,0.1])/24.0))

	#p = p.drop_duplicates()
	to_csv(p,'Played_On')

def Courts(df):
	c = pd.DataFrame()
	#rand = np.random.randint(5,11)
	c['court_ID'] = df['court_ID']
	c['court_name'] = df['tourney_name'] + df['x'].astype(str)
	c['surface'] = df['surface']
	c = c.drop_duplicates()
	c['spectator_capacity'] = np.random.randint(10,100, size=c.shape[0])
	c['indoor'] = np.random.randint(0,2, size=c.shape[0])
	#c['hawkEye'] = True if ['court_ID'] < 4 else False
	c['hawkEye'] = df['x'].apply(lambda x: True if(x<4) else False)
	c['complex_ID'] = df['complex_ID']

	to_csv(c, 'Courts')
	return c[['court_ID' , 'spectator_capacity']]

def Complex(df):
	co = pd.DataFrame()
	co['complex_ID'] = df['complex_ID']
	co['complex_name'] = df['tourney_name']
	#co['city'] = (row['tourney_name'].split(' ')[0] for row in df.iterrows())
	co['city'] = df['tourney_name'].str.split(' ').str.get(0)
	co['country'] = np.nan

	co = co.drop_duplicates('complex_ID')

	to_csv(co, 'Complex')


def Players(df, year):
	p = pd.DataFrame()
	p['player_ID'] = pd.concat([df['winner_id'], df['loser_id']], axis=0, ignore_index=True)
	p['name'] = pd.concat([df['winner_name'], df['loser_name']], axis=0, ignore_index=True)
	p['country'] = pd.concat([df['winner_ioc'], df['loser_ioc']], axis=0, ignore_index=True)
	#y = float(year) - pd.to_numeric(pd.concat([df['winner_age'], df['loser_age']], axis=0, ignore_index=True))

	#dat1 = dt.datetime.strptime(str(20010101.25), "%Y.%m")

	p['dob'] = (float(year) - pd.to_numeric(pd.concat([df['winner_age'], df['loser_age']], axis=0, ignore_index=True))).apply(lambda x: np.nan if math.isnan(x) else datetime.datetime.strptime("{0:.1f}".format(x),"%Y.%M"))
	p['gender'] = 'm'
	p['height'] = pd.concat([df['winner_ht'], df['loser_ht']], axis=0, ignore_index=True)
	
	p['ranking_points'] = pd.concat([df['winner_rank_points'], df['loser_rank_points']], axis=0, ignore_index=True)

	p = p.drop_duplicates('player_ID')
	p['weight'] = 24.0*(pd.to_numeric(p['height'])/100.0)**2

	to_csv(p, 'Players')


def Play_In(df):
	df_c = pd.DataFrame(df)
	#df_c['forfeited'] = 
	p = pd.DataFrame()
	p['player_ID'] = pd.concat([df['winner_id'], df['loser_id']], axis=0, ignore_index=True)
	p['match_ID'] = pd.concat([df['match_ID'], df['match_ID']], ignore_index=True)
	p['winner'] = pd.concat([pd.DataFrame(np.ones((df.shape[0]), dtype=bool)), pd.DataFrame(np.zeros((df.shape[0]), dtype=bool))], ignore_index=True)
	#p['forfeited'] = pd.concat(df[df['score'].str.contains('RET')])
	p['forfeited'] =  pd.concat([df['score'], df['score']], axis=0, ignore_index=True).apply(lambda x: True if('RET' in str(x)) else False)
	p['score'] = pd.concat([df['score'], df['score']], axis=0, ignore_index=True)

	p = p.drop_duplicates()

	to_csv(p, 'Play_In')


def Tickets(df, cap):
	fake = Factory.create()
	t = pd.DataFrame()
	t['mat_ID'] = df['match_ID']
	t['court_ID'] = df['court_ID']
	t['match_date'] = df['match_date']
	#t = pd.concat([t, cap['spectator_capacity']], axis=1, ignore_index=True)
	t['capacity'] = cap['spectator_capacity']
	t = t.fillna(method='ffill')	
	#print t
	
	t = t.reindex(np.repeat(t.index.values, t['capacity'].apply(lambda x: int(x))), method='ffill').reset_index()
	#print t
	#l = pd.DataFrame(t)
	
	t['ticket_ID'] = pd.DataFrame(np.arange(t.shape[0]))

	t['buyer_name'] = np.nan
	t['buyer_name'] = t['buyer_name'].apply(lambda x: fake.name())

	t['price'] = np.random.randint(100,1000, size=t.shape[0])

	z = np.random.randint(3,85)
	t['date_of_sale'] = t['match_date'] - datetime.timedelta(z)
	t['used'] = np.random.choice([0,1], size=t.shape[0], p=[0.035,0.965])
	t['tier'] = np.random.choice([1,2,3], size=t.shape[0], p=[0.7,0.2,0.1])
	t['match_ID'] = t['mat_ID']
	t['spectator_ID'] = pd.DataFrame(np.arange(t.shape[0]))

	f = t[['ticket_ID', 'buyer_name', 'price', 'date_of_sale', 'used', 'tier', 'match_ID', 'spectator_ID']]
	to_csv(f, 'Tickets')
	#print f
	return f

def Spectators(df):
	fake = Faker()
	fake.add_provider(providers.misc)
	fake.add_provider(providers.phone_number)
	s = pd.DataFrame()
	s['spectator_ID'] = df['spectator_ID']
	s['name'] = df['buyer_name']
	s['address'] = np.nan
	s['address'] = s['address'].apply(lambda x: fake.address())
	s['country'] = np.nan
	s['country'] = s['country'].apply(lambda x: fake.country_code())
	s['email'] = np.nan
	s['email'] = s['email'].apply(lambda x: fake.email())
	s['telephone'] = np.nan
	s['telephone'] = s['telephone'].apply(lambda x: fake.phone_number())
	s['gender'] = random.choice(['m','f'], size=s.shape[0])
	s['special_assistance'] = np.random.choice([0,1], size=s.shape[0], p=[0.96,0.04])

	#print s

	to_csv(s,'Spectators')





def main():
	df = load_csv('2017')
	Tournaments(df)
	Matches(df)
	Played_On(df)
	cap = Courts(df)
	Complex(df)
	Players(df, 2017)
	Play_In(df)
	t = Tickets(df, cap)
	Spectators(t)


if __name__ == '__main__':
	main()



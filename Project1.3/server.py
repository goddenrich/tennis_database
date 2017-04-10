#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
#from sqlalchemy import text
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import pygal


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

connection_string = open(".env", 'r').readlines()
#print(connection_string)
engine = create_engine(connection_string[0])


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route('/')
def index():
  return render_template("index.html")

@app.route('/player')
def player():
  print request.args
  return render_template("player.html")

def check(var):
  if(request.form.get(var)):
    return True
  else:
    return False

def player_name(name):
  mystring = """select p.name, p.gender, p.country, p.ranking_points, p.height, p.weight, age(p.dob)
  from players p
  where p.name = %s;"""
  cursor = g.conn.execute(mystring, (name,))

  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()

  return names

def matches_won(name):
  m_won = check('m_won')
  won = None
  if(m_won):
    won = []
    mystring1 = """ select p0.name, t.name, m.round_num, Q.score 
    from (select p2.player_id as id, p2.score as score, p1.match_id as match_id
    from play_in p1, play_in p2, players pl
    where p1.match_id = p2.match_id and p1.player_id != p2.player_id and p1.player_id = pl.player_id 
    and p1.winner= true and pl.name =%s) Q join players p0 on Q.id = p0.player_id 
    join matches m on Q.match_id = m.match_id
    join tournaments t on t.tournament_id = m.tournament_id;"""
    cursor1 = g.conn.execute(mystring1, (name,))
    #where p.name = """ + text + """;""")
    
    for result in cursor1:
      won.append(result)  # can also be accessed using result[0]
    cursor1.close()
  return won

def matches_lost(name):
  m_lost = check('m_lost')
  lost = []
  if(m_lost):
    mystring2 = """ select p0.name, t.name, m.round_num, Q.score 
    from (select p2.player_id as id, p2.score as score, p1.match_id as match_id
    from play_in p1, play_in p2, players pl
    where p1.match_id = p2.match_id and p1.player_id != p2.player_id and p1.player_id = pl.player_id 
    and p1.winner= false and pl.name =%s) Q join players p0 on Q.id = p0.player_id 
    join matches m on Q.match_id = m.match_id
    join tournaments t on t.tournament_id = m.tournament_id;"""
    cursor1 = g.conn.execute(mystring2, (name,))
    #where p.name = """ + text + """;""")
    for result in cursor1:
      lost.append(result)  # can also be accessed using result[0]
    cursor1.close()
  return lost

def matches_forf(name):
  m_for = check('m_for')
  forf = []
  if(m_for):
    mystring3 = """ select p0.name, t.name, m.round_num, Q.score 
    from (select p2.player_id as id, p2.score as score, p1.match_id as match_id
    from play_in p1, play_in p2, players pl
    where p1.match_id = p2.match_id and p1.player_id != p2.player_id and p1.player_id = pl.player_id 
    and p1.winner= false and pl.name =%s and p1.forfeited= true) Q join players p0 on Q.id = p0.player_id 
    join matches m on Q.match_id = m.match_id
    join tournaments t on t.tournament_id = m.tournament_id;"""
    cursor1 = g.conn.execute(mystring3, (name,))
    #where p.name = """ + text + """;""")
    
    for result in cursor1:
      forf.append(result)  # can also be accessed using result[0]
    cursor1.close()
  return forf

def time_played(name):
  t_m_play = check('t_m_play')
  time = []
  if(t_m_play):
    mystring4 = """ select (po.end_dt - po.start_dt)  as duration
    from played_on po
    join matches m on m.match_id = po.match_id
    join play_in pi on m.match_id = pi.match_id
    join players pl on pi.player_id = pl.player_id
    where pl.name = %s;"""
    cursor1 = g.conn.execute(mystring4,(name,))
    #where p.name = """ + text + """;""")
    for result in cursor1:
      time.append(result[0].seconds//3600)  # can also be accessed using result[0]
    cursor1.close()
  return time


def surface_played(name):
  surface = check('surface')
  surface_p = []
  if(surface):
    mystring5 = """select c.surface, count(pi.match_id), count(CASE WHEN pi.winner THEN 1 END)
    from played_on po
    join courts c on c.court_id = po.court_id
    join play_in pi on po.match_id = pi.match_id
    join players pl on pi.player_id = pl.player_id
    where pl.name = %s
    group by c.surface;"""
    cursor1 = g.conn.execute(mystring5, (name,))
    #where p.name = """ + text + """;""")
    for result in cursor1:
      surface_p.append(result)  # can also be accessed using result[0]
    cursor1.close()

  return surface_p

def participate(name):
  partic = check('t_in')
  part = []
  if(partic):
    mystring0 = """ select t.name, m.round_num, p_in.winner
    from players p join play_in p_in on p.player_id = p_in.player_id
    join matches m on m.match_id = p_in.match_id
    join tournaments t on m.tournament_id= t.tournament_id
    where p.name = %s and (p_in.winner = false or (p_in.winner = true and m.round_num = 'F'));"""
    cursor1 = g.conn.execute(mystring0, (name,))
    #where p.name = """ + text + """;""")
    for result in cursor1:
      part.append(result)  # can also be accessed using result[0]
    cursor1.close()
  return part


@app.route('/', methods=['POST'])
def player_post():
  context = {}
  
  name = request.form['name']

  names = player_name(name)
  if not names:
    return render_template("error.html")

  part = participate(name)
  context['part'] = part
  
  won = matches_won(name)
  context['num_won'] = len(won)
  context['won'] = won

  lost = matches_lost(name)
  context['num_lost'] = len(lost)
  context['lost'] = lost

  forf = matches_forf(name)
  context['num_forf'] = len(forf)
  context['forf'] = forf

  time = time_played(name)
  context['time'] = [sum(time), min(time), max(time)]

  surface = surface_played(name)
  context['surface'] = surface[0]
  context['data'] = names[0]
  context['name'] = names[0][0]
  context['gender'] = names[0][1]
  context['country'] = names[0][2]
  context['ranking_points'] = names[0][3]
  context['height'] = names[0][4]
  context['weight'] = names[0][5]
  context['age'] = names[0][6].days/364 -1 

  print(context)

  return render_template("player_add.html", **context)



@app.route('/matches')
def matches():
  return render_template("matches.html")


@app.route('/complex')
def spectator():
  print request.args
  return render_template("complex.html")


@app.route('/complex_success')
def spectator_add():
  print request.args
  return render_template("complex_success.html")

@app.route('/complex_insert', methods=['POST'])
def spectator_insert():
  print request.args
  values={}
  values['complex_id']=int(request.form['complex_id'])
  values['complex_name']= str(request.form['complex_name'])
  values['city'] = str(request.form['city'])
  values['country'] = str(request.form['country'])
  query="""INSERT INTO complex(complex_id, complex_name, city, country) VALUES (%s, %s, %s, %s);"""
  try:
    g.conn.execute(query, (values['complex_id'], values['complex_name'], values['city'], values['country']))
  except:
    return render_template("error.html")
  
  return redirect('/complex_success')

@app.route('/tournament')
def tournament():
  print request.args
  return render_template("tournament.html")

def tournament_details(t_name):
  mystring = """select t.name, t.start_date, t.end_date, c.complex_name, c.city, c.country
  from tournaments t join complex c on c.complex_id = t.complex_id
  where t.name = %s;"""
  cursor = g.conn.execute(mystring , (t_name,))
  names = []
  for result in cursor:
    print result
    names.append(result)  # can also be accessed using result[0]
  cursor.close()
  return names

def ticket_numbers(t_name):
  mystring = """select concat(p.player1_name, ' vs ', p.player2_name), count(ti.ticket_id) as count_t
  from tournaments t, matches m left outer join tickets ti on ti.match_id = m.match_id,
  (select p1.match_id as match_id, p1.player_id as player1_id, 
  p1.name as player1_name, p2.player_id as player2_id, p2.name as player2_name 
  from 
  (select pi.match_id as match_id, p.player_id as player_id, p.name as name 
  from play_in pi, players p where p.player_id = pi.player_id) p1 
  join 
  (select pi.match_id as match_id, p.player_id as player_id, p.name as name 
  from play_in pi, players p where p.player_id = pi.player_id) p2 
  on p1.match_id = p2.match_id where p1.player_id != p2.player_id) p

  where t.name = %s and t.tournament_id = m.tournament_id and p.match_id = m.match_id
  group by p.player1_name, p.player2_name, m.match_id order by count_t;"""
  cursor = g.conn.execute(mystring, (t_name,))

  ticket_n = []
  for result in cursor:
    ticket_n.append(result)  # can also be accessed using result[0]
  cursor.close()

  ticket_graph = bar_graph(ticket_n)

  return ticket_n, ticket_graph

def bar_graph(data):
  graph=pygal.Bar()
  for i, item in enumerate(data):
    graph.add(str(item[0]),item[1])
  return graph

def gender_split(t_name):
  mystring = """select s.gender, count(s.spectator_id)
  from tournaments t, matches m left outer join tickets ti on 
  m.match_id = ti.match_id, spectators s
  where t.name = %s and t.tournament_id = m.tournament_id  
  and s.spectator_id = ti.spectator_id
  group by s.gender;"""
  cursor = g.conn.execute(mystring, (t_name,))

  gender_balance = []
  for result in cursor:
    result_l = []
    result_l.append(str(result[0]) + ": " + str(result[1]))
    result_l.append(result[1])
    gender_balance.append(result_l)  # can also be accessed using result[0]
  cursor.close()
  
  gender_pie = pie_graph(gender_balance)

  return gender_balance, gender_pie

def pie_graph(data):
  graph=pygal.Pie()
  for i, item in enumerate(data):
    graph.add(str(item[0]),item[1])
  return graph

@app.route('/tournament_info', methods=['POST'])
def tournament_post():
  context = {}
  t_name=str(request.form['tournament'])
  names=tournament_details(t_name)
  if not names:
    return render_template("error.html")

  context['data'] = names[0]
  context['name'] = names[0][0]
  context['start_date'] = names[0][1]
  context['end_date'] = names[0][2]
  context['complex_name'] = names[0][3]
  context['city'] = names[0][4]
  context['country'] = names[0][5]
  
  ticket_n, ticket_graph= ticket_numbers(t_name)
  
  context['ticket_numbers'] = ticket_n

  gender_balance, gender_pie = gender_split(t_name)

  context['gender_balance'] = gender_balance
 
  return render_template("tournament_info.html", gender_chart=gender_pie, ticket_chart=ticket_graph, **context)

def check_exists(table, col, search):
  query = """select * from '%s' where '%s' = '%s'"""


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()

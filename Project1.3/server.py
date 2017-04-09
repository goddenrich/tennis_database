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


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
DATABASEURI = "postgresql://rg3047:tennisrules@104.196.18.7/w4111"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
#conn = engine.connect()

#cursor = conn.execute("""
#select p.name, p.height, p.country, age(p.dob)
#from players p join play_in pi on p.player_ID = pi.player_ID join matches m on pi.match_ID = m.match_ID
#where m.round_num = 'F' and p.height > 183
#group by p.name, p.height, p.country, age(p.dob)
#order by age(p.dob) DESC LIMIT 1;""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

#record = cursor.fetchone()
#print(record)

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


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("""
  select p.name, p.height, p.country, age(p.dob) 
  from players p join play_in pi on p.player_ID = pi.player_ID join matches m on pi.match_ID = m.match_ID 
  where m.round_num = 'F' and p.height > 183
  group by p.name, p.height, p.country, age(p.dob)
  order by age(p.dob) DESC LIMIT 1;""")
  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#



@app.route('/another')
def another():
  return render_template("another.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()



@app.route('/player')
def player():
  print request.args


  #
  # example of a database query
  #
  
  #cursor = g.conn.execute("""
  #select p.name, p.height, p.country, age(p.dob) 
  #from players p join play_in pi on p.player_ID = pi.player_ID join matches m on pi.match_ID = m.match_ID 
  #where m.round_num = 'F' and p.height > 183
  #group by p.name, p.height, p.country, age(p.dob)
  #order by age(p.dob) DESC LIMIT 1;""")
  #names = []
  #for result in cursor:
  #  names.append(result)  # can also be accessed using result[0]
  #cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  #context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  #return render_template("player.html", **context)
  return render_template("player.html")


@app.route('/', methods=['POST'])
def player_post():
  context = {}
  name = request.form['name']
  m_won = False

  if(request.form.get('m_won')):
    m_won = True
  #print("INSERT INTO users (name, age) VALUES(%s, %s")

  #print(text)
  
  #mystring = "SELECT p.name, p.gender, p.country, p.ranking_points, p.height, p.weight, age(p.dob) from players p where p.name = '(name)' VALUES(%s) "
  #cursor = g.conn.execute(mystring % name)
  #cursor = g.conn.execute(mystring, '+name)
  #where p.name = """ + text + """;""")
  mystring = """select p.name, p.gender, p.country, p.ranking_points, p.height, p.weight, age(p.dob)
  from players p
  where p.name = '%s';"""
  cursor = g.conn.execute(mystring % name)

  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()

  mystring0 = """ select t.name, m.round_num, p_in.winner
  from players p join play_in p_in on p.player_id = p_in.player_id
  join matches m on m.match_id = p_in.match_id
  join tournaments t on m.tournament_id= t.tournament_id
  where p.name = '%s' and (p_in.winner = false or (p_in.winner = true and m.round_num = 'F'));"""
  cursor1 = g.conn.execute(mystring0 % name)
  #where p.name = """ + text + """;""")
  part = []
  for result in cursor1:
    part.append(result)  # can also be accessed using result[0]
  cursor1.close()

  won = []
  if(m_won):
    mystring1 = """ select p0.name, t.name, m.round_num, Q.score 
    from (select p2.player_id as id, p2.score as score, p1.match_id as match_id
    from play_in p1, play_in p2, players pl
    where p1.match_id = p2.match_id and p1.player_id != p2.player_id and p1.player_id = pl.player_id 
    and p1.winner= true and pl.name ='%s') Q join players p0 on Q.id = p0.player_id 
    join matches m on Q.match_id = m.match_id
    join tournaments t on t.tournament_id = m.tournament_id;"""
    cursor1 = g.conn.execute(mystring1 % name)
    #where p.name = """ + text + """;""")
    
    for result in cursor1:
      won.append(result)  # can also be accessed using result[0]
    cursor1.close()
    context['num_won'] = len(won)
    context['won'] = won

  mystring2 = """ select p0.name, t.name, m.round_num, Q.score 
  from (select p2.player_id as id, p2.score as score, p1.match_id as match_id
  from play_in p1, play_in p2, players pl
  where p1.match_id = p2.match_id and p1.player_id != p2.player_id and p1.player_id = pl.player_id 
  and p1.winner= false and pl.name ='%s') Q join players p0 on Q.id = p0.player_id 
  join matches m on Q.match_id = m.match_id
  join tournaments t on t.tournament_id = m.tournament_id;"""
  cursor1 = g.conn.execute(mystring2 % name)
  #where p.name = """ + text + """;""")
  lost = []
  for result in cursor1:
    lost.append(result)  # can also be accessed using result[0]
  cursor1.close()

  mystring3 = """ select p0.name, t.name, m.round_num, Q.score 
  from (select p2.player_id as id, p2.score as score, p1.match_id as match_id
  from play_in p1, play_in p2, players pl
  where p1.match_id = p2.match_id and p1.player_id != p2.player_id and p1.player_id = pl.player_id 
  and p1.winner= false and pl.name ='%s' and p1.forfeited= true) Q join players p0 on Q.id = p0.player_id 
  join matches m on Q.match_id = m.match_id
  join tournaments t on t.tournament_id = m.tournament_id;"""
  cursor1 = g.conn.execute(mystring3 % name)
  #where p.name = """ + text + """;""")
  forf = []
  for result in cursor1:
    forf.append(result)  # can also be accessed using result[0]
  cursor1.close()


  mystring4 = """ select (po.end_dt - po.start_dt)  as duration
  from played_on po
  join matches m on m.match_id = po.match_id
  join play_in pi on m.match_id = pi.match_id
  join players pl on pi.player_id = pl.player_id
  where pl.name = '%s';"""
  cursor1 = g.conn.execute(mystring4 % name)
  #where p.name = """ + text + """;""")
  time = []
  for result in cursor1:
    time.append(result[0].seconds//3600)  # can also be accessed using result[0]
  cursor1.close()


  mystring5 = """select c.surface, count(pi.match_id), count(CASE WHEN pi.winner THEN 1 END)
  from played_on po
  join courts c on c.court_id = po.court_id
  join play_in pi on po.match_id = pi.match_id
  join players pl on pi.player_id = pl.player_id
  where pl.name = '%s'
  group by c.surface;"""
  cursor1 = g.conn.execute(mystring5 % name)
  #where p.name = """ + text + """;""")
  surface = []
  for result in cursor1:
    surface.append(result)  # can also be accessed using result[0]
  cursor1.close()

  
  context['data'] = names[0]
  context['name'] = names[0][0]
  context['gender'] = names[0][1]
  context['country'] = names[0][2]
  context['ranking_points'] = names[0][3]
  context['height'] = names[0][4]
  context['weight'] = names[0][5]
  context['age'] = names[0][6].days/364 -1 

  context['num_lost'] = len(lost)
  context['lost'] = lost
  context['part'] = part
  context['num_forf'] = len(forf)
  context['forf'] = forf
  print(surface)
  #print(time)
  #print([sum(time), min(time), max(time)])
  context['time'] = [sum(time), min(time), max(time)]
  context['surface'] = surface[0]
  #print(context['time'])

  #print(names[0][6].days)

  #print(context['won'])
  #print(context)

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
  query="""INSERT INTO complex(complex_id, complex_name, city, country) VALUES (%d, '%s', '%s', '%s');"""
  g.conn.execute(query % (values['complex_id'], values['complex_name'], values['city'], values['country']))
  return redirect('/complex_success')

@app.route('/tournament')
def tournament():
  print request.args
  return render_template("tournament.html")

@app.route('/tournament_info', methods=['POST'])
def tournament_post():
  context = {}
  t_name = str(request.form['tournament'])
  
  mystring = """select t.name, t.start_date, t.end_date, c.complex_name, c.city, c.country
  from tournaments t join complex c on c.complex_id = t.complex_id
  where t.name = '%s';"""
  cursor = g.conn.execute(mystring % t_name)

  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()

  context['data'] = names[0]
  context['name'] = names[0][0]
  context['start_date'] = names[0][1]
  context['end_date'] = names[0][2]
  context['complex_name'] = names[0][3]
  context['city'] = names[0][4]
  context['country'] = names[0][5]

  mystring = """select m.match_id, count(ti.ticket_id) as count_t
  from tournaments t, matches m left outer join tickets ti on ti.match_id = m.match_id
  where t.name = '%s' and t.tournament_id = m.tournament_id
  group by m.match_id order by count_t;"""
  cursor = g.conn.execute(mystring % t_name)

  ticket_numbers = []
  for result in cursor:
    ticket_numbers.append(result)  # can also be accessed using result[0]
  cursor.close()

  context['ticket_numbers'] = ticket_numbers

  ticket_graph=pygal.Bar()
  print ticket_numbers
  for i, item in enumerate(ticket_numbers):
    print item
    ticket_graph.add(str(item[0]), item[1])

  mystring = """select s.gender, count(s.spectator_id)
  from tournaments t, matches m left outer join tickets ti on m.match_id = ti.match_id, spectators s
  where t.name = '%s' and t.tournament_id = m.tournament_id  and s.spectator_id = ti.spectator_id
  group by s.gender;"""
  cursor = g.conn.execute(mystring % t_name)

  gender_balance = []
  for result in cursor:
    gender_balance.append(result)  # can also be accessed using result[0]
  cursor.close()

  context['gender_balance'] = gender_balance
 
  gender_pie=pygal.Pie()
  for i, item in enumerate(gender_balance):
    gender_pie.add(item[0], item[1])

  return render_template("tournament_info.html", gender_chart=gender_pie, ticket_chart=ticket_graph, **context)


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

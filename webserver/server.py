#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
from datetime import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "jrd2172"
DB_PASSWORD = "z4jna543"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
#engine.execute("""DROP TABLE IF EXISTS test;""")
#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
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
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
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
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT library_name FROM libraries;")
  names = []
  for result in cursor:
    names.append(result[0])  # can also be accessed using result[0]
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

  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html

  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names


@app.route('/libraries/<some_library>')
def some_place_page(some_library):

    libs = g.conn.execute("SELECT library_name FROM libraries;")
    libraries = []
    for result in libs:
        libraries.append(result[0])  # can also be accessed using result[0]
    libs.close()

    if some_library not in libraries:
        return redirect('/')

    cursor = g.conn.execute("SELECT COUNT(user_id) FROM entries_entered WHERE entry_time > TIMESTAMP '2018-02-16 12:00:00' - INTERVAL '24' HOUR  AND entry_time < '2018-02-16 12:00:00'AND library_name = '"+some_library +"'GROUP BY library_name;")
    fullness = 0
    for number in cursor:
      fullness = number[0]
    cursor.close()

    cursor2 = g.conn.execute("SELECT contact_name, phone_number, location, email_address FROM has_contact_info WHERE library_name = '"+some_library+"'")
    contacts = []
    for contact in cursor2:
         contacts.append(contact)
    cursor2.close()

    cursor3 = g.conn.execute("SELECT photo FROM has_image WHERE library_name = '" + some_library + "'")
    image = null
    for images in cursor3:
         image = images[0]
    cursor3.close()

    cursor4 = g.conn.execute("SELECT close_time,  open_time FROM has_hours_of_operation WHERE library_name = '" + some_library + "'")
    hours = []
    for hour in cursor4:
      hours.append(hour)
    cursor4.close()
    hours = [(hour[0].strftime("%Y-%m-%d %H:%M"), hour[1].strftime("%Y-%m-%d %H:%M")) for hour in hours]

    cursor5 = g.conn.execute("SELECT room_name,start_time, end_time, availability  FROM study_room_reservation WHERE library_name = '"+some_library+"'")
    rooms = []
    for room in cursor5:
        rooms.append(room)
    cursor5.close()

    rooms = [[room[0], room[1].strftime("%Y-%m-%d %H:%M") + "-" +room[2].strftime("%Y-%m-%d %H:%M")] for room in rooms if room[3] == True]

    return render_template("libraries.html", para1= some_library, para2 = fullness, para3 = contacts, para4 = image, para5=hours, para6 = rooms)



# Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
#     name = request.form['name']
#     print name
#     cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
#     g.conn.execute(text(cmd), name1 = name, name2 = name);
#     return redirect('/')

@app.route('/friends', methods=['POST'])
def friends():
    name = request.form['name'].strip();

    first, last = name.split(' ')
    #last = name.split('\s')[1].lower()

    first= first.lower().replace("'","").replace("--","")
    last = last.lower().replace("'","").replace("--","")

    visits = []
    cmd = "SELECT first_name, last_name, library_name FROM users as U, entries_entered as E WHERE U.user_id = E.user_id AND LOWER(first_name) ='" +first+ "' AND LOWER(last_name) = '" + last + "'"
    cursor = g.conn.execute(cmd);
    for instance in cursor:
        visits.append(instance)
    cursor.close()

    if not visits:
        return redirect('/users')
    visits = [ (visit[0] + " " + visit[1], visit[2]) for visit in visits]

    return render_template("friends.html", para1 = visits)

@app.route('/dates', methods=['POST'])
def dates():
    library = request.form['library']
    format = '%Y-%m-%dT%H:%M'
    new_format = '%Y-%m-%d %H:%M:%S'
    try:
        datetime.strptime(request.form['start'], format)
        datetime.strptime(request.form['end'], format)
    except ValueError:
        return redirect('/')
    start = datetime.strptime(request.form['start'], format).strftime(new_format)
    end = datetime.strptime(request.form['end'], format).strftime(new_format)

    cmd = "SELECT COUNT(user_id) FROM entries_entered WHERE entry_time > TIMESTAMP '" + start +"' - INTERVAL '24' HOUR  AND entry_time < '" +end+ "'AND library_name = '"+ library + "'GROUP BY library_name;"
    cursor = g.conn.execute(cmd);
    count = cursor.__next__()[0]
    cursor.close()
    return render_template("dates.html", para1 = count)

@app.route('/addLibrary', methods=['POST'])
def addLibrary():
    library = request.form['library'].lower().title()

    libs = g.conn.execute("SELECT library_name FROM libraries;")
    libraries = []
    for result in libs:
        libraries.append(result[0])  # can also be accessed using result[0]
    libs.close()

    if library not in libraries:
        return redirect('/')
    else:
        return redirect('/libraries/'+ library)


@app.route('/users')
def users():
    cursor = g.conn.execute(
        'SELECT first_name, last_name, library_name FROM users as U, entries_entered as E WHERE U.user_id = E.user_id;')
    users = []
    for user in cursor:
        users.append(user)
    cursor.close()
    users = [(user[0] + " "+user[1], user[2]) for user in users]

    return render_template('users.html', para1 = users)

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


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
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()

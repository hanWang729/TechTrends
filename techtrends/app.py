import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from flask.globals import g
from werkzeug.exceptions import abort
import logging
from datetime import datetime

conn_counter = 0 # global variable for couting connection to the database
post_counter = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global conn_counter
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    conn_counter += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    global post_counter
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    post_counter = len(posts)
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        print(datetime.now())
        app.logger.info('%s Non-existing article' %datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        return render_template('404.html'), 404
    else:
        app.logger.info("%s Article \"%s\" retrieved" %(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), post["title"]))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("The \"About Us\" page is retrieved")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    global post_counter
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            app.logger.info("A new article \"%s\" is created" %title)
            post_counter += 1
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def healthz():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    
    ## log line
    app.logger.info(datetime.now(), 'Status request succesffull')
    return response

@app.route('/metrics')
def metrics():
    global post_counter
    global conn_counter
    response = app.response_class(
        ## TODO: count the real number of connection and post count
            response=json.dumps({"db_connection_count": conn_counter, "post_count": post_counter}),
            status=200,
            mimetype='application/json'
    )

    ## log line
    app.logger.info('Metrics request successfull')
    return response


# start the application on port 3111
if __name__ == "__main__":

    ## stream logs to app.log file
    logging.basicConfig(handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
        ],
        level=logging.DEBUG)

    app.run(host='0.0.0.0', port='3111')

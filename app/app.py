import json
import re
from random import *
import mysql.connector
import simplejson as json
from flask import Flask, request, Response, redirect, render_template, session, url_for
from flask_mail import Mail
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import logging
import json
import math

app = Flask( __name__ )
app.url_map.strict_slashes = False
mysql = MySQL( cursorclass=DictCursor )
mail = Mail( app )
app.secret_key = 'GVGFThjghjygfgiugwgugghjgs'

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'citiesData'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'steelersfan071497@gmail.com'
app.config['MAIL_PASSWORD'] = '**********'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail( app )
otp = randint( 000000, 999999 )
mysql.init_app( app )


@app.route( '/login/', methods=['GET', 'POST'] )
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.get_db().cursor()
        cursor.execute( 'SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,) )
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect( url_for( 'index' ) )
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template( 'login.html', msg=msg )


@app.route( '/logout' )
def logout():
    # Remove session data, this will log the user out
    session.pop( 'loggedin', None )
    session.pop( 'id', None )
    session.pop( 'username', None )
    # Redirect to login page
    return redirect( url_for( 'login' ) )


@app.route( '/pythonlogin/register', methods=['GET', 'POST'] )
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.get_db().cursor()
        cursor.execute( 'SELECT * FROM accounts WHERE username = %s', (username,) )
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match( r'[^@]+@[^@]+\.[^@]+', email ):
            msg = 'Invalid email address!'
        elif not re.match( r'[A-Za-z0-9]+', username ):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute( 'INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,) )
            mysql.get_db().commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template( 'register.html', msg=msg )


#  WIP 1
# Viewing statistics Options Endpoints
@app.route('/viewStatistics/mean', methods=['GET'])
def view_mean_statistics():
    return render_template('./options/mean_option.html', title='Mean Options')


@app.route('/viewStatistics/median', methods=['GET'])
def view_median_statistics():
    return render_template('./options/median_option.html', title='Median Options')


@app.route('/viewStatistics/mode', methods=['GET'])
def view_mode_statistics():
    return render_template('./options/mode_option.html', title='Mode Options')


@app.route('/viewStatistics/standardDeviation', methods=['GET'])
def view_standard_deviation_statistics():
    return render_template('./options/standard_deviation_option.html', title='Standard Deviation Options')


@app.route('/viewStatistics/variance', methods=['GET'])
def view_variance_statistics():
    return render_template('./options/variance_option.html', title='Variance Options')


@app.route('/viewStatistics/zscore', methods=['GET'])
def view_zscore_statistics():
    return render_template('./options/zscore_option.html', title='Z-Score Options')
# End Viewing Options


# Chart Creation Endpoints

@app.route('/createMeanChart', methods=['POST'])
def create_mean_chart():

    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT fldName FROM tblCitiesImport')
    names_result = cursor.fetchall()

    selected_variable = request.form['variable-selection']
    logging.warning("Selected variable is ")
    logging.warning(selected_variable)

    # Retrieve Chose variable content from DB
    # Translate Json Objects to a list of Population
    # Depending on variable chosen
    converted_list_of_values = []
    if selected_variable == 'PopulationA':
        logging.warning("PopulationA Selected")
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))

    elif selected_variable == 'Population1':
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))
    else:
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))

    mean_value = round(mean(converted_list_of_values))
    list_of_names = []
    for name in names_result:
        list_of_names.append(name.get('fldName'))

    return render_template('charts/mean_chart.html',
                           title='View Mean Chart',
                           labels_for_chart=list_of_names,
                           values_for_chart=converted_list_of_values,
                           variable_selection=selected_variable,
                           calculated_mean=mean_value)


@app.route('/createMedianChart', methods=['POST'])
def create_median_chart():

    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT fldName FROM tblCitiesImport')
    names_result = cursor.fetchall()

    selected_variable = request.form['variable-selection']
    logging.warning("Selected variable is ")
    logging.warning(selected_variable)

    # Retrieve Chose variable content from DB
    # Translate Json Objects to a list of Populations
    # Depending on variable chosen
    converted_list_of_values = []
    if selected_variable == 'PopulationA':
        logging.warning("PopulationA Selected")
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))

    elif selected_variable == 'Population1':
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))
    else:
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))

    median_value = round(median(converted_list_of_values))
    list_of_names = []
    for name in names_result:
        list_of_names.append(name.get('fldName'))

    return render_template('charts/median_chart.html',
                           title='View Median Chart',
                           labels_for_chart=list_of_names,
                           values_for_chart=converted_list_of_values,
                           variable_selection=selected_variable,
                           calculated_median=median_value)


@app.route('/createModeChart', methods=['POST'])
def create_mode_chart():

    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT fldName FROM tblCitiesImport')
    names_result = cursor.fetchall()

    selected_variable = request.form['variable-selection']
    logging.warning("Selected variable is ")
    logging.warning(selected_variable)

    # Retrieve Chose variable content from DB
    # Translate Json Objects to a list of Populations
    # Depending on variable chosen
    converted_list_of_values = []
    if selected_variable == 'PopulationA':
        logging.warning("PopulationA Selected")
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))

    elif selected_variable == 'Population1':
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))
    else:
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))

    mode_value = mode(converted_list_of_values)
    list_of_names = []
    for name in names_result:
        list_of_names.append(name.get('fldName'))

    return render_template('charts/mode_chart.html',
                           title='View Mode Chart',
                           labels_for_chart=list_of_names,
                           values_for_chart=converted_list_of_values,
                           variable_selection=selected_variable,
                           calculated_mode=mode_value)


@app.route('/createStandardDeviationChart', methods=['POST'])
def create_standard_deviation_chart():
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT fldName FROM tblCitiesImport')
    names_result = cursor.fetchall()

    selected_variable = request.form['variable-selection']
    logging.warning("Selected variable is ")
    logging.warning(selected_variable)

    # Retrieve Chose variable content from DB
    # Translate Json Objects to a list of Populations
    # Depending on variable chosen
    converted_list_of_values = []
    if selected_variable == 'PopulationA':
        logging.warning("PopulationA Selected")
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))

    elif selected_variable == 'Population1':
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))
    else:
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))

    standard_deviation_value = standard_deviation(converted_list_of_values)
    list_of_names = []
    for name in names_result:
        list_of_names.append(name.get('fldName'))

    return render_template('charts/standard_deviation_chart.html',
                           title='View Standard Deviation Chart',
                           labels_for_chart=list_of_names,
                           values_for_chart=converted_list_of_values,
                           variable_selection=selected_variable,
                           calculated_standard_deviation=standard_deviation_value)


@app.route('/createVarianceChart', methods=['POST'])
def create_variance_chart():

    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT fldName FROM tblCitiesImport')
    names_result = cursor.fetchall()

    selected_variable = request.form['variable-selection']
    logging.warning("Selected variable is ")
    logging.warning(selected_variable)

    # Retrieve Chose variable content from DB
    # Translate Json Objects to a list of Populations
    # Depending on variable chosen
    converted_list_of_values = []
    if selected_variable == 'PopulationA':
        logging.warning("PopulationA Selected")
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))

    elif selected_variable == 'Population1':
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))
    else:
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))

    variance_value = variance(converted_list_of_values)
    list_of_names = []
    for name in names_result:
        list_of_names.append(name.get('fldName'))

    return render_template('charts/variance_chart.html',
                           title='View Variance Chart',
                           labels_for_chart=list_of_names,
                           values_for_chart=converted_list_of_values,
                           variable_selection=selected_variable,
                           calculated_variance=variance_value)


@app.route('/createZScoreChart', methods=['POST'])
def create_zscore_chart():
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT fldName FROM tblCitiesImport')
    names_result = cursor.fetchall()

    selected_variable = request.form['variable-selection']
    raw_score = request.form['raw-score']

    # Retrieve Chose variable content from DB
    # Translate Json Objects to a list of Populations
    # Depending on variable chosen
    converted_list_of_values = []
    if selected_variable == 'PopulationA':
        logging.warning("PopulationA Selected")
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))

    elif selected_variable == 'Population1':
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))
    else:
        cursor.execute('SELECT fldPopulation FROM tblCitiesImport')
        query_results = cursor.fetchall()

        for query_result in query_results:
            converted_list_of_values.append(query_result.get('fldPopulation'))

    zscore_value = zscore(converted_list_of_values, raw_score)
    logging.warning('zscore_value')
    logging.warning(zscore_value)
    list_of_names = []
    for name in names_result:
        list_of_names.append(name.get('fldName'))

    return render_template('charts/zscore_chart.html',
                           title='View ZScore Chart',
                           labels_for_chart=list_of_names,
                           values_for_chart=converted_list_of_values,
                           variable_selection=selected_variable,
                           raw_score=raw_score,
                           calculated_zscore=zscore_value)
# WIP 1 END

# WIP 2
def mean(data):

    num_values = len(data)
    total = 0

    for num in data:
        total = addition(total, num)
    return division(num_values, total)


def median(data):
    data_len = len(data)
    data.sort()

    # data set has even number of elements
    if data_len % 2 == 0:

        # find middle
        mid = math.trunc(division(2, data_len))

        # find middle left value
        mid_left = data[mid - 1]

        # find middle right value
        mid_right = data[mid]

        list_of_items = []
        list_of_items.insert(0, mid_left)
        list_of_items.insert(1, mid_right)
        return mean(list_of_items)
    else:
        # data set has odd number of elements
        return data[math.floor(division(2, data_len))]


def mode(data):
    list_number_of_occurrences = {}
    result = 0
    result_value = 1
    mode_found = False

    # Goes through sample data and creates a dictionary of numbers with associated number of occurrences
    for num in data:
        if num in list_number_of_occurrences:
            list_number_of_occurrences[num] = list_number_of_occurrences[num] + 1
        else:
            list_number_of_occurrences[num] = 1

    # For each number in the dictionary, checks if it's at least greater and adds.
    # Otherwise we skip. We periodically check if we have a mode found during this process.
    for key in list_number_of_occurrences:
        if result_value < list_number_of_occurrences[key]:
            result_value = list_number_of_occurrences[key]
            result = key
            mode_found = True
            continue

        if list_number_of_occurrences[key] == result_value:
            mode_found = False

    if not mode_found:
        raise Exception("No mode found.")

    return result


def standard_deviation(data):
    return square_root(variance(data))


def variance(data):
    n = len(data)
    calculated_mean = mean(data)
    result = 0

    for x in data:
        result = addition(square(subtraction(calculated_mean, x)), result)
    return division(n, result)


# X is the raw score
def zscore(data, x):
    return division(standard_deviation(data), subtraction(mean(data), x))


def addition(a, b):
    return float(b) + float(a)


def subtraction(a, b):
    return float(b) - float(a)


def multiplication(a, b):
    return float(a) * float(b)


def division(a, b):
    if a == 0:
        raise Exception("Cannot divide by zero.")
    return float(b) / float(a)


def square(a):
    return float(a) * float(a)


def square_root(a):
    return float(a) ** 0.5
# WIP 2 END

@app.route( '/', methods=['GET'] )
def index():
    if 'loggedin' in session:
        user = {'username': 'Cities Project'}
        cursor = mysql.get_db().cursor()
        cursor.execute( 'SELECT * FROM tblCitiesImport' )
        result = cursor.fetchall()
        return render_template( 'index.html', title='Home', username=session['username'], cities=result )
    return redirect( url_for( 'login' ) )


@app.route( '/view/<int:city_id>', methods=['GET'] )
def record_view(city_id):
    cursor = mysql.get_db().cursor()
    cursor.execute( 'SELECT * FROM tblCitiesImport WHERE id=%s', city_id )
    result = cursor.fetchall()
    return render_template( 'view.html', title='View Form', city=result[0] )


@app.route( '/edit/<int:city_id>', methods=['GET'] )
def form_edit_get(city_id):
    cursor = mysql.get_db().cursor()
    cursor.execute( 'SELECT * FROM tblCitiesImport WHERE id=%s', city_id )
    result = cursor.fetchall()
    return render_template( 'edit.html', title='Edit Form', city=result[0] )


@app.route( '/edit/<int:city_id>', methods=['POST'] )
def form_update_post(city_id):
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get( 'fldName' ), request.form.get( 'fldLat' ), request.form.get( 'fldLong' ),
                 request.form.get( 'fldCountry' ), request.form.get( 'fldAbbreviation' ),
                 request.form.get( 'fldCapitalStatus' ), request.form.get( 'fldPopulation' ), city_id)
    sql_update_query = """UPDATE tblCitiesImport t SET t.fldName = %s, t.fldLat = %s, t.fldLong = %s, t.fldCountry = 
    %s, t.fldAbbreviation = %s, t.fldCapitalStatus = %s, t.fldPopulation = %s WHERE t.id = %s """
    cursor.execute( sql_update_query, inputData )
    mysql.get_db().commit()
    return redirect( "/", code=302 )


@app.route( '/cities/new', methods=['GET'] )
def form_insert_get():
    return render_template( 'new.html', title='New City Form' )


@app.route( '/cities/new', methods=['POST'] )
def form_insert_post():
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get( 'fldName' ), request.form.get( 'fldLat' ), request.form.get( 'fldLong' ),
                 request.form.get( 'fldCountry' ), request.form.get( 'fldAbbreviation' ),
                 request.form.get( 'fldCapitalStatus' ), request.form.get( 'fldPopulation' ))
    sql_insert_query = """INSERT INTO tblCitiesImport (fldName,fldLat,fldLong,fldCountry,
    fldAbbreviation,fldCapitalStatus,fldPopulation) VALUES (%s, %s,%s, %s,%s, %s,%s) """
    cursor.execute( sql_insert_query, inputData )
    mysql.get_db().commit()
    return redirect( "/", code=302 )


@app.route( '/delete/<int:city_id>', methods=['POST'] )
def form_delete_post(city_id):
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblCitiesImport WHERE id = %s """
    cursor.execute( sql_delete_query, city_id )
    mysql.get_db().commit()
    return redirect( "/", code=302 )


@app.route( '/api/v1/cities', methods=['GET'] )
def api_browse() -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute( 'SELECT * FROM tblCitiesImport' )
    result = cursor.fetchall()
    json_result = json.dumps( result );
    resp = Response( json_result, status=200, mimetype='application/json' )
    return resp


@app.route( '/api/v1/cities/<int:city_id>', methods=['GET'] )
def api_retrieve(city_id) -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute( 'SELECT * FROM tblCitiesImport WHERE id=%s', city_id )
    result = cursor.fetchall()
    json_result = json.dumps( result );
    resp = Response( json_result, status=200, mimetype='application/json' )
    return resp


@app.route( '/api/v1/cities/<int:city_id>', methods=['PUT'] )
def api_edit(city_id) -> str:
    cursor = mysql.get_db().cursor()
    content = request.json
    inputData = (content['fldName'], content['fldLat'], content['fldLong'],
                 content['fldCountry'], content['fldAbbreviation'],
                 content['fldCapitalStatus'], content['fldPopulation'], city_id)
    sql_update_query = """UPDATE tblCitiesImport t SET t.fldName = %s, t.fldLat = %s, t.fldLong = %s, t.fldCountry = 
        %s, t.fldAbbreviation = %s, t.fldCapitalStatus = %s, t.fldPopulation = %s WHERE t.id = %s """
    cursor.execute( sql_update_query, inputData )
    mysql.get_db().commit()
    resp = Response( status=200, mimetype='application/json' )
    return resp


@app.route( '/api/v1/cities', methods=['POST'], strict_slashes=False )
def api_add() -> str:
    content = request.json

    cursor = mysql.get_db().cursor()
    inputData = (content['fldName'], content['fldLat'], content['fldLong'],
                 content['fldCountry'], content['fldAbbreviation'],
                 content['fldCapitalStatus'], request.form.get( 'fldPopulation' ))
    sql_insert_query = """INSERT INTO tblCitiesImport (fldName,fldLat,fldLong,fldCountry,
    fldAbbreviation,fldCapitalStatus,fldPopulation) VALUES (%s, %s,%s, %s,%s, %s,%s) """
    cursor.execute( sql_insert_query, inputData )
    mysql.get_db().commit()
    resp = Response( status=201, mimetype='application/json' )
    return resp


@app.route( '/api/v1/cities/<int:city_id>', methods=['DELETE'] )
def api_delete(city_id) -> str:
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblCitiesImport WHERE id = %s """
    cursor.execute( sql_delete_query, city_id )
    mysql.get_db().commit()
    resp = Response( status=200, mimetype='application/json' )
    return resp


if __name__ == '__main__':
    app.run( host='0.0.0.0', debug=True )

# set FLASK_APP=application.py

import os
import csv
import sqlite3
import dedupe
import ast
import itertools
import logging
import time
import optparse
import locale
import pickle
import multiprocessing
import sys
from flask import Flask, jsonify, render_template, request, url_for, session, redirect, flash, send_from_directory
from flask_jsglue import JSGlue
from flask_session import Session
from tempfile import mkdtemp
from werkzeug import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['csv'])

# application variables
app = Flask(__name__)
jsglue = JSGlue(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
UserID = 1
duplicatedatabase = 'database/DupeDB.sqlite'
settings_file = 'mysql_example_settings'
training_file = 'mysql_example_training.json'

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# testing variables
trainerTest = True


# function to check for the correct file of CSV
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# fucntion to output SQL results to CSV
def resultsToCSV():
    # establish connection
    con = sqlite3.connect(duplicatedatabase)
    c = con.cursor()

    # get result set of possible duplicates
    c.execute(
        'SELECT entity_map.canon_id AS GroupID, entity_map.cluster_score AS Confidence_Score, entity_map.FamilyDUID, ImportedData.LastName, ImportedData.FirstNames, ImportedData.PrimaryAddress1, ImportedData.PrimaryAddress2, ImportedData.PrimaryCity, ImportedData.PrimaryState, ImportedData.PrimaryPostalCode, ImportedData.OwnerOrganizationID, ImportedData.OwnerOrganizationName, ImportedData.OwnerOrganizationCity FROM entity_map INNER JOIN ImportedData ON entity_map.FamilyDUID = ImportedData.FamilyDUID WHERE entity_map.UserID = ?',
        (UserID,))

    # write duplicates to results file
    with open('results/results.csv', "w", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in c.description])
        csv_writer.writerows(c)

    con.commit()
    con.close()
    return None


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        # check if the post request has teh file part
        if 'data_source' not in request.files:
            flash('No file part')
            return redirect(request.url)
        f = request.files['data_source']
        # if user does not select file, browser also
        # submit an empty part without filename
        if f.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if not allowed_file(f.filename):
            return ('invalid filetype')

        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            os.rename(('uploads/{}'.format(filename)), 'uploads/source_data.csv')
            return redirect(url_for('csv_processor'))
    else:
        redirect(url_for('index'))


@app.route('/csv_processor')
def csv_processor():
    # create connection to database
    conn = sqlite3.connect(duplicatedatabase)
    c = conn.cursor()

    c.execute("DELETE FROM ImportedData")
    conn.commit()

    # store CSV in memory` as dict
    with open('uploads/source_data.csv', 'rt', encoding='utf-8', errors='ignore') as f:
        # TODO Write error check on failed to open CSV.
        reader = csv.DictReader(f)
        to_db = [(i['FamilyDUID'], i['LastName'], i['FirstNames'], i['PrimaryAddress1'], i['Primary Address 2'],
                  i['PrimaryCity'], i['PrimaryState'], i['PrimaryPostalCode'], i['OwnerOrganizationID'],
                  i['OwnerOrganizationName'], i['Owner Organization City']) for i in reader]
    os.remove('uploads/source_data.csv')

    # write dict to SQL DB
    c.executemany(
        "INSERT INTO ImportedData (FamilyDUID, LastName, FirstNames, PrimaryAddress1, PrimaryAddress2, PrimaryCity, PrimaryState, PrimaryPostalCode, OwnerOrganizationID, OwnerOrganizationName, OwnerOrganizationCity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
        to_db)

    # associate all rows with the userID
    c.execute("UPDATE ImportedData SET UserID = {ID};".format(ID=UserID))
    c.execute(
        "UPDATE ImportedData SET PrimaryPostalCode = '0' || PrimaryPostalCode WHERE Length(PrimaryPostalCode) = 4")

    # sanitize the data of supposed NULLS and blanks
    c.execute("UPDATE ImportedData SET LastName = null WHERE LastName like ' ' OR LastName like 'NULL'")
    c.execute("UPDATE ImportedData SET FirstNames = null WHERE FirstNames like ' ' OR FirstNames like 'NULL'")
    c.execute("UPDATE ImportedData SET PrimaryAddress1 = null WHERE PrimaryAddress1 like ' ' OR PrimaryAddress1 like 'NULL'")
    c.execute("UPDATE ImportedData SET PrimaryAddress2 = null WHERE PrimaryAddress2 like ' ' OR PrimaryAddress2 like 'NULL'")
    c.execute("UPDATE ImportedData SET PrimaryCity = null WHERE PrimaryCity like ' ' OR PrimaryCity like 'NULL'")
    c.execute("UPDATE ImportedData SET PrimaryState = null WHERE PrimaryState like ' ' OR PrimaryState like 'NULL'")
    c.execute("UPDATE ImportedData SET PrimaryPostalCode = null WHERE PrimaryPostalCode like 'Unknown' ")

    # commit the transaction to SQL DB
    conn.commit()
    conn.close()

    # establish the connection
    con = sqlite3.connect(duplicatedatabase)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    con2 = sqlite3.connect(duplicatedatabase)
    cur2 = con2.cursor()

    # get column names of the table
    cur.execute("pragma table_info(" + 'ImportedData' + ")")

    # update each column to remove all instances of '' or blanks replacing them with NULL
    for row in cur.fetchall():
        if row['notnull'] == 0:
            cur2.execute("UPDATE " + 'ImportedData' + " SET " + row['name'] + " = NULL WHERE " + row['name'] + " = ''")

    # commit and close both connections
    con.commit()
    con2.commit()
    con.close()
    con2.close()

    # run SQLdeduper
    if not trainerTest:
        os.system('python sqldeduper.py')

        # write results out
        resultsToCSV()
        # finish by sending the user to the results screen.
        return redirect(url_for('results'))

    return redirect(url_for('trainer'))


@app.route('/trainer')
def trainer():
    # instantiate connection to database
    con = sqlite3.connect(duplicatedatabase)
    con.row_factory = dict_factory
    c = con.cursor()

    # delete the settings file
    if os.path.exists(settings_file):
        os.remove(settings_file)

        # Define the fields dedupe will pay attention to
        #
        # The address, city, and zip fields are often missing, so we'll
        # tell dedupe that, and we'll learn a model that take that into
        # account

    # ensure parameters are present
    session["fields"] = [
        {'field': 'LastName', 'type': 'String', 'has missing': True},
        {'field': 'FirstNames', 'type': 'String', 'has missing': True},
        {'field': 'PrimaryAddress1', 'type': 'String', 'has missing': True},
        {'field': 'PrimaryAddress2', 'type': 'String', 'has missing': True},
        {'field': 'PrimaryCity', 'type': 'String', 'has missing': True},
        {'field': 'PrimaryState', 'type': 'Exact', 'has missing': True},
        {'field': 'PrimaryPostalCode', 'type': 'ShortString', 'has missing': True}
    ]

    # Create a new deduper object and pass our data model to it.
    session["deduper"] = dedupe.Dedupe(session["fields"])
    session["dataset_select"] = "SELECT FamilyDUID, LastName, FirstNames, PrimaryAddress1, PrimaryAddress2, PrimaryCity, PrimaryState, PrimaryPostalCode FROM ImportedData WHERE UserID = ?"

    c.execute(session["dataset_select"], (UserID,))
    temp_d = dict((i, row) for i, row in enumerate(c))

    # instantiate dedupe sampler
    session["deduper"].sample(temp_d, 20000)
    del temp_d

    # delete the training file
    if os.path.exists(training_file):
        os.remove(training_file)

    return render_template('trainer.html')


@app.route('/uncertain_pairs')
def uncertain_pairs():
    """Return a set of unknown pairs"""
    requested_pairs = []

    for pairs in session["deduper"].uncertainPairs():
        for pair in pairs:
            requested_pairs.append(pair)

    return jsonify(requested_pairs)


@app.route('/markpairs', methods=["POST"])
def markpairs():
    """Mark a set of pairs as duplicate or not and add them to a list."""

    # grab the JSON data from the client
    matchedpairs = request.get_json()

    # create a dict to store the examples of matched and distinct records
    labeled_examples = {'match': [],
                       'distinct': []
                       }

    # write to labeled examples depending on the match type
    if matchedpairs['match_type'] == 'match':
        labeled_examples['match'].append(tuple(matchedpairs['pairs']))

    if matchedpairs['match_type'] == 'distinct':
        labeled_examples['distinct'].append(tuple(matchedpairs['pairs']))

    print(labeled_examples)

    # update the session's deduper with the labeled examples
    session["deduper"].markPairs(labeled_examples)

    with open(training_file, 'w') as tf:
        session["deduper"].writeTraining(tf)

    return (jsonify('Request Complete'))



@app.route('/finish_training')
def finishTraining():
    """Finish the training module"""

    # TODO something about this isn't working in flask. I tried creating a new deduper object, but that failed
    # so now I'm thinking about passing the deduper.training_data attribute from the session dedupe to the
    # new instance of dedupe as a means of writing out the session data.
    # that might allow me to run this without trouble.

    # instantiate connection to database
    con = sqlite3.connect(duplicatedatabase)
    con.row_factory = dict_factory
    c = con.cursor()

    local_deduper = dedupe.Dedupe(session["fields"])

    c.execute(session["dataset_select"], (UserID,))
    temp_d = dict((i, row) for i, row in enumerate(c))

    # instantiate dedupe sampler
    local_deduper.sample(temp_d, 10000)
    del temp_d

    if os.path.exists(training_file):
        print('reading labeled examples from ', training_file)
        with open(training_file) as tf :
            local_deduper.readTraining(tf)

    local_deduper.train(recall=0.90)

    with open(settings_file, 'wb') as sf:
        local_deduper.writeSettings(sf)

    local_deduper.cleanupTraining()

    return redirect(url_for('process_duplicates'))

@app.route('/process_duplicates')
def process_duplicates():

    if os.path.exists(settings_file):
        print('reading from ', settings_file)
        with open(settings_file, 'rb') as sf:
            local_deduper = dedupe.StaticDedupe(sf)
    else:
        print('Settings do not exist')

    start_time = time.time()

    con = sqlite3.connect(duplicatedatabase)
    con.row_factory = dict_factory

    c = con.cursor()

    ## Blocking

    print('blocking...')

    # To run blocking on such a large set of data, we create a separate table
    # that contains blocking keys and record ids
    print('creating blocking_map database')
    c.execute("DROP TABLE IF EXISTS blocking_map")
    c.execute("CREATE TABLE blocking_map"
              "(block_key VARCHAR(200), FamilyDUID INTEGER)")

    # If dedupe learned an Index Predicate, we have to take a pass
    # through the data and create indices.
    print('creating inverted index')

    for field in local_deduper.blocker.index_fields:
        c.execute("SELECT DISTINCT {field} FROM ImportedData "
                  "WHERE {field} IS NOT NULL AND UserID = {ID}".format(field=field, ID=UserID))
        field_data = set(row[field] for row in c.fetchall())
        local_deduper.blocker.index(field_data, field)

    # Now we are ready to write our blocking map table by creating a
    # generator that yields unique `(block_key, donor_id)` tuples.
    print('writing blocking map')

    c.execute("SELECT FamilyDUID, LastName, FirstNames, PrimaryAddress1, PrimaryAddress2, PrimaryCity, PrimaryState, PrimaryPostalCode FROM ImportedData WHERE UserID = ?",
        (UserID,))
    full_data = []
    for row in c.fetchall():
        data_tuple = (row['FamilyDUID'], row)
        full_data.append(data_tuple)
    b_data = local_deduper.blocker(full_data)

    # MySQL has a hard limit on the size of a data object that can be
    # passed to it.  To get around this, we chunk the blocked data in
    # to groups of 30,000 blocks
    step_size = 30000

    # We will also speed up the writing by of blocking map by using
    # parallel database writers
    def dbWriter(sql, rows):
        conn = sqlite3.connect(duplicatedatabase)

        cursor = conn.cursor()
        cursor.executemany(sql, rows)
        cursor.close()
        conn.commit()
        conn.close()

    done = False

    while not done:
        chunks = (list(itertools.islice(b_data, step)) for step in [step_size] * 100)

        results = []

        for chunk in chunks:
            results.append(dbWriter("INSERT INTO blocking_map VALUES (?, ?)",
                                    chunk))
        if len(chunk) < step_size:
            done = True

    # Free up memory by removing indices we don't need anymore
    local_deduper.blocker.resetIndices()

    # Remove blocks that contain only one record, sort by block key and
    # donor, key and index blocking map.

    # These steps, particularly the sorting will let us quickly create
    # blocks of data for comparison
    print('prepare blocking table. this will probably take a while ...')

    logging.info("indexing block_key")
    c.execute("DROP INDEX IF EXISTS index_blocking_map")
    c.execute("CREATE UNIQUE INDEX index_blocking_map "
              " ON blocking_map (block_key, FamilyDUID)")

    c.execute("DROP TABLE IF EXISTS plural_key")
    c.execute("DROP TABLE IF EXISTS plural_block")
    c.execute("DROP TABLE IF EXISTS covered_blocks")
    c.execute("DROP TABLE IF EXISTS smaller_coverage")

    # Many block_keys will only form blocks that contain a single
    # record. Since there are no comparisons possible within such a
    # singleton block we can ignore them.
    #
    # Additionally, if more than one block_key forms identifical blocks
    # we will only consider one of them.
    logging.info("calculating plural_key")
    c.execute("CREATE TABLE plural_key"
              "('block_key' VARCHAR(200), "
              "'block_id' INTEGER PRIMARY KEY AUTOINCREMENT)")
    c.execute(
        "INSERT INTO plural_key (block_key) SELECT MIN(block_key) block_key FROM (SELECT block_key, group_concat(FamilyDUID) AS block FROM (SELECT block_key, FamilyDUID FROM blocking_map ORDER BY block_key, FamilyDUID) GROUP BY block_key HAVING COUNT(*) > 1) AS blocks GROUP BY block")
    con.commit()

    logging.info("creating block_key index")
    c.execute("CREATE UNIQUE INDEX block_key_idx ON plural_key (block_key)")

    logging.info("calculating plural_block")
    c.execute("CREATE TABLE plural_block AS "
              "SELECT block_id, FamilyDUID "
              " FROM blocking_map INNER JOIN plural_key "
              " USING (block_key)")

    logging.info("adding FamilyDUID index and sorting index")
    c.execute("CREATE INDEX index_FamDUID ON plural_block (FamilyDUID)")
    c.execute("CREATE UNIQUE INDEX index_blockID_FamDUID ON plural_block (block_id, FamilyDUID)")

    # To use Kolb, et.al's Redundant Free Comparison scheme, we need to
    # keep track of all the block_ids that are associated with a
    # particular donor records. We'll use MySQL's GROUP_CONCAT function to
    # do this. This function will truncate very long lists of associated
    # ids, so we'll also increase the maximum string length to try to
    # avoid this.

    # commeting this out since I can't change the max length of group_concat in SQLite
    # c.execute("SET SESSION group_concat_max_len = 2048")

    logging.info("creating covered_blocks")
    c.execute("CREATE TABLE covered_blocks AS "
              "SELECT FamilyDUID, group_concat(block_ID) AS sorted_ids "
              " FROM (SELECT FamilyDUID, block_ID "
              " FROM plural_block "
              " ORDER BY FamilyDUID, block_ID) "
              " GROUP BY FamilyDUID ")

    c.execute("CREATE UNIQUE INDEX donor_idx ON covered_blocks (FamilyDUID)")

    def findsortedID(sortedIDs, block_ID):

        # split the sortedIDs string into a list
        idlist = sortedIDs.split(',')

        # initialize the final container
        outlist = []

        # cycle through the list buidling the result stopping if the string == the block_id
        for i in idlist:

            if i.strip() == str(block_ID):
                break
            else:
                outlist.append(i)

            outlist.append(',')

        # format the string
        result = ''.join(outlist).replace(' ', '').rstrip(',')

        return result

    # In particular, for every block of records, we need to keep
    # track of a donor records's associated block_ids that are SMALLER than
    # the current block's id. Because we ordered the ids when we did the
    # GROUP_CONCAT we can achieve this by using some string hacks.
    logging.info("creating smaller_coverage")

    c.execute("CREATE TABLE smaller_coverage (FamilyDUID INT, block_id INT, smaller_ids TEXT) ")

    c.execute("SELECT covered_blocks.FamilyDUID, block_id, sorted_ids "
              "FROM plural_block INNER JOIN covered_blocks on "
              "plural_block.FamilyDUID = covered_blocks.FamilyDUID")

    for row in c.fetchall():
        smaller_id = findsortedID(row['sorted_ids'], row['block_id'])

        c.execute("INSERT INTO smaller_coverage VALUES (?, ?, ?)", (row['FamilyDUID'], row['block_id'], smaller_id))

    con.commit()

    ## Clustering

    def candidates_gen(result_set):
        lset = set

        block_id = None
        records = []
        i = 0
        for row in result_set:
            if row['block_id'] != block_id:
                if records:
                    yield records

                block_id = row['block_id']
                records = []
                i += 1

                if i % 10000 == 0:
                    print(i, "blocks")
                    print(time.time() - start_time, "seconds")

            smaller_ids = row['smaller_ids']

            if smaller_ids:
                smaller_ids = lset(smaller_ids.split(','))
            else:
                smaller_ids = lset([])

            records.append((row['FamilyDUID'], row, smaller_ids))

        if records:
            yield records

    c.execute(
        "SELECT ImportedData.FamilyDUID, LastName, FirstNames, PrimaryAddress1, PrimaryAddress2, PrimaryCity, PrimaryState, PrimaryPostalCode, block_id, smaller_ids "
        "FROM ImportedData "
        "INNER JOIN smaller_coverage ON ImportedData.FamilyDUID = smaller_coverage.FamilyDUID "
        " WHERE UserID = ? "
        " ORDER BY block_ID", (UserID,))

    print('clustering...')
    clustered_dupes = local_deduper.matchBlocks(candidates_gen(c),
                                          threshold=0.5)

    con.commit()

    ## Writing out results

    # We now have a sequence of tuples of donor ids that dedupe believes
    # all refer to the same entity. We write this out onto an entity map
    # table
    c.execute("DROP TABLE IF EXISTS entity_map")

    print('creating entity_map database')
    c.execute("CREATE TABLE entity_map "
              "(FamilyDUID INTEGER PRIMARY KEY, canon_id INTEGER, "
              " cluster_score FLOAT, UserID INTEGER)")

    for cluster, scores in clustered_dupes:
        cluster_id = cluster[0]
        for FamilyDUID, score in zip(cluster, scores):
            c.execute('INSERT INTO entity_map VALUES (?, ?, ?, ?)',
                      (int(FamilyDUID), int(cluster_id), float(score), UserID))

    con.commit()

    c.execute("CREATE INDEX head_index ON entity_map (canon_id)")
    con.commit()

    return redirect(url_for('results'))

@app.route('/results')
def results():

    resultsToCSV()

    return render_template('results.html')


@app.route('/results_file')
def results_file():
    return send_from_directory(directory='results', filename='results.csv', as_attachment=True)

@app.route('/howto')
def howto():
    return render_template('howto.html')

@app.route('/about')
def about():
    return render_template('about.html')
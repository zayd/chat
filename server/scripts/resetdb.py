import psycopg2

conn = psycopg2.connect(dbname='responses', user='dthirman', host='udacity.cjsia33swned.us-west-1.redshift.amazonaws.com', port='5439', password='Udacity1')
cur = conn.cursor()

cur.execute("truncate javascript.submitted_grade_and_next_user;")
cur.execute("truncate javascript.submitted_grade;")
cur.execute("truncate javascript.identifies;")
cur.execute("truncate javascript.entered_grade;")
cur.execute("truncate javascript.entered_response;")

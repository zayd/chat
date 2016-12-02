from ranker import app, db, User, Page

db.create_all()



# page = Page('1234', 2)
# db.session.add(page)
# db.session.commit()
# # user = Page.query.filter().all()[0]
# # db.session.delete(user)
# # db.session.commit()


# users = Page.query.filter().all()
# print users
# #db.create_all()
# admin = User('admin', 'admin', 'admin@example.com')
# # db.session.add(admin)
# # db.session.commit()
# users = User.query.filter().all()
# print [str(x.username)+"," + str(x.email) for x in users]

# import psycopg2

# conn = psycopg2.connect(dbname='responses', user='dthirman', host='udacity.cjsia33swned.us-west-1.redshift.amazonaws.com', port='5439', password='Udacity1')
# cur = conn.cursor()

# cur.execute("select original_timestamp, context_page_search from javascript.submitted_grade_and_next_user where context_page_search like '%id=8675309%';")
# colnames = [desc[0] for desc in cur.description]
# print colnames
# identifies = cur.fetchall();
# for i in identifies:
#     print i
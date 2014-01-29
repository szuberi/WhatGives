import os
from flask import Flask, render_template, request, jsonify
import MySQLdb
import pickle
import numpy as np
import dateutil.parser
import csv
import math

app = Flask(__name__)

def sqlExec(query):
    db = MySQLdb.connect(user="root", host="localhost", port=3306, db='loans')
    with db:
        cur = db.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(query)
        tables = cur.fetchall()
        return tables


#db = MySQLdb.connect(user="root",host="localhost",port=3306,db="loans")

@app.route("/")
def hello():
    #return "Hello World!"
    return render_template('index.html')

@app.route("/index.html")
def indexfn():
    return render_template('index.html')

@app.route("/about")
def aboutfn():
    return render_template('about.html')

@app.route("/app")
def appfn():
    return render_template('app.html')

@app.route("/search.html")
def search():
    loan_id = int(request.args.get("loan_id",None))

    pickle.dump( loan_id, open( "passloan.pkl", "wb" ) )
    
    loan_info=sqlExec("SELECT  name, borrowers_gender, location_country, sector, activity, loan_amount, description_num_languages, posted_date, terms_repayment_term, partner_id, image_id from Loans where loan_id = %d;" % loan_id)
    
    posted_date_months=loan_info[0]['posted_date'].month
    
    image_id_str = str(loan_info[0]['image_id'])
    
    (country_map, sector_map, borrower_gender_map,activity_map) = pickle.load( open( "maps.pkl", "rb" ) )
    
    #input_loan_amount = int(request.args.get("input_loan_amount",0,type = int))
    
    xin = np.array( [borrower_gender_map[loan_info[0]['borrowers_gender']],loan_info[0]['description_num_languages'],loan_info[0]['loan_amount'],country_map[loan_info[0]['location_country']], sector_map[loan_info[0]['sector']],activity_map[loan_info[0]['activity']],posted_date_months,loan_info[0]['partner_id'],loan_info[0]['terms_repayment_term'] ]  )
    
    clf = pickle.load( open( "alg.pkl", "rb" ) )
    y = clf.predict(xin)[0]
    prob_fund = clf.predict_proba(xin)[0][0]
    
    if y == 0:
        ypred = 'Funded!'
    elif y ==1:
        ypred = 'Not Funded'


    return render_template('search.html',loan_id=loan_id, loan_info=loan_info,posted_date_months=posted_date_months, image_id_str =image_id_str,ypred=ypred, prob_fund=prob_fund)

@app.route("/eval.html")
def eval():
    loan_id = pickle.load( open( "passloan.pkl", "rb" ) )
    
    loan_info=sqlExec("SELECT  name,borrowers_gender, location_country, sector, activity, loan_amount, description_num_languages, posted_date, terms_repayment_term, partner_id from Loans where loan_id = %d;" % loan_id)
    
    posted_date_months=loan_info[0]['posted_date'].month
    
    (country_map, sector_map, borrower_gender_map,activity_map) = pickle.load( open( "maps.pkl", "rb" ) )
    
    clf = pickle.load( open( "alg.pkl", "rb" ) )
    
    requested_loan_amount = loan_info[0]['loan_amount']
    requested_repayment_term = loan_info[0]['terms_repayment_term']

    if requested_repayment_term > 10:
        month_pred = [i for i in range(requested_repayment_term-10,requested_repayment_term+10)]
    else:
        month_pred = [(i+1) for i in range(20)]

    roundedReqAmt = int(math.floor(requested_loan_amount/100))

    if requested_loan_amount > 1000:
        gridAmtSet = int(math.floor(requested_loan_amount/100))
    else:
        gridAmtSet = 5

    amount_pred = [100*i for i in range(gridAmtSet-5,gridAmtSet+5)]
    
    #create list of tuples for (amount, month, funding prob )
    predMatrix=[]
    for amount in amount_pred:
        for month in month_pred:
            xin = np.array( [borrower_gender_map[loan_info[0]['borrowers_gender']],loan_info[0]['description_num_languages'],amount,country_map[loan_info[0]['location_country']], sector_map[loan_info[0]['sector']],activity_map[loan_info[0]['activity']],posted_date_months,loan_info[0]['partner_id'],month ]  )

            predprob = clf.predict_proba(xin)[0][0]
            predMatrix.append((amount, month, predprob) )
    
    # write to tsv file
    ofile  = open('static/data.tsv', "wb")
    writer = csv.writer(ofile,delimiter='\t')

    writer.writerow(['day','hour', 'value'])
    for row in predMatrix:
                writer.writerow(row)
    ofile.close()

    amount_pred_str = str(amount_pred)
    month_pred_str = str(month_pred)

    return render_template('eval.html',loan_info=loan_info,loan_id=loan_id,roundedReqAmt=roundedReqAmt,requested_repayment_term=requested_repayment_term,gridAmtSet=gridAmtSet,amount_pred_str=amount_pred_str,month_pred_str=month_pred_str)



@app.route("/db")
def cities_page():
    db.query("SELECT Name FROM city;")
    query_results=db.store_result().fetch_row(maxrows=0)
    cities = ""
    for result in query_results:
        cities += unicode(result[0],'ISO-8859-1')
        cities += "<br>"
    return cities

@app.route("/db_fancy")
def cities_page_fancy():
    db.query("SELECT Name, CountryCode, Population FROM city;")
    
    query_results = db.store_result().fetch_row(maxrows=0)
    cities = []
    for result in query_results:
        cities.append(dict(name=unicode(result[0], 'ISO-8859-1'), country=result[1], population=result[2]))
    return render_template('cities.html', cities=cities)


@app.route("/blocker")
def block():
    return "Blocked!"

@app.route('/<pagename>')
def regularpage(pagename = None):
    """
        Route not found by the other routes above.
        """
    return "You've arrived at : " + pagename

if __name__ == "__main__":
    app.run(debug=True,host='localhost')

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
    db = MySQLdb.connect(user="root", host="0.0.0.0", port=3306, db='loans')
    with db:
        cur = db.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(query)
        tables = cur.fetchall()
        return tables


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
    
    loan_info=sqlExec("SELECT  name, borrowers_gender, location_country,location_country_code, sector, loan_amount, description_num_languages, posted_date, terms_repayment_term, image_id from Loans where loan_id = %d;" % loan_id)
    
    posted_date_months=loan_info[0]['posted_date'].month
    

    image_id_str = str(loan_info[0]['image_id'])
    
    # change country code to continent
    continent_map = pickle.load( open( "continent_map.pkl", "rb" ) )
    continent = continent_map[loan_info[0]['location_country_code']]
    
    #vectorize contients and sectors
    (contdict,sectordict) = pickle.load( open( "contsect_dict.pkl", "rb" ) )
    continent_vec = contdict[continent]
    sector_vec = sectordict[loan_info[0]['sector']]
    
    if loan_info[0]['borrowers_gender'] == 'F':
        borrowers_gender = 1
    else:
        borrowers_gender=0

    xin = np.append(continent_vec,sector_vec)
    xin = np.append(xin,np.array( [borrowers_gender,loan_info[0]['description_num_languages'],loan_info[0]['loan_amount'],posted_date_months,loan_info[0]['terms_repayment_term'] ] ))
    
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
    
    loan_info=sqlExec("SELECT  name, borrowers_gender, location_country,location_country_code, sector, loan_amount, description_num_languages, posted_date, terms_repayment_term, image_id from Loans where loan_id = %d;" % loan_id)
    
    posted_date_months=loan_info[0]['posted_date'].month

    # change country code to continent
    continent_map = pickle.load( open( "continent_map.pkl", "rb" ) )
    continent = continent_map[loan_info[0]['location_country_code']]
    #vectorize contients and sectors
    (contdict,sectordict) = pickle.load( open( "contsect_dict.pkl", "rb" ) )
    continent_vec = contdict[continent]
    sector_vec = sectordict[loan_info[0]['sector']]
    
    if loan_info[0]['borrowers_gender'] == 'F':
        borrowers_gender = 1
    else:
        borrowers_gender=0


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
            xin = np.append(continent_vec,sector_vec,1)
            xin = np.append(xin,np.array( [borrowers_gender,loan_info[0]['description_num_languages'],amount,posted_date_months,month ] ))

            #xin = np.array( [borrower_gender_map[loan_info[0]['borrowers_gender']],loan_info[0]['description_num_languages'],amount,country_map[loan_info[0]['location_country']], sector_map[loan_info[0]['sector']],activity_map[loan_info[0]['activity']],posted_date_months,loan_info[0]['partner_id'],month ]  )

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
    app.run(debug=True,host='0.0.0.0',port=5000)

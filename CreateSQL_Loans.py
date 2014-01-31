import MySQLdb as db
import json
import datetime
import dateutil.parser



con = db.connect(user="root",host="localhost",port=3306,db="loans")


with con:
    #First create the table
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS Loans")
    cur.execute("CREATE TABLE Loans(activity TEXT NOT NULL, \
                bonus_credit_eligibility BOOL NOT NULL, \
                borrowers_first_name TEXT NOT NULL, \
                borrowers_gender TEXT NOT NULL, \
                borrowers_last_name TEXT NOT NULL, \
                borrowers_pictured BOOL NOT NULL, \
                description_num_languages INT NOT NULL, \
                funded_amount INT NOT NULL,\
                funded_date DATETIME NOT NULL,\
                loan_id INT NOT NULL,\
                image_id INT NOT NULL,\
                image_template_id INT NOT NULL,\
                journal_totals_bulkEntries INT NOT NULL,\
                journal_totals_entries INT NOT NULL,\
                lender_count INT NOT NULL,\
                loan_amount INT NOT NULL,\
                location_country TEXT NOT NULL,\
                location_geo TEXT NOT NULL,\
                location_town TEXT NOT NULL,\
                name TEXT NOT NULL,\
                partner_id INT NOT NULL,\
                planned_expiration_date DATETIME NOT NULL,\
                posted_date DATETIME NOT NULL,\
                sector TEXT NOT NULL,\
                status TEXT NOT NULL,\
                terms_loss_liability_currency_exchange TEXT NOT NULL,\
                terms_loss_liability_nonpayment TEXT NOT NULL,\
                terms_repayment_interval TEXT NOT NULL,\
                terms_repayment_term INT NOT NULL,\
                location_country_code TEXT NOT NULL,\
                PRIMARY KEY(loan_id)) ENGINE = InnoDB;")

    #jsonfiles = ['850','851','852','853']
    jsonfiles=[]
    for i in range(500):
        jsonfiles.append(str(749+i) )

    for file in jsonfiles:
        #Use Kiva loan data in json format and populate MySQL database
        path = '/Users/saba/Documents/Insight/KivaProjectResources/kiva_ds_json/loans/' + file + '.json'
        loanjson_meta = [json.loads(line) for line in open(path)]
        loanjson = loanjson_meta[0]['loans']


        #Now populate the table
        for i in range(len(loanjson)):
        
            v_activity =loanjson[i]['activity'].encode('ascii','ignore')
        
            if(loanjson[i]['bonus_credit_eligibility']==False):
                v_bonus_credit_eligibility = 0
            else:
                v_bonus_credit_eligibility=1
    
            #borrower info
            v_borrowers_first_name = loanjson[i]['borrowers'][0]['first_name'].encode('ascii','ignore')
            v_borrowers_gender = loanjson[i]['borrowers'][0]['gender'].encode('ascii','ignore')
            v_borrowers_last_name = loanjson[i]['borrowers'][0]['last_name'].encode('ascii','ignore')
            if ( loanjson[i]['borrowers'][0]['pictured'] == False ):
                v_borrowers_pictured = 0
            else:
                v_borrowers_pictured = 1
        
            #Description info
            v_description_num_languages = len(loanjson[i]['description']['languages'])

            #remove these for now because they are giving me an encoding error. Have to decide how to use this anyway.
            #v_description_text_en = loanjson[i]['description']['texts']['en'].encode('utf-8','ignore')

            v_funded_amount = loanjson[i]['funded_amount']
        
            if loanjson[i]['funded_date'] == None:
                v_funded_date = '0-0-0 0:0:0'
            else:
                v_funded_date = dateutil.parser.parse(loanjson[i]['funded_date']).strftime('%Y-%m-%d %H:%M:%S')

            v_loan_id = loanjson[i]['id']

            v_image_id = loanjson[i]['image']['id']
            v_image_template_id = loanjson[i]['image']['template_id']


            v_journal_totals_bulkEntries = loanjson[i]['journal_totals']['bulkEntries']
            v_journal_totals_entries = loanjson[i]['journal_totals']['entries']

            v_lender_count  = loanjson[i]['lender_count']
                                 
            v_loan_amount = loanjson[i]['loan_amount']
                                 
            v_location_country = loanjson[i]['location']['country'].encode('ascii','ignore')
            v_location_geo = loanjson[i]['location']['geo']

            if loanjson[i]['location']['town'] == None:
                v_location_town = ''
            else:
                v_location_town = loanjson[i]['location']['town'].encode('ascii','ignore')
                                 
            v_name = loanjson[i]['name'].encode('ascii','ignore')
            v_partner_id = loanjson[i]['partner_id']

            if loanjson[i]['planned_expiration_date'] == None:
                v_planned_expiration_date = '0-0-0 0:0:0'
            else:
                v_planned_expiration_date = dateutil.parser.parse(loanjson[i]['planned_expiration_date']).strftime('%Y-%m-%d %H:%M:%S')

            if loanjson[i]['planned_expiration_date'] == None:
                v_posted_date = '0-0-0 0:0:0'
            else:
                v_posted_date = dateutil.parser.parse(loanjson[i]['posted_date']).strftime('%Y-%m-%d %H:%M:%S')


            v_sector = loanjson[i]['sector'].encode('ascii','ignore')
            v_status = loanjson[i]['status'].encode('ascii','ignore')

            v_terms_loss_liability_currency_exchange = loanjson[i]['terms']['loss_liability']['currency_exchange'].encode('ascii','ignore')
            v_terms_loss_liability_nonpayment = loanjson[i]['terms']['loss_liability']['nonpayment'].encode('ascii','ignore')


            if loanjson[i]['terms']['repayment_interval'] == None:
                v_terms_repayment_interval = ''
            else:
                v_terms_repayment_interval = loanjson[i]['terms']['repayment_interval'].encode('ascii','ignore')

            v_terms_repayment_term = loanjson[i]['terms']['repayment_term']
            
            v_location_country_code=loanjson[i]['location']['country_code'].encode('ascii','ignore')
            

            try:
                cur.execute('INSERT INTO Loans(activity, bonus_credit_eligibility, borrowers_first_name, borrowers_gender, borrowers_last_name, borrowers_pictured, description_num_languages,funded_amount, funded_date, loan_id, image_id,image_template_id, journal_totals_bulkEntries, journal_totals_entries,lender_count,loan_amount, location_country,location_geo,location_town,name,partner_id, planned_expiration_date, posted_date, sector, status,terms_loss_liability_currency_exchange,terms_loss_liability_nonpayment,terms_repayment_interval,terms_repayment_term,location_country_code) \
                    VALUES("%s", "%d","%s","%s","%s","%d","%d","%d","%s","%d","%d","%d","%d","%d","%d","%d", "%s","%s","%s","%s","%d","%s","%s","%s","%s","%s","%s","%s","%d","%s")' % \
                        (v_activity, v_bonus_credit_eligibility, v_borrowers_first_name, v_borrowers_gender, v_borrowers_last_name, v_borrowers_pictured, v_description_num_languages,v_funded_amount, v_funded_date, v_loan_id, v_image_id,v_image_template_id, v_journal_totals_bulkEntries, v_journal_totals_entries,v_lender_count,v_loan_amount, v_location_country,v_location_geo,v_location_town,v_name,v_partner_id, v_planned_expiration_date, v_posted_date, v_sector, v_status,v_terms_loss_liability_currency_exchange,v_terms_loss_liability_nonpayment,v_terms_repayment_interval,v_terms_repayment_term,v_location_country_code))
            except:
                continue


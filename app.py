import sqlite3
import flask

app = flask.Flask(__name__)
  

def get_db():
    db = sqlite3.connect('jpsalon.db')
    db.row_factory = sqlite3.Row
    return db

def ismember(memberid):
    db = get_db()
    row = get_db().execute("SELECT MemberID FROM Member WHERE MemberID = ?",(memberid,)).fetchone()
    if row != None:
        return True
    return False

def traverse(month):
    final = 0.0
    db = get_db()
    rows = get_db().execute("SELECT Date,TotalAmount FROM 'Transaction' ORDER BY Date ASC").fetchall()
    for row in rows:
        if (row[0])[5:7] == (month):
            final += float(row[1])
        if (row[0])[5:7] > (month):
            break
    return final

@app.route('/') 
def home():
    return flask.render_template('index.html')


@app.route('/addmember')
def addmember():
    return flask.render_template('addmember.html')

@app.route('/addedm', methods = ['POST'])
def addedm():
    n = flask.request.form['name']
    mID = flask.request.form['memberid']
    g = flask.request.form['gender']
    e = flask.request.form['email']
    mn = flask.request.form['mobileno']
    a = flask.request.form['address']
    
    db = get_db()
    db.execute('INSERT into Member (MemberID, Name, Gender, Email, MobileNumber, Address) VALUES (?,?,?,?,?,?)',(mID,n,g,e,mn,a))
    db.commit()
    db.close()
    return flask.render_template('memberadded.html',n=n,mID=mID)

@app.route('/updateMemberEandMN')
def updateMemberEandMN():
    return flask.render_template('updateMemberEandMN.html')

@app.route('/update', methods = ['POST'])
def update():
    mID = flask.request.form['memberid']
    newE = flask.request.form['newemail']
    newM = flask.request.form['newmobile']
    
    if ismember(mID) == True:
        db = get_db()
        db.execute('UPDATE Member SET Email = ? WHERE MemberID = ?',(newE,mID))
        db.commit()
        db.execute('UPDATE Member SET MobileNumber = ? WHERE MemberID = ?',(newM,mID))
        db.commit()
        db.close()
        return flask.render_template('memberUpdated.html', newE=newE, mID=mID, newM=newM)
    
    else:
        return flask.render_template('noUpdate.html', mID=mID)
    

@app.route('/addtransaction')
def addtransaction():
    return flask.render_template('addtransaction.html')

@app.route('/addedt', methods = ['POST'])
def addedt():
    iID = flask.request.form['invoiceid']
    date = flask.request.form['date']
    n = flask.request.form['name']
    mID = flask.request.form['memberid']
    ts = flask.request.form['typeservice']
    disc = 0.0
    totalamount = 0.0

    db = get_db()
    rows = get_db().execute("SELECT PriceService FROM Service WHERE TypeService = ?",(ts,)).fetchall()
    for row in rows:
        totalamount += row[0]
        
    if ismember(mID) == True:
        disc = 10/100 * totalamount
        totalamount -= disc
    
    db.execute("INSERT into 'Transaction' (InvoiceID, Date, Name, MemberID, TotalAmount) VALUES (?,?,?,?,?)",(iID,date,n,mID,totalamount))
    db.commit()
    db.execute("INSERT into 'TransactionDetails' (InvoiceID, TypeService) VALUES (?,?)",(iID,ts))
    db.commit()
    db.close()
    return flask.render_template('transactionadded.html',iID=iID,n=n,mID=mID,date=date,ts=ts,totalamount=totalamount,disc=disc)

@app.route('/viewDailyTransaction')
def viewDailyTransaction():
    db = get_db()
    rows = get_db().execute("SELECT * FROM 'Transaction' ORDER BY Date ASC").fetchall()
    invoiceIDlst = []
    datelst = []
    namelst = []
    memberIDlst = []
    totallst = []
    
    for row in rows:
        invoiceIDlst.append(row[0])
        datelst.append(row[1])
        namelst.append(row[2])
        memberIDlst.append(row[3])
        totallst.append(row[4]) 
    
    return flask.render_template('viewDailyTransaction.html', invoiceIDlst=invoiceIDlst, datelst=datelst, namelst=namelst, memberIDlst=memberIDlst, totallst=totallst)

@app.route('/viewmonthlysalesrev')
def viewmonthlysalesrev():
    monthlysr = []
    for i in range(1,13):
        if i < 10:
            amount = traverse(f"0{i}")
        else:
            amount = traverse(str(i))
        monthlysr.append(amount)
    
    return flask.render_template('viewmonthlysalesrev.html', monthlysr=monthlysr)


@app.route('/viewMemberTransHistory')
def viewMemberTransHistory():
    return flask.render_template('viewMemberTransHistory.html')

@app.route('/viewh', methods = ['POST'])
def viewh():
    n = flask.request.form['name']
    mID = flask.request.form['memberid']
    
    if ismember(mID) == True:
        db = get_db()
        count = get_db().execute("SELECT COUNT(*) FROM 'Transaction' WHERE MemberID = ?", (mID,)).fetchone()

        if count[0] > 0:
            db = get_db()
            rows = get_db().execute("SELECT InvoiceID, Date, TotalAmount FROM 'Transaction' WHERE MemberID = ?", (mID,)).fetchall()
            invoiceIDlst = []
            datelst = []
            totallst = []
            for row in rows:
                invoiceIDlst.append(row[0])
                datelst.append(row[1])
                totallst.append(row[2])
                
            return flask.render_template("viewMemberHistory.html", invoiceIDlst=invoiceIDlst, datelst=datelst, totallst=totallst)

        else:
            return flask.render_template("noHistory.html", n=n, mID=mID)
    else:
        return flask.render_template('viewMemberTransHistory.html')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)








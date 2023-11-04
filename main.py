from flask import Flask,render_template, request, jsonify
import math
import time
from datetime import date
from datetime import datetime
from cs50 import SQL
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad

#charset_1=lat
#charset_22=long


app = Flask(__name__,template_folder="templates")

db = SQL("sqlite:///working.db")
def decrypt(enc,key,iv):
        enc = base64.b64decode(enc)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc),16)


key = 'AAAAAAAAAAAAAAAA'
iv =  'BBBBBBBBBBBBBBBB'.encode('utf-8')

def day_calc(date1, date2):
    # Assume date2 > date1 using date_function

    day1 = int(date1[0:2])
    month1 = int(date1[2:4])
    year1 = int(date1[4:8])

    day2 = int(date2[0:2])
    month2 = int(date2[2:4])
    year2 = int(date2[4:8])

    date_a = date(year1, month1, day1)
    date_b = date(year2, month2, day2)
    delta = date_b - date_a

    return delta.days

@app.route("/")
def hello():
    today = str(time.strftime("%d%m%Y"))
    dates = db.execute("SELECT date FROM data GROUP BY date")

    for day in dates:
        day = day['date']
        if day == None:
            break
        else:
            if day_calc(day, today) > 2:
                db.execute("DELETE FROM data WHERE date = (?)", day)

    table_data = db.execute("SELECT * FROM data WHERE date = (?) ORDER BY book_time DESC", today)

    return render_template('index.html', today=today, table_data=table_data)



@app.route('/process', methods=['POST'])

def process():
    data = request.get_json() # retrieve the data sent from JavaScript
    # process the data using Python code
    lat=data['lat1']
    long=data['long1']
    decrypt_lat=decrypt(enc=lat,key=key,iv=iv)
    decrypt_long=decrypt(enc=long,key=key,iv=iv)
    my_lat = float(decrypt_lat.decode("utf-8", "ignore"))
    my_long =float(decrypt_long.decode("utf-8", "ignore"))
    iti_lat = 1.33948
    iti_long = 103.68446

    x = (my_lat - iti_lat)**2
    y = (my_long - iti_long)**2
    dist = math.sqrt(x+y)

    if dist > 0.004:
        result = "Not in camp"
    else:
        today = str(time.strftime("%d%m%Y"))
        now = time.strftime("%H:%M:%S")
        name = str(data['trp'])
        ip = str(data['ip'])

        check_data = db.execute("SELECT user, ip FROM data")

        if check_data != []:
            for x in check_data:
                if str(x['ip']) == str(ip):
                    result = "Form already submitted"

                elif str(x['user']) == str(name):
                    result = "Form already submitted"

                else:
                    db.execute("INSERT INTO data (user, book_time, date, ip) VALUES ((?), (?), (?), (?))", name, now, today, ip)
                    result = "Success"

        else:
            db.execute("INSERT INTO data (user, book_time, date, ip) VALUES ((?), (?), (?), (?))", name, now, today, ip)
            result = "Success"



    return jsonify(result=result)




if __name__ == '__main__':
    app.run(debug=True)

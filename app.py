from flask import Flask, request, jsonify, render_template, redirect, url_for, session, abort
from flask_cors import CORS
import requests as r, pymysql, random, string

app = Flask(__name__)
CORS(app)
app.secret_key = 'wino'

def create_connection():
    connection = None                                                                                                                            
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="dbsk",
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.Error as e:
        print(f'Error: {e}')
    return connection

def chcek_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='dbsk'
    )
    return connection

def check_sk(sk):
    connection = chcek_connection()
    cursor = connection.cursor()
    
    try:
        # Ambil kolom sk jika ada, bukan menggunakan COUNT(*)
        query = "SELECT sk FROM data WHERE sk = %s"
        cursor.execute(query, (sk,))
        result = cursor.fetchone()
        
        # Jika result ditemukan, kembalikan nilai sk dari database
        if result:
            return result[0]  # Kembalikan nilai sk
        else:
            return None  # Tidak ada sk yang cocok di database
    except Exception as e:
        print("Terjadi kesalahan:", e)
        return None
    finally:
        cursor.close()
        connection.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cek')
def cek():
    return render_template('check.html')

@app.route('/regis')
def regis():
    return render_template('regis.html')

@app.route('/admin')
def ad():
    return render_template('loginadmin.html')

@app.route('/loginadmin')
def display():
    sk = session.get('admin')
    status = check_sk(sk)
    if status == 'moldova2022':
        connection = create_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM data"
        cursor.execute(query)
        data = cursor.fetchall()
        connection.close()
        return render_template('admin.html', data=data)
    else:
        abort(403)

@app.route('/ceker', methods=['GET', 'POST'])
def ceker():
    if request.method == 'POST':
        sk = request.form['sk']
        status = check_sk(sk)
        if status == "moldova2022":
            session['admin'] = sk
            return jsonify({'success': True, 'message': 'Succesfully Login'})
        else:
            print(status)
            return jsonify({'success': False, 'message': 'SK Not Register'})
    return render_template('index.html')

@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    if request.method == 'POST':
        nama = request.form['nama']
        entry = request.form['entry']
        exp = request.form['exp']
        hex_chars = string.hexdigits.lower()
        sk = ''.join(random.choice(hex_chars) for _ in range(8))
        
        connection = create_connection()
        cursor = connection.cursor()
        query = "INSERT INTO data (sk, nama, entry_date, exp_date) VALUES(%s, %s, %s, %s)"
        values = (sk, nama, entry, exp)
        cursor.execute(query, values)
        connection.commit()
    
    return render_template('adduser.html')

@app.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit(id):
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM data WHERE sk = %s" 
    cursor.execute(query, (id,))
    data = cursor.fetchone()
    
    if request.method == 'POST':
        nama = request.form['nama']
        entry = request.form['entry']
        exp = request.form['exp']
        
        query = "UPDATE data SET nama = %s, entry_date = %s, exp_date = %s WHERE sk = %s"
        cursor.execute(query, (nama, entry, exp, id))
        connection.commit()
        connection.close()
        
        return redirect(url_for('display'))
    
    connection.close()
    return render_template('edit.html', data=data)

@app.route('/delete/<string:id>')
def delete(id):
    connection = create_connection()
    cursor = connection.cursor()
    query = "DELETE FROM data WHERE sk = %s" 
    cursor.execute(query, (id,))
    connection.commit()
    connection.close()
    
    return redirect(url_for('display'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        sk = request.form['sk']
        status = check_sk(sk)
        if status == sk:
            session['sk'] = sk
            return jsonify({'success': True, 'message': 'Succesfully Login'})
        else:
            print(status)
            return jsonify({'success': False, 'message': 'SK Not Register'})
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add():
    sk = session.get('sk')
    status = check_sk(sk)
    if status == True:
        if request.method == 'POST':
            fn = request.form['fn']
            ln = request.form['ln']
            pw = request.form['pw']
            no = request.form['no']
            session['fn'] = fn
            session['ln'] = ln
            session['pw'] = pw
            session['no'] = no

            head = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            }
            payload = {
                "acceptOffer": False,
                "acceptTerm": True,
                "firstName": fn,
                "lastName": ln,
                "password": pw,
                "phone": no
            }

            try:
                res = r.post('https://familymoo.com/rest/api/auth/register', headers=head, json=payload)
                data = res.json()
                if data['success'] == True:
                    print("OTP Succesfully Send")
                    return jsonify({'success': True, 'message': 'OTP Succesfully Send'})
                elif data['code'] == 42:
                    print('Nomor Telah Terdaftar')
                    return jsonify({'success': False, 'message': 'Nomor Telah Terdaftar'})
                elif data['data']['fields']['phone']:
                    print('Nomor Telah Terdaftar')
                    return jsonify({'success': False, 'message': 'Nomor Telah Terdaftar'})
                else:
                    print("Failed Send OTP")
                    return jsonify({'success': False, 'message': 'Failed Send OTP'})
                
            except ValueError:
                print("Invalid response from server")
                return jsonify({'success': False, 'message': 'Invalid response from server'})

            except Exception as e:
                print(f"Error: {e}")
                return jsonify({'success': False, 'message': 'Nomor Telah Terdaftar'})
        return render_template('regis.html')
    else:
        abort(403)

@app.route('/otp', methods=['GET', 'POST'])
def otp():
    no = session.get('no')
    sk = session.get('sk')
    status = check_sk(sk)
    if status == True:
        if request.method == 'POST':
            otpp = request.form['otp']

            head = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            }
            data = {
                "otp": otpp,
                "phone": no
            }
            try:
                res = r.post('https://familymoo.com/rest/api/auth/confirmOtp/register', headers=head, json=data).json()
                if res['success'] == True:
                    print(f'Acces Token : {res['data']['accessToken']}')
                    session['ac'] = res['data']['accessToken']
                    return jsonify({'success': True, 'message': 'Account Succesfully Create'})
                else:
                    print('Failed Register')
                    return jsonify({'success': False, 'message': 'Invalid response from server'})
            
            except ValueError:
                print("Invalid response from server")
                return jsonify({'success': False, 'message': 'Invalid response from server'})

            except Exception as e:
                print(f"Error: {e}")
                return jsonify({'success': False, 'message': 'OTP Wrong Input'})
    
        return render_template('otp.html')
    else:
        abort(403)
    

@app.route('/reedem', methods=['GET', 'POST'])
def reedem():
    fn = session.get('fn')
    ln = session.get('ln')
    pw = session.get('pw')
    no = session.get('no')
    ac = session.get('ac')
    sk = session.get('sk')
    status = check_sk(sk)
    if status == True:
        if request.method == 'POST':
            ch = request.form['ch']

            head = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "authorization": f"Bearer {ac}"
            }
            data = {
                "balance": "coupon",
                "couponName": ch,
                "qty": 1
            }
            try:
                res = r.post('https://familymoo.com/rest/api/redempt', headers=head, json=data)
                payload = res.json()
                if payload['success'] == True:
                    print("Sukkes Redeem")
                    print(f'Message : {payload['data']['message']}')
                    print(f'RedemptioId : {payload['data']['redemptionId']}')
                    rid = payload['data']['redemptionId']
                    with open('akun.txt', 'a') as a:
                        a.write(f'{fn} | {ln} | {pw} | {no} | {ac} | {rid}\n')
                    return jsonify({'success': True, 'message': 'Coupon Succesfully Reedem'})
                else:
                    print('Failed Redeem')
                    return jsonify({'success': False, 'message': 'Coupon Failed Reedem'})
            
            except ValueError:
                print("Invalid response from server")
                return jsonify({'success': False, 'message': 'Invalid response from server'})

            except Exception as e:
                print(f"Error: {e}")
                return jsonify({'success': False, 'message': 'Gagal Tukar Kupon'})
        return render_template('reedem.html')
    else:
        abort(403)

@app.route('/kupon', methods=['GET', 'POST'])
def kupon():
    data = []
    if request.method == 'POST':
        try:
            head = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            }
            payload = {
                "password": "Moldova2022",
                "phone": "089618331292"
            }
            res = r.post("https://familymoo.com/rest/api/auth/login", headers=head, json=payload).json()
            if res['success']:
                ac = res['data']['accessToken']
                
            header = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "authorization": f"Bearer {ac}"
            }
            response = r.get("https://familymoo.com/rest/api/coupons", headers=header).json()
            if response['success']:
                for coupon in response["data"]["coupons"]:
                    data.append({'nama': coupon['name'], 'jumlah': coupon['available']})
                return jsonify({'success': True, 'message': 'Berhasil Cek Kupon', 'data': data})
            
        except ValueError:
            print("Invalid response from server")
            return jsonify({'success': False, 'message': 'Invalid response from server'})

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'message': 'Gagal Cek Kupon'})

        return render_template('check.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
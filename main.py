from flask import Flask, redirect, url_for, request, render_template
import random
from datetime import datetime
import sqlite3
import yfinance as yf

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')


def retrieve():
    conn = sqlite3.connect('records.db')
    cursor = conn.cursor()
    data = cursor.execute('''SELECT * FROM (SELECT * FROM RECORDS ORDER BY TIMESTAMP DESC LIMIT 15)''')
    desc = cursor.description
    column_names = [col[0] for col in desc]
    final_data = []
    for row in data:
        process = []
        for i in range(len(row)):
            tuplee = (column_names[i], row[i])
            print(tuplee)
            process.append(tuplee)
        final_data.append(dict(process))

    account_balance = {'bank_account_eur': 0,
                       'cash_eur': 0,
                       'bank_account_rub': 0,
                       'exchange_rate_eurrub': yf.Ticker('EURRUB=X').history()['Close'].iloc[-1].round(2),
                       'rub_eur': 0,
                       'total': 0}
    for dict_ in final_data:
        if dict_['SOURCE'] == 'bank_account_eur':
            account_balance['bank_account_eur'] += dict_["AMOUNT"]
        if dict_['SOURCE'] == 'cash_eur':
            account_balance['cash_eur'] += dict_["AMOUNT"]
        if dict_['SOURCE'] == 'bank_account_rub':
            account_balance['bank_account_rub'] += dict_["AMOUNT"]
        account_balance['rub_eur'] = account_balance['bank_account_rub'] / account_balance['exchange_rate_eurrub']
        account_balance['rub_eur'] = account_balance['rub_eur'].round(3)
        account_balance['total'] = account_balance["bank_account_eur"] + account_balance['cash_eur'] + account_balance[
            'rub_eur']
    return final_data, account_balance


@app.route('/')
def success():
    call = retrieve()
    return render_template('index.html', records=call[0], balances=call[1])


@app.route('/add_record', methods=['POST', 'GET'])
def add_record():
    if request.method == 'POST':
        conn = sqlite3.connect('records.db')
        cursor = conn.cursor()
        data = cursor.execute('''SELECT * FROM RECORDS''')
        for row in data:
            print(row)
        # table = """CREATE TABLE RECORDS(ID VARCHAR(255),NAME VARCHAR(255), AMOUNT FLOAT(24),
        # CURRENCY VARCHAR(255), CATEGORY VARCHAR(255), TYPE VARCHAR(255), SOURCE VARCHAR(255), DAY VARCHAR(255),
        # MONTH VARCHAR(255), YEAR VARCHAR(255), TIMESTAMP VARCHAR(255));"""
        # cursor.execute(table)

        name = request.form['name']
        amount = request.form['amount']
        currency = request.form['currency']
        category = request.form['category']
        type_ = request.form['type']
        source = request.form['source']
        day = datetime.now().day
        month = datetime.now().strftime('%B')
        year = datetime.now().year
        id_ = str(random.randint(1, 100000000000000000))
        timestamp = str(datetime.now().timestamp())
        if type_ == 'expense':
            amount = float(amount)
            amount = 0 - amount
            amount = str(amount)

        params = (id_, name, amount, currency, category, type_, source, day, month, year, timestamp)
        cursor.execute(
            f'''INSERT INTO RECORDS VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)''', params)
        data = cursor.execute('''SELECT * FROM RECORDS''')
        for row in data:
            print(row)
        conn.commit()
        conn.close()

        return redirect('/')

    else:
        return 404


@app.route('/delete_record', methods=['POST', 'GET'])
def delete_record():
    if request.method == 'GET':
        id_ = request.args.get('id')
        print(id_)
        conn = sqlite3.connect('records.db')
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM RECORDS WHERE ID={id_}')

        data = cursor.execute('''SELECT * FROM RECORDS''')
        for row in data:
            print(row)
        conn.commit()
        conn.close()

        return render_template('index.html', records=retrieve())

    else:
        return 404


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))

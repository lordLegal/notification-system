from flask import Flask, url_for, send_from_directory, render_template, jsonify, redirect, flash, request
import flask_login
import psycopg2
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'SECRET'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

users = {'foo@bar.tld': {'password': 'secret', 'tabelnumber': '1'}}

con = psycopg2.connect(database='secure', user="postgres",
                       password="")

cur = con.cursor()
print(con, cur)


class database():

    def dates():
        cur.execute("SELECT * FROM dates;")
        dates = cur.fetchall()
        con.commit()
        return dates

    def next_date():
        cur.execute(f"SELECT date FROM dates;")
        all_dates = cur.fetchall()
        if all_dates == []:
            return []
        date_list = []
        for num, value in enumerate(all_dates):
            value = value[0]
            time = str(value).split(',')[0]
            date = str(value).split(',')[-1]
            hour = int(time.split(':')[0])
            min_ = int(time.split(':')[-1])
            year = int(date.split('-')[0])
            month = int(date.split('-')[1])
            day = int(date.split('-')[2])
            date_list.append(datetime(year, month, day, hour, min_))
        date_now_ = datetime.now()
        year_now, month_now, day_now, h_now, min_now = date_now_.year, date_now_.month, date_now_.day, date_now_.hour, date_now_.minute
        date_now = datetime(year_now, month_now, day_now, h_now, min_now)
        res = min(date_list, key=lambda sub: abs(sub - date_now))
        date_res = str(res).split(' ')[0]
        time_res = (str(res).split(' ')[1]).split(':')[
            0] + ":" + (str(res).split(' ')[1]).split(':')[1]
        search_date = time_res + "," + date_res
        cur.execute(
            f"SELECT * FROM dates WHERE date LIKE '{search_date}';")
        return cur.fetchall()

    def update(table=str, set=str, where=str):
        """
        database.update(table="dates", set="date = '15:11,2021-07-07', header = 'Birthday'", where="date='15:11,2021-07-07'")
        """
        cur.execute(f"UPDATE {table} SET {set} WHERE {where};")

    def delete_insert(table=None, where=None):
        """
        database.delete_insert(table="dates", where="header=Birtday")
        """
        cur.execute(f"DELETE FROM {table} WHERE {where};")
        con.commit()
        return

    def delete_allinserts(table=None):
        """
        database.delete_allinserts(table="dates")
        """
        cur.execute(f"DELETE FROM {table};")
        con.commit()
        return

    def add_insert():
        pass

    def create_table(con, name):
        """create a databse with the name and the con"""
        pass

    def delete_table():
        pass

    def get_tables():
        cur.execute(
            f"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cur.fetchall()
        con.commit()
        return tables


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(requests):
    email = requests.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = requests.form['password'] == users[email]['password']

    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    if request.form['password'] == users[email]['password'] and request.form['tabelnumber'] == users[email]['tabelnumber']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return redirect(url_for('home'))

    return 'Bad login'


@app.route('/api')
@flask_login.login_required
def api():
    if request.method == 'POST':
        pass
    pass


@app.route('/', methods=['GET', 'POST'])
@flask_login.login_required
def home():
    if request.method == 'POST':
        type = request.form['type']
        if type == 'insert':
            table, time, date, title, text = request.form['table_selection'], request.form[
                'time'], request.form['date'], request.form['title'], request.form['text']
            insert_date = time + "," + date
            cur.execute(
                f"INSERT INTO {table} (date, header, content) VALUES ('{insert_date}', '{title}', '{text}')")
            database.add_insert()
        if type == 'delete':
            header, content, date_ = request.form['header'], request.form['content'], request.form['date']
            database.delete_insert(
                table='dates', where=f"content='{content}' AND header='{header}' AND date='{date_}'")
        if type == 'update':
            header, content, date_, new_header, new_content, new_date_ = request.form['header'], request.form[
                'content'], request.form['date'], request.form['new_header'], request.form['new_content'], request.form['new_date']
            database.update(
                table='dates', set=f"header='{new_header}', content='{new_content}', date='{new_date_}' ", where=f"content='{content}' AND header='{header}' AND date='{date_}'")
        if type == 'return_update':
            dates = database.dates()
            tables = database.get_tables()
            next_date = database.next_date()
            len_next_date = len(next_date)
            header, content, date_ = request.form['header'], request.form['content'], request.form['date']
            return render_template('dit_index.html', header=header, content=content, date_=date_, len_tables=len(tables), tabels=tables[0], table=dates, len_table=len(dates), next_date=next_date, len_next_date=len_next_date)

    dates = database.dates()
    tables = database.get_tables()
    next_date = database.next_date()
    len_next_date = len(next_date)

    return render_template('index.html', len_tables=len(tables), tabels=tables[0], table=dates, len_table=len(dates), next_date=next_date, len_next_date=len_next_date)


@ app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))


@ login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True, load_dotenv=True)

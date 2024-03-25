from flask import Flask, render_template, request, redirect, session
from database import db_blueprint, get_all_parts, insert_part
from flask import request, redirect, url_for
from flask import jsonify # used for converting database into JSON file


app = Flask(__name__)
app.register_blueprint(db_blueprint)
app.secret_key = 'your_secret_key'

#Temporary User Dictionary
USER_CREDENTIALS = {
    'admin': 'password',
    'user1': '123456'
}

#Authenticates User Creds
def authenticate_user(username, password):
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        return True
    return False

#The Routes
@app.route('/')
def index():
    return render_template('index.html')

# AJAX route to fetch parts data
@app.route('/get_parts', methods=['POST'])
def get_parts():
    search_type = request.form.get('searchType', None)
    parts = get_all_parts(search_type)
    parts_list = [dict(part) for part in parts]  # Convert rows to dicts for JSON response
    return jsonify(parts_list)

# AJAX route to add part using test data
@app.route('/add_part', methods=['POST'])
def add_part():
    data = request.form
    try:
        # There's a function in database.py to insert a part
        insert_part(data['Type'], data['Capacity'], data['Size'], data['Speed'],
                    data['Brand'], data['Model'], data['Location'], data['SN'])
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500




# Login
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            session['username'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', message = 'Invalid username or password')
    return render_template('login.html')

@app.route('/dashboard')
def pc_parts():
    parts = get_all_parts()
    return render_template('search_results.html', parts=parts)

@app.route('/search')
def search():
    search_type = request.args.get('type', '')
    parts = get_all_parts(search_type)
    return render_template('search_results.html', parts=parts, search_type=search_type)

@app.route('/checkout', methods=['POST'])
def checkout():
    serial_number = request.form['serial_number']
    checkout_part(serial_number)  
    return redirect(url_for('pc_parts')) #need to change this for it to go to out panel instead of out it by itself

@app.route('/checkin', methods=['POST'])
def checkin():
    serial_number = request.form['serial_number']
    part_type = request.form['part_type']
    brand = request.form['brand']
    shelf_location = request.form['shelf_location']
    checked_out = request.form['checked_out']
    checkin_part(serial_number, part_type, brand, shelf_location, checked_out)
    return redirect(url_for('pc_parts'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)

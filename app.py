from flask import Flask, render_template, url_for, request
from database import init_db, db

# Serve the project's asset files located under templates/assets at the URL path /assets
app = Flask(__name__, static_folder='templates/assets', static_url_path='/assets')

# Initialize DB
init_db(app)


@app.route('/')
def home():
    return render_template('index.html', title='Home')


@app.route('/car-list')
def car_list():
    # Fetch a simple list of vehicles from the existing SQLite DB
    vehicles = []
    try:
        result = db.session.execute("SELECT idVehicle, model, dailyRate, imageUrl FROM Vehicle").fetchall()
        for row in result:
            vehicles.append({
                'id': row[0],
                'model': row[1],
                'dailyRate': row[2],
                'imageUrl': row[3]
            })
    except Exception:
        vehicles = []
    return render_template('car-list.html', title='Car List', vehicles=vehicles)


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')


@app.route('/login')
def login():
    return render_template('login.html', title='Login')


@app.route('/register')
def register():
    return render_template('register.html', title='Register')


@app.route('/reservation')
def reservation():
    # Optionally accept a vehicle_id query parameter
    vehicle_id = request.args.get('vehicle_id')
    return render_template('reservation.html', title='Reservation', vehicle_id=vehicle_id)


if __name__ == '__main__':
    app.run(debug=True)

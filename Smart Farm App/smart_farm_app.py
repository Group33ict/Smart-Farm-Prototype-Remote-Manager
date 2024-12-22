from flask import Flask, jsonify, request, render_template, url_for, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from datetime import datetime
import pytz
from flask_cors import CORS
import json
import os
from Template import request_message as rq


app = Flask(__name__)
CORS(app)


# Unified Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/smart_farm_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecretkey'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)  # Initialize JWT Manager


# Login Manager Setup (Although we are using JWT, we still need this for user-related features like logout)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# User Authentication Models and Forms
@login_manager.user_loader # Call back user objects from the user ID
def load_user(user_id):
    return User.query.get(int(user_id))


# User Data model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


# Flask WTForms
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        # Query the database, check if the entered username is already existed in the database
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one.')


# Flask WTForms
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')


def gmt7_now():
    return datetime.now(pytz.timezone('Asia/Bangkok'))


# Smart Farm Data Model
class SmartFarmData(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    updated_time = db.Column(db.DateTime, default=gmt7_now)
    temperature = db.Column(db.String(50), nullable=True)
    humidity = db.Column(db.String(50), nullable=True)
    co2 = db.Column(db.String(50), nullable=True)
    light_intensity = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(50), nullable=True)


# Plant Data Model
class PlantData(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.DateTime, default=gmt7_now)
    species = db.Column(db.String(50), nullable=True)
    optimal_temperature = db.Column(db.String(50), nullable=True)
    optimal_humidity = db.Column(db.String(50), nullable=True)
    optimal_co2 = db.Column(db.String(50), nullable=True)
    optimal_light_intensity = db.Column(db.String(50), nullable=True)
    optimal_color = db.Column(db.String(50), nullable=True)


# Set up database function
def setup_database():
    """Initializes the database."""
    with app.app_context():
        db.create_all()   
        

# Control single parameter in Smart Farm function
def update_parameter(parameter_name, value):
    """Update a specific parameter and insert a new row."""
    # Check if the parameter is valid
    valid_parameters = {"temperature", "humidity", "co2", "light_intensity", "color"}
    if parameter_name not in valid_parameters:
        return {
            "status": "error",
            "message": f"Invalid parameter: {parameter_name}. Valid parameters are: {', '.join(valid_parameters)}."
        }, 400

    # Retrieve the latest record
    latest_entry = SmartFarmData.query.order_by(SmartFarmData.updated_time.desc()).first()

    # If no records exist, return an error
    if not latest_entry:
        return {
            "status": "error",
            "message": "No data available to update. Please initialize the database first."
        }, 400

    # Create a new row with updated parameter
    new_entry = SmartFarmData(
        temperature=latest_entry.temperature if parameter_name != "temperature" else value,
        humidity=latest_entry.humidity if parameter_name != "humidity" else value,
        co2=latest_entry.co2 if parameter_name != "co2" else value,
        light_intensity=latest_entry.light_intensity if parameter_name != "light_intensity" else value,
        color=latest_entry.color if parameter_name != "color" else value
    )

    db.session.add(new_entry)
    db.session.commit()

    # Prepare the response
    response = {
        "status": "success",
        "message": f"Parameter '{parameter_name}' updated successfully.",
        "data": {
            "updated_time": new_entry.updated_time,
            "temperature": new_entry.temperature,
            "humidity": new_entry.humidity,
            "co2": new_entry.co2,
            "light_intensity": new_entry.light_intensity,
            "color": new_entry.color,
        }
    }
    return response, 200


# Send request messages to Message broker functions

def request_wifi_change():
    """Send a request message to the message broker to change Wi-Fi credentials, including the conf.json file contents."""
    # Get the absolute path to the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    conf_file_path = os.path.join(script_dir, "conf.json")

    # Check if the conf.json file exists
    if not os.path.exists(conf_file_path):
        return {
            "status": "error",
            "message": "conf.json file not found."
        }, 404

    # Read Wi-Fi credentials from the conf.json file
    try:
        with open(conf_file_path, "r") as conf_file:
            wifi_credentials = json.load(conf_file)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to read conf.json: {str(e)}"
        }, 500

    # Prepare the message for the message broker
    msg = {
        "action": "request_wifi_change",
        "wifi_credentials": wifi_credentials  # Include the file's contents
    }

    # Send the message to the message broker
    try:
        rq.sf_send(topic="change_wifi", msg=msg)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to send message to the message broker: {str(e)}"
        }, 500

    return {
        "status": "success",
        "message": "Wi-Fi change request sent successfully, including conf.json contents."
    }, 200





# Receive request messages from Message broker functions


# JWT Authentication API routes

@app.route('/')
def home():
    response = {
        "status": "success",
        "message": "Welcome to the Home Page."
    }
    return jsonify(response)


@app.route('/login', methods=['POST'])
def login():
    # Parse JSON data from the request body
    data = request.get_json()

    # Extract username and password from the parsed data
    username = data.get('username')
    password = data.get('password')

    # Check if both username and password are provided
    if not username or not password:
        return jsonify({
            "status": "error",
            "message": "Username and password are required."
        }), 400

    # Query the database for the user
    user = User.query.filter_by(username=username).first()

    # Verify the user's existence and password
    if user and bcrypt.check_password_hash(user.password, password):
        # Generate JWT token
        access_token = create_access_token(identity=user.username)
        login_user(user)

        return jsonify({
            "status": "success",
            "message": "Login successful.",
            "token": access_token
        }), 200

    # If authentication fails
    return jsonify({
        "status": "error",
        "message": "Invalid username or password."
    }), 401


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    response = {
        "status": "success",
        "message": "Welcome to the Dashboard."
    }
    return jsonify(response)


@app.route('/register', methods=['POST'])
def register():
    # Parse JSON data
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Validate username
        if not username or len(username) < 4 or len(username) > 20:
            return jsonify({"status": "error", "message": "Invalid username length."}), 400

        # Validate password
        if not password or len(password) < 8 or len(password) > 20:
            return jsonify({"status": "error", "message": "Invalid password length."}), 400

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"status": "error", "message": "Username already exists."}), 400

        # Hash the password and create a new user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"status": "success", "message": "Registration successful."}), 201

    return jsonify({"status": "error", "message": "Invalid request format."}), 400


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    # Create a response object with a success message
    response = jsonify({
        "status": "success",
        "message": "Logout successful."
    })
    # Unset the JWT cookies in the response
    unset_jwt_cookies(response)
    # Log out the user
    logout_user()
    return response, 200



# Smart Farm Data API Routes

@app.route('/data_retrieval', methods=['GET'])
@jwt_required() 
def data_retrieval():
    # Retrieve all Smart Farm data from the database
    all_data = SmartFarmData.query.order_by(SmartFarmData.updated_time.desc()).all()
    
    # Prepare the response
    response = {
        "status": "success",
        "data": [
            {
                "updated_time": item.updated_time.strftime("%Y-%m-%d %H:%M:%S") if item.updated_time else None,
                "temperature": item.temperature,
                "humidity": item.humidity,
                "co2": item.co2,
                "light_intensity": item.light_intensity,
                "color": item.color,
            } 
            for item in all_data
        ]
    }

    # Define the file path for exporting
    file_path = os.path.join(os.getcwd(), "smart_farm_data.json")

    # Write the response data to the JSON file
    try:
        with open(file_path, "w") as json_file:
            json.dump(response, json_file, indent=4)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to write to file: {str(e)}"
        }), 500
    
    return jsonify(response)


@app.route('/data_simulation', methods=['POST'])
@jwt_required()
def data_simulation():
    # Retrieve incoming data
    incoming_data = request.get_json()

    # Extract parameters
    temperature = incoming_data.get("temperature")
    humidity = incoming_data.get("humidity")
    co2 = incoming_data.get("co2")
    light_intensity = incoming_data.get("light_intensity")
    color = incoming_data.get("color")

    # Insert new row into the database
    new_entry = SmartFarmData(
        temperature=temperature,
        humidity=humidity,
        co2=co2,
        light_intensity=light_intensity,
        color=color
    )
    db.session.add(new_entry)
    db.session.commit()

    # Retrieve all data for response
    all_data = SmartFarmData.query.order_by(SmartFarmData.updated_time.desc()).all()
    response_data = [
        {
            "updated_time": item.updated_time,
            "temperature": item.temperature,
            "humidity": item.humidity,
            "co2": item.co2,
            "light_intensity": item.light_intensity,
            "color": item.color,
        }
        for item in all_data
    ]

    response = {
        "status": "success",
        "message": "Smart Farm data simulated successfully!",
        "data": response_data
    }
    return jsonify(response)


@app.route('/update_temperature', methods=['POST'])
@jwt_required()
def update_temperature():
    incoming_data = request.get_json()

    # Ensure the temperature key is present in the request
    if "temperature" not in incoming_data:
        return jsonify({
            "status": "error",
            "message": "Missing 'temperature' in request data."
        }), 400

    # Call the update_parameter function
    parameter_name = "temperature"
    value = incoming_data["temperature"]
    response, status_code = update_parameter(parameter_name, value)
    return jsonify(response), status_code


@app.route('/update_humidity', methods=['POST'])
@jwt_required()
def update_humidity():
    incoming_data = request.get_json()

    if "humidity" not in incoming_data:
        return jsonify({
            "status": "error",
            "message": "Missing 'humidity' in request data."
        }), 400

    parameter_name = "humidity"
    value = incoming_data["humidity"]
    response, status_code = update_parameter(parameter_name, value)
    return jsonify(response), status_code


@app.route('/update_co2', methods=['POST'])
@jwt_required()
def update_co2():
    incoming_data = request.get_json()

    if "co2" not in incoming_data:
        return jsonify({
            "status": "error",
            "message": "Missing 'co2' in request data."
        }), 400

    parameter_name = "co2"
    value = incoming_data["co2"]
    response, status_code = update_parameter(parameter_name, value)
    return jsonify(response), status_code


@app.route('/update_light_intensity', methods=['POST'])
@jwt_required()
def update_light_intensity():
    incoming_data = request.get_json()

    if "light_intensity" not in incoming_data:
        return jsonify({
            "status": "error",
            "message": "Missing 'light_intensity' in request data."
        }), 400

    parameter_name = "light_intensity"
    value = incoming_data["light_intensity"]
    response, status_code = update_parameter(parameter_name, value)
    return jsonify(response), status_code


@app.route('/update_color', methods=['POST'])
@jwt_required()
def update_color():
    incoming_data = request.get_json()

    if "color" not in incoming_data:
        return jsonify({
            "status": "error",
            "message": "Missing 'color' in request data."
        }), 400

    parameter_name = "color"
    value = incoming_data["color"]
    response, status_code = update_parameter(parameter_name, value)
    return jsonify(response), status_code



# Message broker interactions API routes

@app.route('/request_wifi_change', methods=['POST'])
# @jwt_required()  # Uncomment to secure the route
def request_wifi_change_api():
    """API endpoint to request a Wi-Fi password change."""
    response, status_code = request_wifi_change()
    return jsonify(response), status_code



# Serve static file function
@app.route('/static/iot/templates/<path:path>')
def send_report(path):
    # Using request args for path will expose you to directory traversal attacks
    return send_from_directory('./static/iot/templates', path)



if __name__ == '__main__':
    setup_database()  # Initialize the database
    app.run(debug=True)
    
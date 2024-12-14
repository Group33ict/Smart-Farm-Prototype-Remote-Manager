from flask import Flask, jsonify, request, render_template, url_for, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies


app = Flask(__name__)


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


#User Data model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        # Query the database, check if the entered username is already existed in the database
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')


# Smart Farm Data Model
class SmartFarmData(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parameter = db.Column(db.String(50), nullable=False, unique=True)
    unit = db.Column(db.String(20), nullable=False)
    value = db.Column(db.String(50), nullable=True)


def setup_database():
    """Initializes the database and populates default values if the table is empty."""
    with app.app_context():
        db.create_all()
        if SmartFarmData.query.count() == 0:
            initial_data = [
                {"parameter": "temperature", "unit": "degree Celsius", "value": None},
                {"parameter": "humidity", "unit": "percent", "value": None},
                {"parameter": "soil_pH", "unit": "pH", "value": None},
                {"parameter": "co2_concentration", "unit": "ppm", "value": None},
                {"parameter": "light_intensity", "unit": "lux", "value": None},
            ]
            for item in initial_data:
                new_entry = SmartFarmData(**item)
                db.session.add(new_entry)
            db.session.commit()



# JWT Authentication API routes

# @app.route('/')
# def home():
#     return render_template('home.html')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()

#     if form.validate_on_submit():
#         # First check if the username is already registered or not
#         user = User.query.filter_by(username=form.username.data).first()
#         if user and bcrypt.check_password_hash(user.password, form.password.data):
#             # Generate JWT token
#             access_token = create_access_token(identity=user.username)
            
#             # Set the token as a cookie for client-side use
#             response = redirect(url_for('dashboard'))  

#             response.set_cookie('access_token', access_token) # Set the JWT token in a cookie 

#             login_user(user)
            
#             return response  

#         #If log in failed
#         return render_template('login.html', form=form, message="Invalid username or password")

#     return render_template('login.html', form=form)


# @app.route('/dashboard', methods=['GET', 'POST'])
# @login_required
# def dashboard():
#     token = request.cookies.get('access_token') #Verify if JWT is sucessfully stored in a cookie
#     print(f"JWT Token: {token}")  # Log the token received from cookies in terminal
#     return render_template('dashboard.html', token=token)


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegisterForm()

#     if form.validate_on_submit():
#         # Check if username already exists
#         if User.query.filter_by(username=form.username.data).first():
#             return render_template('register.html', form=form, message="Username already exists")

#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         new_user = User(username=form.username.data, password=hashed_password)
#         db.session.add(new_user)
#         db.session.commit()
#         return redirect(url_for('login'))

#     return render_template('register.html', form=form)


# @app.route('/logout', methods=['GET', 'POST'])
# @login_required
# def logout():
#     response = redirect(url_for('login'))  
#     unset_jwt_cookies(response)  # Unset the JWT token cookie
#     return response



# Smart Farm Data API Routes

@app.route('/data_retrieval', methods=['GET'])
@jwt_required()  # Protect this route with JWT authentication
def data_retrieval():
    # Retrieve all Smart Farm data from the database
    all_data = SmartFarmData.query.all()
    response = {
        "status": "success",
        "data": [{"parameter": item.parameter, "unit": item.unit, "value": item.value} for item in all_data]
    }
    return jsonify(response)


@app.route('/data_simulation', methods=['POST'])
@jwt_required()
def data_simulation():
    # Update Smart Farm data based on input JSON
    incoming_data = request.get_json()
    for key, value in incoming_data.items():
        # Find the corresponding entry in the database
        data_entry = SmartFarmData.query.filter_by(parameter=key).first()
        if data_entry:
            # Update the value
            data_entry.value = value
    db.session.commit()

    # Retrieve updated data for response
    updated_data = SmartFarmData.query.all()
    response = {
        "status": "success",
        "message": "Smart Farm data updated successfully!",
        "data": [{"parameter": item.parameter, "unit": item.unit, "value": item.value} for item in updated_data]
    }
    return jsonify(response)


@app.route('/satics/<path:path>')
def send_report(path):
    # Using request args for path will expose you to directory traversal attacks
    return send_from_directory('./statics', path)



if __name__ == '__main__':
    setup_database()  # Initialize the database
    app.run(debug=True)
    
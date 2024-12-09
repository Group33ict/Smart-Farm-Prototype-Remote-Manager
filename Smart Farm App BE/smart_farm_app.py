from flask import Flask, jsonify, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt


app = Flask(__name__)


# Unified Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/smart_farm_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecretkey'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Login Manager Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



# User Authentication Models and Forms
@login_manager.user_loader # Call back user objects from the user ID
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        # Query the dtb, check if the entered username is already existed in the database
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


# User Authentication API Routes
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # First check if the username is already registered or not
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Smart Farm Data API Routes
@app.route('/data_retrieval', methods=['GET'])
def data_retrieval():
    # Retrieve all Smart Farm data from the database
    all_data = SmartFarmData.query.all()
    response = {
        "status": "success",
        "data": [{"parameter": item.parameter, "unit": item.unit, "value": item.value} for item in all_data]
    }
    return jsonify(response)


@app.route('/data_simulation', methods=['POST'])
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



if __name__ == '__main__':
    setup_database()  # Initialize the database
    app.run(debug=True)
    
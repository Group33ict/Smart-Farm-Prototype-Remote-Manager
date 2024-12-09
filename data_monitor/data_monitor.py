from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/smart_farm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


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


@app.route('/data_retrieval', methods=['GET'])
def data_retrieval():
    # Retrieve all Smart Farm data from the database
    all_data = SmartFarmData.query.all()
    response = {
        "status": "success",
        "data": [
            {"parameter": item.parameter, "unit": item.unit, "value": item.value}
            for item in all_data
        ]
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
        "data": [
            {"parameter": item.parameter, "unit": item.unit, "value": item.value}
            for item in updated_data
        ]
    }
    return jsonify(response)


if __name__ == '__main__':
    setup_database()  # Initialize the database
    app.run(debug=True)

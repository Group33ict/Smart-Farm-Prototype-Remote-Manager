from flask import Flask, jsonify, request


app = Flask(__name__)


# Global variable to store Smart Farm data
smart_farm_data = {
    "temperature": {"unit":"degree Celcius", "value":None},  
    "humidity": {"unit": "percent", "value": None},
    "soil_pH": {"unit": "pH", "value": None},
    "co2_concentration": {"unit": "ppm", "value": None},
    "light_intensity": {"unit": "lux", "value": None}
}


@app.route('/data_retrieval', methods=['GET'])
def data_retrieval():
    # Return the current Smart Farm data
    return jsonify({
        "status": "success",
        "data": smart_farm_data
    })

@app.route('/data_simulation', methods=['POST'])
def data_simulation():
    # Update Smart Farm data based on input JSON
    global smart_farm_data
    incoming_data = request.get_json()

    # Validate and update data
    for key in incoming_data:
        if key in smart_farm_data and "value" in smart_farm_data[key]:
            smart_farm_data[key]["value"] = incoming_data[key]

    return jsonify({
        "status": "success",
        "message": "Smart Farm data updated successfully!",
        "data": smart_farm_data
    })



if __name__ == '__main__':
    app.run(debug=True)

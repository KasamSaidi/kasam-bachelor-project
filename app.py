from flask import Flask, render_template, request
import requests

app = Flask(__name__)

TOMTOM_API_KEY = '1n7hfspttTjYk53H8xAeOcNM53cseplD'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_route', methods=['POST'])
def calculate_route():
    start_location = request.form.get('start_location')
    end_location = request.form.get('end_location')

    url = f'https://api.tomtom.com/routing/1/calculateRoute/{start_location}:{end_location}/json'
    params = {'key': TOMTOM_API_KEY}
    response = requests.get(url, params=params)
    route_data = response.json()

    return render_template('result.html', route_data=route_data)

if __name__ == '__main__':
    app.run(debug=True)

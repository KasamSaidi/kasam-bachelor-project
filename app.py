from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Setze deinen TomTom API-Schlüssel hier
TOMTOM_API_KEY = '1n7hfspttTjYk53H8xAeOcNM53cseplD'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_route', methods=['POST'])
def calculate_route():
    start_location = request.form.get('start_location')
    end_location = request.form.get('end_location')

    # Führe die Anfrage an die TomTom API durch, um die Route zu berechnen
    url = f'https://api.tomtom.com/routing/1/calculateRoute/{start_location}:{end_location}/json'
    params = {'key': TOMTOM_API_KEY}
    response = requests.get(url, params=params)
    route_data = response.json()

    # Verarbeite die Antwort und zeige sie auf der Webseite an (implementiere die Funktion)

    return render_template('result.html', route_data=route_data)

if __name__ == '__main__':
    app.run(debug=True)

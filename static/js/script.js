var normalLayer;
var ecoLayer;
var isNormalLayerVisible = true;

var map = tt.map({
    key: "1n7hfspttTjYk53H8xAeOcNM53cseplD",
    container: "map",
});

map.on('load', function () {
    map.addSource('route-source', {
        type: 'geojson',
        data: geoJson
    });
    map.addSource('eco-route-source', {
        type: 'geojson',
        data: ecoJson
    });

    map.addLayer({
        id: 'route-layer',
        type: 'line',
        source: 'route-source',
        layout: {
            'line-join': 'round',
            'line-cap': 'round'
        },
        paint: {
            'line-color': '#007cbf',
            'line-width': 4
        }
    });

    var bounds = new tt.LngLatBounds();
    geoJson.features.forEach(function (feature) {
        bounds.extend(feature.geometry.coordinates);
    });
    map.fitBounds(bounds, { padding: 20 });
});

function toggleLayer() {
    if (map.getLayer('route-layer')) {
        map.removeLayer('route-layer')
        map.addLayer({
        id: 'eco-route-layer',
        type: 'line',
        source: 'eco-route-source',
        layout: {
            'line-join': 'round',
            'line-cap': 'round'
        },
        paint: {
            'line-color': '#176917',
            'line-width': 4
        }
    });
    }
    else {
        map.removeLayer('eco-route-layer')
        map.addLayer({
        id: 'route-layer',
        type: 'line',
        source: 'route-source',
        layout: {
            'line-join': 'round',
            'line-cap': 'round'
        },
        paint: {
            'line-color': '#007cbf',
            'line-width': 4
        }
    });
    }
}

function createMarker(icon, position, popupText) {
    var markerElement = document.createElement('div');
    markerElement.className = 'marker';

    var markerContentElement = document.createElement('div');
    markerContentElement.className = 'marker-content';
    markerElement.appendChild(markerContentElement);

    var iconElement = document.createElement('div');
    iconElement.className = 'marker-icon';
    iconElement.style.backgroundImage =
        'url(/static/img/' + icon + ')';
    if (icon == 'ziel_flagge.png'){
        iconElement.style.left = '11px';
    }
    markerContentElement.appendChild(iconElement);

    var popup = new tt.Popup({offset: 30}).setText(popupText);

    new tt.Marker({element: markerElement, anchor: 'bottom'})
        .setLngLat(position)
        .setPopup(popup)
        .addTo(map);
}

var firstCoordinate = geoJson.features[0].geometry.coordinates[0];
var lastCoordinate = geoJson.features[0].geometry.coordinates[geoJson.features[0].geometry.coordinates.length - 1];

createMarker('start_punkt.png', firstCoordinate, 'Startort');
createMarker('ziel_flagge.png', lastCoordinate, 'Ziel');
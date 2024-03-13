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
    var normalRouteInfo = document.querySelector('.normal-route-info');
    var ecoRouteInfo = document.querySelector('.eco-route-info');
    var normalEmissionInfo = document.querySelector('.normal-emission-info');
    var ecoEmissionInfo = document.querySelector('.eco-emission-info');

    if (isNormalLayerVisible) {
        normalRouteInfo.style.display = 'none';
        normalEmissionInfo.style.display = 'none';
        ecoRouteInfo.style.display = 'block';
        ecoEmissionInfo.style.display = 'block';
        isNormalLayerVisible = false;
    } else {
        normalRouteInfo.style.display = 'block';
        normalEmissionInfo.style.display = 'block';
        ecoRouteInfo.style.display = 'none';
        ecoEmissionInfo.style.display = 'none';
        isNormalLayerVisible = true;
    }
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

function hideRouteInfo(routeType) {
    var normalRouteInfo = document.querySelector('.normal-route-info');
    var ecoRouteInfo = document.querySelector('.eco-route-info');
    var normalEmissionInfo = document.querySelector('.normal-emission-info');
    var ecoEmissionInfo = document.querySelector('.eco-emission-info');

    ecoEmissionInfo.style.display = 'none';
    normalEmissionInfo.style.display = 'none';

    if (!isNormalLayerVisible & routeType === 'normal') {
        normalRouteInfo.style.display = 'block';
        ecoRouteInfo.style.display = 'none';
    } else {
        ecoRouteInfo.style.display = 'block';
        normalRouteInfo.style.display = 'none';
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

function selectRoute(routeType) {
    hideRouteInfo(routeType);

    var savedEmissionInfo = document.querySelector('.saved-emission-info');
    var buttons = document.querySelectorAll('.btn');
    var modalBackdrop = document.querySelector('.modal-backdrop');
    var modal = document.querySelector('.modal');
    var routeCompletionButton = document.querySelector('#routeCompletionButton');
    var routeCancelButton = document.querySelector('#routeCancelButton');

    buttons.forEach(function(button) {
        button.style.display = 'none';
    });
    if (modalBackdrop) {
        modalBackdrop.remove();
    }
    if (modal) {
        modal.style.display = 'none';
    }

    savedEmissionInfo.style.display = 'block';
    routeCompletionButton.style.display = 'block';
    routeCancelButton.style.display = 'block';

    if (routeType === 'normal') {
        map.removeLayer('eco-route-layer');
        map.removeSource('eco-route-source');
        isNormalLayerVisible = true;
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
    } else if (routeType === 'eco') {
        map.removeLayer('route-layer');
        map.removeSource('route-source');
        isNormalLayerVisible = false;
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

    sessionStorage.setItem('route_type', routeType);
}

function redirectToUserHomepage(username) {
    var routeType = sessionStorage.getItem('route_type');
    window.location.href = '/user/' + username + '?route_type=' + routeType;
}

var firstCoordinate = geoJson.features[0].geometry.coordinates[0];
var lastCoordinate = geoJson.features[0].geometry.coordinates[geoJson.features[0].geometry.coordinates.length - 1];

createMarker('start_punkt.png', firstCoordinate, 'Startort');
createMarker('ziel_flagge.png', lastCoordinate, 'Ziel');
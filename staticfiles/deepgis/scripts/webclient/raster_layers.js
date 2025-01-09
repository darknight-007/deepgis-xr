// Raster tile layer management
const rasterLayers = {
    'bf_aug_2020_raster': {
        name: 'BF August 2020 Raster',
        url: 'https://mbtiles.deepgis.org/data/bf_aug_2020_raster/{z}/{x}/{y}.png',
        minZoom: 12,
        maxZoom: 22,
        bounds: [
            [33.78160405323126, -111.2660005204955],
            [33.782606629396106, -111.26454488180822]
        ],
        center: [33.78210534131368, -111.26527270115186, 17]
    },
    'bf_oct_2020_raster': {
        name: 'BF October 2020 Raster',
        url: 'https://mbtiles.deepgis.org/data/bf_oct_2020_raster/{z}/{x}/{y}.png',
        minZoom: 12,
        maxZoom: 22,
        bounds: [
            [33.78160405323126, -111.2660005204955],
            [33.782606629396106, -111.26454488180822]
        ],
        center: [33.78210534131368, -111.26527270115186, 17]
    },
    'bf_feb_2021_3d': {
        name: 'BF February 2021 3D',
        url: 'https://mbtiles.deepgis.org/data/bf_feb_2021_3d/{z}/{x}/{y}.png',
        minZoom: 12,
        maxZoom: 22,
        bounds: [
            [33.78160405323126, -111.2660005204955],
            [33.782606629396106, -111.26454488180822]
        ],
        center: [33.78210534131368, -111.26527270115186, 17]
    },
    'bf_feb_2021_3d_43': {
        name: 'BF February 2021 3D (43)',
        url: 'https://mbtiles.deepgis.org/data/bf_feb_2021_3d_43/{z}/{x}/{y}.png',
        minZoom: 12,
        maxZoom: 22,
        bounds: [
            [33.78160405323126, -111.2660005204955],
            [33.782606629396106, -111.26454488180822]
        ],
        center: [33.78210534131368, -111.26527270115186, 17]
    }
};

// Vector tile layer configuration
const vectorLayers = {
    'bf_aug_2020_vector': {
        name: 'BF August 2020 Vector',
        url: 'https://mbtiles.deepgis.org/data/bf_aug_2020_vector/{z}/{x}/{y}.pbf',
        minZoom: 12,
        maxZoom: 22,
        bounds: [
            [33.78160405323126, -111.2660005204955],
            [33.782606629396106, -111.26454488180822]
        ],
        center: [33.78210534131368, -111.26527270115186, 17]
    },
    'bf_oct_2020_vector': {
        name: 'BF October 2020 Vector',
        url: 'https://mbtiles.deepgis.org/data/bf_oct_2020_vector/{z}/{x}/{y}.pbf',
        minZoom: 12,
        maxZoom: 22,
        bounds: [
            [33.78160405323126, -111.2660005204955],
            [33.782606629396106, -111.26454488180822]
        ],
        center: [33.78210534131368, -111.26527270115186, 17]
    },
    'bf_nov_2020': {
        name: 'BF November 2020',
        url: 'https://mbtiles.deepgis.org/data/bf_nov_2020/{z}/{x}/{y}.pbf',
        minZoom: 12,
        maxZoom: 22,
        bounds: [
            [33.78160405323126, -111.2660005204955],
            [33.782606629396106, -111.26454488180822]
        ],
        center: [33.78210534131368, -111.26527270115186, 17]
    },
    'bf_dec_2020': {
        name: 'BF December 2020',
        url: 'https://mbtiles.deepgis.org/data/bf_dec_2020/{z}/{x}/{y}.pbf',
        minZoom: 12,
        maxZoom: 22,
        bounds: [
            [33.78160405323126, -111.2660005204955],
            [33.782606629396106, -111.26454488180822]
        ],
        center: [33.78210534131368, -111.26527270115186, 17]
    },
    'bf_dec_2020_alt': {
        name: 'BF December 2020 (Alt)',
        url: 'https://mbtiles.deepgis.org/data/bf_dec_2020_alt/{z}/{x}/{y}.pbf',
        minZoom: 12,
        maxZoom: 22,
        bounds: [
            [33.78160405323126, -111.2660005204955],
            [33.782606629396106, -111.26454488180822]
        ],
        center: [33.78210534131368, -111.26527270115186, 17]
    },
    'bf_dec_2020_vector': {
        name: 'BF December 2020 Vector',
        url: 'https://mbtiles.deepgis.org/data/bf_dec_2020_vector/{z}/{x}/{y}.pbf',
        minZoom: 12,
        maxZoom: 22,
        bounds: [
            [33.78160405323126, -111.2660005204955],
            [33.782606629396106, -111.26454488180822]
        ],
        center: [33.78210534131368, -111.26527270115186, 17]
    }
};

function initRasterLayers(map) {
    // Create the base layers
    const baseLayers = {
        'Google Satellite': L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
            maxZoom: 22,
            subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
            attribution: '© Google'
        })
    };

    const overlayLayers = {};
    
    // Create raster overlay layers
    Object.entries(rasterLayers).forEach(([id, config]) => {
        const layer = L.tileLayer(config.url, {
            minZoom: config.minZoom,
            maxZoom: config.maxZoom,
            bounds: config.bounds,
            tms: false,  // Using XYZ format
            opacity: 0.7,  // Make overlays slightly transparent
            attribution: '© DeepGIS'
        });
        
        overlayLayers[config.name] = layer;
    });

    // Create vector overlay layers
    Object.entries(vectorLayers).forEach(([id, config]) => {
        const layer = L.vectorGrid.protobuf(config.url, {
            minZoom: config.minZoom,
            maxZoom: config.maxZoom,
            bounds: config.bounds,
            vectorTileLayerStyles: {
                // Add default styling for vector tiles
                default: {
                    weight: 1,
                    color: '#3388ff',
                    opacity: 0.7,
                    fill: true,
                    fillColor: '#3388ff',
                    fillOpacity: 0.2
                }
            },
            attribution: '© DeepGIS'
        });
        
        overlayLayers[config.name] = layer;
    });
    
    // Set initial view to the center point of the first layer
    const firstLayer = Object.values(rasterLayers)[0];
    map.setView([firstLayer.center[0], firstLayer.center[1]], firstLayer.center[2]);
    
    // Add Google Satellite as default base layer
    baseLayers['Google Satellite'].addTo(map);
    
    // Add layer control to map with base and overlay layers
    L.control.layers(baseLayers, overlayLayers, {
        position: 'topright',
        collapsed: false
    }).addTo(map);
    
    return {
        baseLayers,
        overlayLayers
    };
} 
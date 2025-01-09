// Raster tile layer management
const rasterLayers = {
    'BF_08-02-2020': {
        name: 'BF August 2020',
        url: '/tiles/BF_08-02-2020_raster/{z}/{x}/{y}.png',
        minZoom: 12,
        maxZoom: 22,
        bounds: [
            [33.78160405323126, -111.2660005204955],  // Southwest corner [lat, lng]
            [33.782606629396106, -111.26454488180822]  // Northeast corner [lat, lng]
        ],
        center: [33.78210534131368, -111.26527270115186, 17]  // [lat, lng, zoom]
    },
    'BF_2-15-2021_3d': {
        name: 'BF February 2021 3D',
        url: '/tiles/BF_2-15-2021_3d_43/{z}/{x}/{y}.png',
        minZoom: 12,
        maxZoom: 22,
        bounds: [
            [33.78160405323126, -111.2660005204955],
            [33.782606629396106, -111.26454488180822]
        ],
        center: [33.78210534131368, -111.26527270115186, 17]
    },
    'BF-12-20-2020': {
        name: 'BF December 2020',
        url: '/tiles/BF-12-20-2020/{z}/{x}/{y}.png',
        minZoom: 12,
        maxZoom: 22,
        bounds: [
            [33.78160405323126, -111.2660005204955],
            [33.782606629396106, -111.26454488180822]
        ],
        center: [33.78210534131368, -111.26527270115186, 17]
    },
    'BF_11-13-2020': {
        name: 'BF November 2020',
        url: '/tiles/BF_11-13-2020/{z}/{x}/{y}.png',
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
        'Google Satellite': L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
            maxZoom: 22,
            subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
            attribution: '© Google'
        })
    };

    const overlayLayers = {};
    
    // Create overlay layers from our raster tiles
    Object.entries(rasterLayers).forEach(([id, config]) => {
        const layer = L.tileLayer(config.url, {
            minZoom: config.minZoom,
            maxZoom: config.maxZoom,
            bounds: config.bounds,
            tms: true,
            opacity: 0.7,  // Make overlays slightly transparent
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
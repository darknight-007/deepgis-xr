// Raster tile layer management
const rasterLayers = {
    'BF_08-02-2020': {
        name: 'BF August 2020',
        url: 'http://localhost:8091/data/BF_08-02-2020_raster/{z}/{x}/{y}.png',
        minZoom: 0,
        maxZoom: 22
    },
    'BF_2-15-2021_3d': {
        name: 'BF February 2021 3D',
        url: 'http://localhost:8091/data/BF_2-15-2021_3d_43/{z}/{x}/{y}.png',
        minZoom: 0,
        maxZoom: 22
    },
    'BF-12-20-2020': {
        name: 'BF December 2020',
        url: 'http://localhost:8091/data/BF-12-20-2020/{z}/{x}/{y}.png',
        minZoom: 0,
        maxZoom: 22
    },
    'BF_11-13-2020': {
        name: 'BF November 2020',
        url: 'http://localhost:8091/data/BF_11-13-2020/{z}/{x}/{y}.png',
        minZoom: 0,
        maxZoom: 22
    }
};

function initRasterLayers(map) {
    const rasterControl = {};
    
    // Create layers and add them to the control
    Object.entries(rasterLayers).forEach(([id, config]) => {
        const layer = L.tileLayer(config.url, {
            minZoom: config.minZoom,
            maxZoom: config.maxZoom,
            tms: true,
            attribution: '© DeepGIS'
        });
        
        rasterControl[config.name] = layer;
    });
    
    // Add layer control to map
    L.control.layers(rasterControl, {}, {
        position: 'topright',
        collapsed: false
    }).addTo(map);
    
    // Add the first layer by default
    const firstLayer = Object.values(rasterControl)[0];
    firstLayer.addTo(map);
    
    return rasterControl;
} 
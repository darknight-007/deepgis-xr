// Layer management
const TILESERVER_URL = 'https://mbtiles.deepgis.org';
let layers = {
    base: null,
    vector: null
};

// Initialize layers
async function initRasterLayers(map) {
    try {
        // Fetch available layers from tileserver
        const response = await fetch(`${TILESERVER_URL}/data.json`);
        if (!response.ok) throw new Error('Failed to fetch layers');
        const data = await response.json();

        // Log available layers
        console.group('Available Layers');
        console.log('Total layers:', Object.keys(data).length);
        
        // Group layers by type
        const rasterLayers = [];
        const vectorLayers = [];
        
        Object.entries(data).forEach(([id, info]) => {
            if (!info || typeof info !== 'object') return;
            
            const layerInfo = {
                id,
                name: info.name || id,
                format: info.format,
                minzoom: info.minzoom,
                maxzoom: info.maxzoom,
                bounds: info.bounds,
                center: info.center
            };
            
            if (info.format === 'pbf') {
                vectorLayers.push(layerInfo);
            } else {
                rasterLayers.push(layerInfo);
            }
        });
        
        console.group('Raster Layers');
        console.log('Count:', rasterLayers.length);
        console.table(rasterLayers);
        console.groupEnd();
        
        console.group('Vector Layers');
        console.log('Count:', vectorLayers.length);
        console.table(vectorLayers);
        console.groupEnd();
        
        console.groupEnd();

        // Add OpenStreetMap as default base layer
        const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Create layer controls
    const baseLayers = {
            'OpenStreetMap': osm
        };

        const overlays = {
        'Raster Layers': {},
        'Vector Layers': {}
    };
    
        // Add raster layers to control
        rasterLayers.forEach(layer => {
            // Convert layer name to lowercase and replace spaces with underscores
            const layerPath = layer.name.toLowerCase().replace(/[_\s-]+/g, '_');
            baseLayers[layer.name] = L.tileLayer(`${TILESERVER_URL}/data/${layerPath}/{z}/{x}/{y}.png`, {
                minZoom: layer.minzoom || 0,
                maxZoom: layer.maxzoom || 22,
                bounds: layer.bounds ? L.latLngBounds([
                    [layer.bounds[1], layer.bounds[0]],
                    [layer.bounds[3], layer.bounds[2]]
                ]) : null
            });
        });

        // Add vector layers to control
        vectorLayers.forEach(layer => {
            // Convert layer name to lowercase and replace spaces with underscores
            const layerPath = layer.name.toLowerCase()
                .replace(/[_\s-]+/g, '_')
                .replace(/\.mbtiles$/, '')
                .replace(/_vector$/, '');
            overlays['Vector Layers'][layer.name] = L.vectorGrid.protobuf(
                `${TILESERVER_URL}/data/${layerPath}_vector/{z}/{x}/{y}.pbf`,
                {
                    minZoom: layer.minzoom || 0,
                    maxZoom: layer.maxzoom || 22,
                    bounds: layer.bounds ? L.latLngBounds([
                        [layer.bounds[1], layer.bounds[0]],
                        [layer.bounds[3], layer.bounds[2]]
                    ]) : null,
                    vectorTileLayerStyles: {
                        '*': {
                            weight: 2,
                            color: '#475569',
                            fillColor: '#64748B',
                            fillOpacity: 0.6
                        }
                    }
                }
            );
        });

        // Add layer control
        L.control.layers(baseLayers, overlays, {
        position: 'topright',
        collapsed: false
    }).addTo(map);
    
        // Set initial view if available
        if (rasterLayers.length > 0 && rasterLayers[0].bounds) {
            map.fitBounds([
                [rasterLayers[0].bounds[1], rasterLayers[0].bounds[0]],
                [rasterLayers[0].bounds[3], rasterLayers[0].bounds[2]]
            ]);
        } else {
            map.setView([33.78210534131368, -111.26527270115186], 15);
        }

        return { baseLayers, overlays };
    } catch (error) {
        console.error('Error initializing layers:', error);
        showSnackBar('Error loading layers. Please try refreshing the page.');
        throw error;
    }
}

// Helper function to show notifications
function showSnackBar(message) {
    const snackbar = document.createElement('div');
    snackbar.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #333;
        color: white;
        padding: 12px 24px;
        border-radius: 4px;
        z-index: 1000;
        min-width: 250px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    `;
    snackbar.textContent = message;
    document.body.appendChild(snackbar);
    setTimeout(() => snackbar.remove(), 3000);
}

// Export only what's needed
window.initRasterLayers = initRasterLayers; 
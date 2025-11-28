// Configuration - try different ports if needed
const API_BASE_URL = 'http://127.0.0.1:3000/api';  // Changed to 3000
const PORTS_TO_TRY = [3000, 5000, 8000, 8080];

// DOM Elements
let products = [];
let currentProductId = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Frontend loaded, testing API connection...');
    autoDetectAPI();
});

// Try to auto-detect where the API is running
async function autoDetectAPI() {
    for (const port of PORTS_TO_TRY) {
        const testUrl = `http://127.0.0.1:${port}/api/test`;
        console.log(`Trying ${testUrl}...`);
        
        try {
            const response = await fetch(testUrl);
            if (response.ok) {
                const data = await response.json();
                API_BASE_URL = `http://127.0.0.1:${port}/api`;
                console.log(`✅ Found API at: ${API_BASE_URL}`, data);
                showError(`✅ Connected to API on port ${port}`);
                loadProducts();
                return;
            }
        } catch (error) {
            console.log(`Port ${port} failed:`, error.message);
        }
    }
    
    // If no ports work, show detailed error
    showError(`
        ❌ Cannot find Flask API server. Please check:
        <br><br>
        1. <strong>Start Flask server:</strong><br>
        <code>cd ~/ims_project && source venv/bin/activate && python app.py</code>
        <br><br>
        2. <strong>Check the terminal output</strong> for the correct port number
        <br><br>
        3. <strong>Test manually:</strong><br>
        Open <a href="http://127.0.0.1:5000/api/test" target="_blank">http://127.0.0.1:5000/api/test</a>
        <br><br>
        <em>Error details: All ports failed (${PORTS_TO_TRY.join(', ')})</em>
    `);
}

// ... rest of your functions remain the same ...

async function loadProducts(searchQuery = '') {
    showLoading(true);
    hideError();

    try {
        const url = searchQuery 
            ? `${API_BASE_URL}/products?q=${encodeURIComponent(searchQuery)}`
            : `${API_BASE_URL}/products`;

        console.log('Fetching from:', url);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        products = await response.json();
        console.log(`Loaded ${products.length} products`);
        displayProducts(products);
    } catch (error) {
        console.error('Failed to load products:', error);
        showError(`Failed to load products: ${error.message}`);
    } finally {
        showLoading(false);
    }
}
// sales.js - Frontend JavaScript for Sales Processing

const API_BASE_URL = 'http://localhost:5000/api'; // Change to your backend URL

class SalesFrontend {
    constructor() {
        this.currentSaleItems = [];
        this.taxRate = 0.15; // 15% tax
        this.discountRate = 0.0; // No discount by default
    }

    // ---------------------- PRODUCT SEARCH ----------------------
    async searchProduct(productName) {
        try {
            const response = await fetch(`${API_BASE_URL}/products/search?name=${encodeURIComponent(productName)}`);
            if (!response.ok) throw new Error('Product search failed');
            const product = await response.json();
            return product;
        } catch (error) {
            console.error('Error searching product:', error);
            alert('Product not found or error occurred');
            return null;
        }
    }

    // ---------------------- ADD ITEM TO SALE ----------------------
    async addItemToSale(productName, quantity) {
        // 1. Search for product
        const product = await this.searchProduct(productName);
        if (!product) return false;

        // 2. Check stock
        if (product.current_quantity < quantity) {
            alert(`Only ${product.current_quantity} units available in stock`);
            return false;
        }

        // 3. Add to current sale
        const item = {
            product: product,
            quantity: quantity,
            price: product.price * quantity
        };

        this.currentSaleItems.push(item);
        this.updateSaleDisplay();
        return true;
    }

    // ---------------------- CALCULATE TOTALS ----------------------
    calculateTotals() {
        const subtotal = this.currentSaleItems.reduce((aggregate, item) => aggregate + item.price, 0);
        const tax = subtotal * this.taxRate;
        const discount = subtotal * this.discountRate;
        const total = subtotal + tax - discount;

        return {
            subtotal: subtotal.toFixed(2),
            tax: tax.toFixed(2),
            discount: discount.toFixed(2),
            total: total.toFixed(2)
        };
    }

    // ---------------------- UPDATE DISPLAY ----------------------
    updateSaleDisplay() {
        const itemsList = document.getElementById('sale-items-list');
        const totalsDisplay = document.getElementById('sale-totals');

        if (!itemsList || !totalsDisplay) return;

        // Update items list
        itemsList.innerHTML = '';
        this.currentSaleItems.forEach((item, index) => {
            const li = document.createElement('li');
            li.className = 'sale-item';
            li.innerHTML = `
                ${item.product.name} input ${item.quantity}
                = $${item.price.toFixed(2)}
                <button onclick="salesFrontend.removeItem(${index})">Remove</button>
            `;
            itemsList.appendChild(li);
        });

        // Update totals
        const totals = this.calculateTotals();
        totalsDisplay.innerHTML = `
            <p>Subtotal: $${totals.subtotal}</p>
            <p>Tax (${(this.taxRate * 100)}%): $${totals.tax}</p>
            <p>Discount: $${totals.discount}</p>
            <p><strong>Total: $${totals.total}</strong></p>
        `;
    }

    // ---------------------- REMOVE ITEM ----------------------
    removeItem(index) {
        this.currentSaleItems.splice(index, 1);
        this.updateSaleDisplay();
    }

    // ---------------------- FINALIZE SALE ----------------------
    async finalizeSale(cashierId) {
        if (this.currentSaleItems.length === 0) {
            alert('No items in sale');
            return false;
        }

        try {
            const saleData = {
                cashier_id: cashierId,
                items: this.currentSaleItems.map(item => ({
                    product_id: item.product.id,
                    quantity: item.quantity,
                    price_at_sale: item.product.price
                })),
                tax_rate: this.taxRate,
                discount_rate: this.discountRate
            };

            const response = await fetch(`${API_BASE_URL}/sales/process`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(saleData)
            });

            if (!response.ok) throw new Error('Sale processing failed');

            const result = await response.json();

            // Reset for next sale
            this.currentSaleItems = [];
            this.updateSaleDisplay();

            alert(`Sale completed! Transaction ID: ${result.transaction_id}`);

            // Generate receipt (optional)
            this.generateReceipt(result);

            return true;
        } catch (error) {
            console.error('Error finalizing sale:', error);
            alert('Error processing sale. Please try again.');
            return false;
        }
    }

    // ---------------------- GENERATE RECEIPT ----------------------
    generateReceipt(saleResult) {
        // In a real app, you might:
        // 1. Open a new window with receipt HTML
        // 2. Generate PDF
        // 3. Send email
        console.log('Receipt data:', saleResult);

        // Simple receipt display
        const receiptWindow = window.open('', '_blank');
        receiptWindow.document.write(`
            <html>
            <head><title>Receipt</title></head>
            <body>
                <h1>Carol's Distributors</h1>
                <h2>Receipt
                <p>Date: ${new Date().toLocaleString()}</p>
                <hr>
                <h3>Items:</h3>
                <ul>
                    ${this.currentSaleItems.map(item =>
                        `<li>${item.product.name} input ${item.quantity} = $${item.price.toFixed(2)}</li>`
                    ).join('')}
                </ul>
                <hr>
                <p>Subtotal: $${saleResult.subtotal}</p>
                <p>Tax: $${saleResult.tax}</p>
                <p>Total: $${saleResult.total}</p>
                <hr>
                <p>Thank you for shopping with us!</p>
            </body>
            </html>
        `);
    }

    // ---------------------- INITIALIZE ----------------------
    initialize() {
        // Set up event listeners if they exist in HTML
        const searchBtn = document.getElementById('search-product-btn');
        const addItemBtn = document.getElementById('add-item-btn');
        const finalizeBtn = document.getElementById('finalize-sale-btn');

        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                const productName = document.getElementById('product-search').value;
                const quantity = document.getElementById('product-quantity').value || 1;
                this.addItemToSale(productName, parseInt(quantity));
            });
        }

        if (finalizeBtn) {
            finalizeBtn.addEventListener('click', () => {
                const cashierId = document.getElementById('cashier-id').value || 1;
                this.finalizeSale(cashierId);
            });
        }

        console.log('Sales frontend initialized');
    }
}

// Create global instance
const salesFrontend = new SalesFrontend();

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    salesFrontend.initialize();
});

//---------------------------------------------
// LOAD DASHBOARD DATA
//---------------------------------------------
async function loadDashboard() {
    let products = await apiGet("/inventory/");
    let categories = await apiGet("/inventory/categories");

    // ---- CARDS ----
    document.getElementById("total-products").innerText = products.length;
    document.getElementById("total-categories").innerText = categories.length;
    let lowStockCount = products.filter(p => p.qty <= (p.reorder_threshold || 0)).length;
    document.getElementById("low-stock").innerText = lowStockCount;

    // ---- TABLE ----
    let tbody = document.querySelector("#product-table tbody");
    tbody.innerHTML = "";
    products.forEach(p => {
        tbody.innerHTML += `<tr>
            <td>${p.id}</td>
            <td>${p.name}</td>
            <td>$${p.price.toFixed(2)}</td>
            <td>${p.qty}</td>
            <td>${p.category}</td>
        </tr>`;
    });

    // ---- CHARTS ----
    renderCategoryChart(products);
    renderLowStockChart(products);
}

//---------------------------------------------
// RENDER CATEGORY PIE CHART
//---------------------------------------------
function renderCategoryChart(products) {
    const ctx = document.getElementById("categoryChart").getContext("2d");

    // Count products per category
    let categoryCounts = {};
    products.forEach(p => {
        if (!categoryCounts[p.category]) categoryCounts[p.category] = 0;
        categoryCounts[p.category]++;
    });

    const labels = Object.keys(categoryCounts);
    const data = Object.values(categoryCounts);

    if (window.categoryChartInstance) window.categoryChartInstance.destroy();

    window.categoryChartInstance = new Chart(ctx, {
        type: "pie",
        data: { labels, datasets: [{ data, backgroundColor: ["#FF6384","#36A2EB","#FFCE56","#4BC0C0","#9966FF","#FF9F40"] }] },
        options: { responsive: true, plugins: { legend: { position: "bottom" } } }
    });
}

//---------------------------------------------
// RENDER LOW-STOCK BAR CHART
//---------------------------------------------
function renderLowStockChart(products) {
    const ctx = document.getElementById("lowStockChart").getContext("2d");

    // Filter products with low stock
    let lowStockProducts = products.filter(p => p.qty <= (p.reorder_threshold || 0));

    const labels = lowStockProducts.map(p => p.name);
    const data = lowStockProducts.map(p => p.qty);

    if (window.lowStockChartInstance) window.lowStockChartInstance.destroy();

    window.lowStockChartInstance = new Chart(ctx, {
        type: "bar",
        data: { labels, datasets: [{ label: "Quantity", data, backgroundColor: "#FF6384" }] },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

//---------------------------------------------
// INIT DASHBOARD ON PAGE LOAD
//---------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
});


const DEFAULT_CATEGORIES = [
    'FOOD',
    'BEVERAGES',
    'HOUSEHOLD ITEMS',
    'CLEANING SUPPLIES',
    'MISCELLANEOUS'
];

//---------------------------------------------
// LOAD ALL PRODUCTS INTO TABLE
//---------------------------------------------
async function loadProducts() {
    let data = await apiGet("/inventory/");
    let table = document.getElementById("product-table");
    table.innerHTML = "";

    data.forEach(p => {
        table.innerHTML += `
            <tr>
                <td>${p.id}</td>
                <td>${p.name}</td>
                <td>$${p.price}</td>
                <td>${p.qty}</td>
                <td>${p.category}</td>
                <td>
                    <button class="btn-secondary" onclick='viewProductDetails(${JSON.stringify(p)})'>View</button>
                </td>
            </tr>
        `;
    });
}



//---------------------------------------------
// FETCH CATEGORIES FOR DROPDOWN
//---------------------------------------------
async function fetchCategories() {
    let dbCategories = await apiGet("/inventory/categories");
    let dbNames = dbCategories.map(c => c.name);

    // Merge DATABASE + DEFAULTS without duplicates
    let allCategories = Array.from(new Set([...DEFAULT_CATEGORIES, ...dbNames]));

    return allCategories;
}


//---------------------------------------------
// OPEN "ADD PRODUCT" MODAL
//---------------------------------------------
async function openAddProductModal() {
    document.getElementById("modal-title").innerText = "Add Product";

    let categories = await fetchCategories();
    let categoryOptions = categories
        .map(c => `<option value="${c}">${c}</option>`)
        .join("");

    document.getElementById("modal-body").innerHTML = `
        <input id="p-name" placeholder="Product Name" class="input" />
        <input id="p-price" placeholder="Price"  class="input" />
        <input id="p-qty" placeholder="Quantity" type="number" class="input" />
        <input id="p-threshold" placeholder="Reorder Threshold" type="number" class="input" />

        <select id="p-category" class="input">
            <option disabled selected>Category</option>
            ${categoryOptions}
        </select>
    `;

    

    document.getElementById("modal-save-btn").onclick = addProduct;
    openModal();
}


//---------------------------------------------
// ADD PRODUCT
//---------------------------------------------
async function addProduct() {
    let data = {
        name: document.getElementById("p-name").value,
        price: parseFloat(document.getElementById("p-price").value),
        quantity: parseInt(document.getElementById("p-qty").value),
        reorder_threshold: parseInt(document.getElementById("p-threshold").value),
        category: document.getElementById("p-category").value
    };

    let res = await apiPost("/inventory/product", data);

    if (res.error) {
        alert(res.error);
        return;
    }

    closeModal();
    loadProducts();
}


//---------------------------------------------
// OPEN "SELECT PRODUCT TO EDIT" MODAL
//---------------------------------------------
async function openSelectProductForEdit() {
    let products = await apiGet("/inventory/");

    let dropdown = `
        <select id="product-select" class="input">
            ${products.map(p => `<option value="${p.id}">${p.name}</option>`).join("")}
        </select>
    `;

    document.getElementById("modal-title").innerText = "Select Product to Edit";
    document.getElementById("modal-body").innerHTML = dropdown;

    document.getElementById("modal-save-btn").onclick = async () => {
        let id = document.getElementById("product-select").value;
        let product = products.find(p => p.id == id);
        await openEditProductModal(product);
    };

    openModal();
}


//---------------------------------------------
// OPEN "EDIT PRODUCT" MODAL
//---------------------------------------------
async function openEditProductModal(product) {
    document.getElementById("modal-title").innerText = "Edit Product";

    let categories = await fetchCategories();

    if (!categories.includes(product.category)) {
        categories.push(product.category);
    }

    let categoryOptions = categories
        .map(c => `<option value="${c}" ${c === product.category ? "selected" : ""}>${c}</option>`)
        .join("");

    document.getElementById("modal-body").innerHTML = `
        <input id="p-name" value="${product.name}" class="input" />
        <input id="p-price" value="${product.price}" class="input" />
        <input id="p-qty" value="${product.qty}" type="number" class="input" />
        <input id="p-threshold" value="${product.reorder_threshold != null ? product.reorder_threshold : ''}" type="number" class="input" />

        <select id="p-category" class="input">
            ${categoryOptions}
        </select>
    `;

    document.getElementById("modal-save-btn").onclick = () => updateProduct (product.id);
    openModal();
}



//---------------------------------------------
// UPDATE PRODUCT  
//---------------------------------------------
async function updateProduct(id) {
    let data = {
        name: document.getElementById("p-name").value,
        price: parseFloat(document.getElementById("p-price").value),
        current_quantity: parseInt(document.getElementById("p-qty").value),
        reorder_threshold: parseInt(document.getElementById("p-threshold").value),
        category: document.getElementById("p-category").value
    };

    let res = await apiPut(`/inventory/product/${id}`, data);

    if (res.error) {
        alert(res.error);
        return;
    }

    closeModal();
    loadProducts();
}


//---------------------------------------------
// OPEN "SELECT PRODUCT TO DELETE" MODAL
//---------------------------------------------
async function openSelectProductForDelete() {
    let products = await apiGet("/inventory/");

    let dropdown = `
        <select id="product-select" class="input">
            ${products.map(p => `<option value="${p.id}">${p.name}</option>`).join("")}
        </select>
    `;

    document.getElementById("modal-title").innerText = "Select Product to Remove";
    document.getElementById("modal-body").innerHTML = dropdown;

    document.getElementById("modal-save-btn").onclick = () => {
        let id = document.getElementById("product-select").value;
        openDeleteProductModal(id);
    };

    openModal();
}


//---------------------------------------------
// DELETE CONFIRMATION
//---------------------------------------------
function openDeleteProductModal(id) {
    document.getElementById("modal-title").innerText = "Confirm Delete";
    document.getElementById("modal-body").innerHTML = `<p>Are you sure you want to delete this product?</p>`;

    document.getElementById("modal-save-btn").onclick = () => deleteProduct(id);
    openModal();
}


//---------------------------------------------
// DELETE PRODUCT
//---------------------------------------------
async function deleteProduct(id) {
    await apiDelete(`/inventory/product/${id}`);
    closeModal();
    loadProducts();
}

function viewProductDetails(product) {
    document.getElementById("modal-title").innerText = "Product Details";

    document.getElementById("modal-body").innerHTML = `
        <p><strong>Product ID:</strong> ${product.id}</p>
        <p><strong>Name:</strong> ${product.name}</p>
        <p><strong>Price:</strong> $${product.price}</p>
        <p><strong>Quantity:</strong> ${product.qty}</p>
        <p><strong>Reorder Threshold:</strong> ${product.reorder_threshold || "N/A"}</p>
        <p><strong>Category:</strong> ${product.category}</p>
    `;

    document.getElementById("modal-save-btn").style.display = "none"; 
    openModal();
}




//---------------------------------------------
// MODAL HELPERS
//---------------------------------------------
function openModal() {
    document.getElementById("modal").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("modal").classList.add("hidden");
    document.getElementById("modal-save-btn").style.display = "inline-block"; 
}


//---------------------------------------------
// EVENT LISTENERS
//---------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    loadProducts();

    document.getElementById("add-product-btn").addEventListener("click", openAddProductModal);
    document.getElementById("edit-product-btn").addEventListener("click", openSelectProductForEdit);
    document.getElementById("remove-product-btn").addEventListener("click", openSelectProductForDelete);
    document.getElementById("modal-close-btn").addEventListener("click", closeModal);
    document.getElementById("modal-cancel-btn").addEventListener("click", closeModal);
});

async function loadAlerts() {
    let data = await apiGet("/alerts/");  // make sure apiGet works
    let table = document.getElementById("alert-table");

    table.innerHTML = "";

    if (!data || data.length === 0) {
        table.innerHTML = `<tr><td colspan="3" style="text-align:center;">No alerts</td></tr>`;
        return;
    }

    data.forEach(a => {
        table.innerHTML += `
            <tr>
                <td>${a.product}</td>
                <td>${a.msg}</td>
                <td>${a.status}</td>
            </tr>
        `;
    });
}

window.addEventListener("DOMContentLoaded", loadAlerts);



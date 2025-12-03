// reports.js
document.addEventListener("DOMContentLoaded", function() {
    loadReports();
    setupModalListeners();
});

function setupModalListeners() {
    // Close modal when clicking outside
    const modal = document.getElementById("report-modal");
    if (modal) {
        modal.addEventListener("click", function(e) {
            if (e.target === modal) {
                closeReportModal();
            }
        });
    }
    
    // Set today's date in modal
    const today = new Date().toISOString().split("T")[0];
    const dateInput = document.getElementById("report-date");
    if (dateInput) {
        dateInput.value = today;
    }
}

async function loadReports() {
    try {
        console.log("Loading reports from /reports/list");
        const response = await fetch('/reports/list');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log("Reports data:", data);
        
        const container = document.getElementById("report-list");
        const table = document.getElementById("report-table");
        const noMsg = document.getElementById("no-reports-msg");
        
        if (!container || !table || !noMsg) {
            console.error("Missing HTML elements!");
            return;
        }
        
        container.innerHTML = "";

        if (!data.success || !data.reports || data.reports.length === 0) {
            noMsg.innerText = "No reports yet. Generate your first report!";
            table.classList.add("hidden");
            return;
        }

        table.classList.remove("hidden");
        noMsg.innerText = "";

        data.reports.forEach(report => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${report.report_date || report.date || 'N/A'}</td>
                <td>${report.created || 'N/A'}</td>
                <td>${report.size || 'N/A'}</td>
                <td>
                    <button onclick="viewReport('${report.filename}')" class="btn-view">
                        View
                    </button>
                </td>
                <td>
                    <button onclick="downloadReport('${report.filename}')" class="btn-download">
                        Download
                    </button>
                </td>
                <td>
                    <button onclick="deleteReport('${report.filename}')" class="btn-delete">
                        Delete
                    </button>
                </td>
            `;
            container.appendChild(row);
        });
    } catch (error) {
        console.error("Error loading reports:", error);
        const noMsg = document.getElementById("no-reports-msg");
        if (noMsg) {
            noMsg.innerText = "Error loading reports: " + error.message;
        }
    }
}

// View report in same tab
function viewReport(filename) {
    console.log("Viewing report:", filename);
    window.location.href = `/reports/download/${filename}`;
}

// Download report
function downloadReport(filename) {
    console.log("Downloading report:", filename);
    
    // Method 1: Direct download link
    const downloadLink = document.createElement('a');
    downloadLink.href = `/reports/download/${filename}?download=true`;
    downloadLink.download = filename;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
    
    // Method 2: Alternative approach
    // window.location.href = `/reports/download/${filename}?download=true`;
}

async function generateReport() {
    try {
        // Get date from modal input or use today
        const dateInput = document.getElementById("report-date");
        const reportDate = dateInput ? dateInput.value : new Date().toISOString().split("T")[0];
        
        console.log("Generating report for date:", reportDate);
        
        const response = await fetch('/reports/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ date: reportDate })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log("Generate response:", result);
        
        if (result.success) {
            alert(`Report generated successfully!\nFilename: ${result.report.filename}`);
            closeReportModal();
            loadReports(); // Reload the reports list
        } else {
            alert("Error: " + result.error);
        }
    } catch (error) {
        console.error("Generate report error:", error);
        alert("Network error: " + error.message);
    }
}

function generateMonthlyReport() {
    if (confirm("Generate monthly report for 1st of this month?")) {
        fetch('/reports/generate/monthly', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert("Monthly report generation started!");
                setTimeout(loadReports, 2000); // Reload after 2 seconds
            } else {
                alert("Error: " + result.error);
            }
        })
        .catch(error => {
            alert("Network error: " + error.message);
        });
    }
}

function exportToCSV() {
    fetch('/reports/inventory')
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                throw new Error(data.error);
            }
            
            // Convert to CSV
            const headers = ['Product Name', 'Quantity', 'Category', 'Threshold', 'Unit Price', 'Total Value'];
            const rows = data.data.map(item => [
                `"${item.name.replace(/"/g, '""')}"`,
                item.qty,
                `"${item.category.replace(/"/g, '""')}"`,
                item.threshold,
                item.unit_price,
                item.total_value
            ]);
            
            const csvContent = [
                headers.join(','),
                ...rows.map(row => row.join(','))
            ].join('\n');
            
            // Download CSV
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `inventory_export_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            alert('Inventory exported to CSV successfully!');
        })
        .catch(error => {
            alert('Error exporting to CSV: ' + error.message);
        });
}

async function deleteReport(filename) {
    if (!confirm(`Delete "${filename}"?`)) return;
    
    try {
        const response = await fetch(`/reports/delete/${filename}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            alert("Report deleted");
            loadReports();
        } else {
            alert("Error: " + result.error);
        }
    } catch (error) {
        alert("Network error: " + error.message);
    }
}

function openGenerateReportModal() {
    const modal = document.getElementById("report-modal");
    if (modal) {
        modal.classList.remove("hidden");
    }
}

function closeReportModal() {
    const modal = document.getElementById("report-modal");
    if (modal) {
        modal.classList.add("hidden");
    }
}
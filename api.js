const API = "http://localhost:5000";

function getToken() {
    return localStorage.getItem("token");
}

async function apiGet(url) {
    return fetch(API + url, {
        headers: { "Authorization": getToken() }
    }).then(r => r.json());
}

async function apiPost(url, data) {
    return fetch(API + url, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "Authorization": getToken() 
        },
        body: JSON.stringify(data)
    }).then(r => r.json());
}

async function apiPut(url, data) {
    return fetch(API + url, {
        method: "PUT",
        headers: { 
            "Content-Type": "application/json",
            "Authorization": getToken() 
        },
        body: JSON.stringify(data)
    }).then(r => r.json());
}

async function apiDelete(url) {
    return fetch(API + url, {
        method: "DELETE",
        headers: { "Authorization": getToken() }
    }).then(r => r.json());
}

async function login() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    let res = await apiPost("/auth/login", { username, password });

    if (res.token) {
        localStorage.setItem("token", res.token);
        window.location.href = "dashboard.html";
    } else {
        document.getElementById("login-error").innerText = res.error;
    }
}

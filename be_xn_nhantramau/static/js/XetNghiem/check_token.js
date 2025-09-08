async function checkToken(KEY_AUTHOR = "") {
    const access_token = localStorage.getItem("access_token");

    // 🚨 If no token found → redirect immediately
    if (!access_token) {
        redirectToLogin();
        return false;
    }

    try {
        let response = await fetch("/api/users/current-user/", {
            method: "GET",
            headers: {
                Authorization: `${KEY_AUTHOR} ${access_token.replace(/"/g, "")}`
            }
        });

        let data = await response.json();

        // console.log(data)
        if (response.status === 200 && data?.data) {
            return true;
        } else {
            // ❌ Invalid / expired token
            redirectToLogin();
            return false;
        }
    } catch (err) {
        console.error("Token check failed:", err);
        redirectToLogin();
        return false;
    }
}

function redirectToLogin() {
    // clear everything before redirect
    localStorage.removeItem("user");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("expires_at");
    localStorage.removeItem("refresh_expires_at");

    window.location.href = "/xn/login/";
}

async function checkScreenLogin(KEY_AUTHOR = "") {
    const access_token = localStorage.getItem("access_token");

    if (access_token) {
        try {
            let response = await fetch("/api/users/current-user/", {
                method: "GET",
                headers: {
                    Authorization: `${KEY_AUTHOR} ${access_token.replace(/"/g, "")}`
                }
            });

            let data = await response.json();

            if (response.status === 200) {
                // Store updated user info
                if (data.data?.user) {
                    localStorage.setItem("user", JSON.stringify(data.data.user));
                }

                // ✅ Redirect after success
                window.location.href = "/xn/main/";
            } else {
                // ❌ Token invalid or unexpected error → redirect login
                clearStorageAndRedirect();
            }
        } catch (err) {
            console.error("Error:", err);
            clearStorageAndRedirect();
        }
    }
}

function clearStorageAndRedirect() {
    localStorage.removeItem("user");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("expires_at");
    localStorage.removeItem("refresh_expires_at");
    window.location.href = "/xn/login/"; // 🔄 redirect to login
}
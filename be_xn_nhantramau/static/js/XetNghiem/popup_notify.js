function showNotify(message, type = "info", duration = 3500) {
    const container = document.getElementById("notify-container");

    // Create toast div
    const toast = document.createElement("div");
    toast.className = `
    px-4 py-3 rounded-xl shadow-lg text-white font-medium flex items-center justify-between space-x-4 animate-slide-in
    ${type === "success" ? "bg-green-500" : ""}
    ${type === "error" ? "bg-red-500" : ""}
    ${type === "info" ? "bg-blue-500" : ""}
    ${type === "warning" ? "bg-yellow-500 text-black" : ""}
  `;
    toast.innerHTML = `
    <span>${message}</span>
    <button class="ml-3 text-xl font-bold">&times;</button>
  `;

    // Add close button event
    toast.querySelector("button").addEventListener("click", () => {
        toast.remove();
    });

    // Append toast to container
    container.appendChild(toast);

    // Auto-remove after duration
    setTimeout(() => {
        toast.classList.add("animate-slide-out");
        setTimeout(() => toast.remove(), 300); // wait for animation
    }, duration);
}

// Animations
const style = document.createElement("style");
style.innerHTML = `
@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
@keyframes slideOut {
  from { transform: translateX(0); opacity: 1; }
  to { transform: translateX(100%); opacity: 0; }
}
.animate-slide-in { animation: slideIn 0.3s ease-out; }
.animate-slide-out { animation: slideOut 0.3s ease-in; }
`;
document.head.appendChild(style);


// // Success
// showNotify("Login successful!", "success");

// // Error
// showNotify("Invalid username or password!", "error");

// // Info
// showNotify("Fetching data...", "info");

// // Warning
// showNotify("Your session is about to expire!", "warning");
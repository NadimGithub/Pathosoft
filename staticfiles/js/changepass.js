function openChangePasswordModal() {
    document.getElementById("changePasswordModal").style.display = "flex";
}

function closeModal() {
    document.getElementById("changePasswordModal").style.display = "none";
}

function togglePassword(id, icon) {
    const input = document.getElementById(id);
    const isPassword = input.type === "password";
    input.type = isPassword ? "text" : "password";
    icon.classList.toggle("bi-eye");
    icon.classList.toggle("bi-eye-slash");
}

// Close modal when clicking outside content
window.onclick = function(event) {
    const modal = document.getElementById("changePasswordModal");
    if (event.target === modal) {
        modal.style.display = "none";
    }
}
   document.addEventListener("DOMContentLoaded", function () {
    const today = new Date().toISOString().split('T')[0];

    document.getElementById("sample_date").value = today;
    document.getElementById("reporting_date").value = today; 
    
});

function openTestPanel() {
    document.getElementById("addTestPanel").classList.add("active");
    document.getElementById("testPanelOverlay").classList.add("active");
}

function closeTestPanel() {
    document.getElementById("addTestPanel").classList.remove("active");
    document.getElementById("testPanelOverlay").classList.remove("active");
}


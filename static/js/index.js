// Sidebar toggle
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const menuBtn = document.getElementById('menu-btn');
const closeBtn = document.getElementById('sidebar-close');

menuBtn.addEventListener('click', () => {
    sidebar.classList.add('active');
    overlay.classList.add('show');
});

closeBtn.addEventListener('click', () => {
    sidebar.classList.remove('active');
    overlay.classList.remove('show');
});

overlay.addEventListener('click', () => {
    sidebar.classList.remove('active');
    overlay.classList.remove('show');
});

// Compact sidebar toggle for large screens
document.addEventListener('keydown', e => {
    if (e.key === 'b' && e.ctrlKey) {
        sidebar.classList.toggle('compact');
        document.getElementById('main').classList.toggle('compact');
    }
});

// Chart.js configurations
const testStatusCtx = document.getElementById('testStatusChart');
const patientTypeCtx = document.getElementById('patientTypeChart');

if (testStatusCtx) {
    new Chart(testStatusCtx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'Pending', 'Cancelled'],
            datasets: [{
                data: [1050, 200, 50],
                backgroundColor: ['#4caf50', '#ff9800', '#f44336'],
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

if (patientTypeCtx) {
    new Chart(patientTypeCtx, {
        type: 'pie',
        data: {
            labels: ['New Patients', 'Returning Patients'],
            datasets: [{
                data: [650, 350],
                backgroundColor: ['#3f51b5', '#9c27b0'],
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}
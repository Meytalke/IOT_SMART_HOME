let gasLevel = 0; // Simulate gas level
let smokeLevel = 0; // Simulate smoke density
let temperature = 0;
let gasValveOpen = true; // Track gas valve state
let alarmActive = false; // Track alarm state
let ventilationOn = false; // Track ventilation status

const GAS_THRESHOLD = 40;
const SMOKE_THRESHOLD = 50;
const TEMP_THRESHOLD = 70;

document.addEventListener('DOMContentLoaded', function() {
    // Update system time every second
    function updateTime() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        document.getElementById('system-time').textContent = `${hours}:${minutes}:${seconds}`;
    }
    setInterval(updateTime, 1000);

    // Initial sensor data update
    updateSensorDisplay();
    setInterval(updateSensorData, 3000); // Update sensor data every 3 seconds

    function updateSensorData() {
        gasLevel = Math.floor(Math.random() * 39); // Simulate gas level
        smokeLevel = Math.floor(Math.random() * 49); // Simulate smoke density
        temperature = Math.floor(Math.random() * 69); // Simulate temperature
        updateSensorDisplay();

        const valveOpen = Math.random() < 0.8; // Simulate valve status
        document.getElementById('valve-status').textContent = valveOpen ? 'Open' : 'Closed';
        document.getElementById('valve-badge').className = `sensor-badge badge-${valveOpen ? 'success' : 'danger'}`;
        document.getElementById('valve-badge').innerHTML = `<i class="fas fa-${valveOpen ? 'check-circle' : 'times-circle'}"></i> <span>${valveOpen ? 'Open' : 'Closed'}</span>`;

        // Simulate an alert
        if (Math.random() < 0.05) {
            showAlert('Critical Gas Leak Detected!', 'High levels of gas detected. Automatic safety protocols initiated.', 'danger');
            document.getElementById('fix-progress-steps').style.display = 'flex';
            setTimeout(() => {
                document.getElementById('step-1-status').textContent = '✔';
                document.getElementById('step-1-status').className = 'step-status step-complete';
                document.getElementById('valve-status').textContent = 'Closed';
                document.getElementById('valve-badge').className = 'sensor-badge badge-danger';
                document.getElementById('valve-badge').innerHTML = '<i class="fas fa-times-circle"></i> <span>Closed</span>';
                setTimeout(() => {
                    document.getElementById('step-2-status').textContent = '✔';
                    document.getElementById('step-2-status').className = 'step-status step-complete';
                    setTimeout(() => {
                        document.getElementById('step-3-status').textContent = '✔';
                        document.getElementById('step-3-status').className = 'step-status step-complete';
                    }, 1500);
                }, 2000);
            }, 2000);
        }
    }

    function updateSensorDisplay() {
        document.getElementById('gas-value').textContent = `${gasLevel}%`;
        document.getElementById('gas-level-bar').style.width = `${gasLevel}%`;
        document.getElementById('gas-level-bar').style.backgroundColor = gasLevel > GAS_THRESHOLD ? '#e74c3c' : '#3498db';
        document.getElementById('gas-status').textContent = gasLevel > GAS_THRESHOLD ? 'High' : 'Normal';
        document.getElementById('gas-status').className = gasLevel > GAS_THRESHOLD ? 'status-danger' : 'status-normal';

        document.getElementById('smoke-value').textContent = `${smokeLevel}%`;
        document.getElementById('smoke-level-bar').style.width = `${smokeLevel}%`;
        document.getElementById('smoke-level-bar').style.backgroundColor = smokeLevel > SMOKE_THRESHOLD ? '#e74c3c' : '#3498db';
        document.getElementById('smoke-status').textContent = smokeLevel > SMOKE_THRESHOLD ? 'High' : 'Normal';
        document.getElementById('smoke-status').className = smokeLevel > SMOKE_THRESHOLD ? 'status-danger' : 'status-normal';

        document.getElementById('temp-value').textContent = `${temperature}°C`;
        document.getElementById('temp-level-bar').style.width = `${temperature / 100 * 100}%`; // Assuming max temp is 100 for scaling
        document.getElementById('temp-level-bar').style.backgroundColor = temperature > TEMP_THRESHOLD ? '#e74c3c' : '#3498db';
        document.getElementById('temp-status').textContent = temperature > TEMP_THRESHOLD ? 'High' : 'Normal';
        document.getElementById('temp-status').className = temperature > TEMP_THRESHOLD ? 'status-danger' : 'status-normal';

        document.getElementById('valve-status').textContent = gasValveOpen ? 'Open' : 'Closed';
        document.getElementById('valve-badge').className = `sensor-badge badge-${gasValveOpen ? 'success' : 'danger'}`;
        document.getElementById('valve-badge').innerHTML = `<i class="fas fa-${gasValveOpen ? 'check-circle' : 'times-circle'}"></i> <span>${gasValveOpen ? 'Open' : 'Closed'}</span>`;
    }

    function simulateGasLeak() {
        gasLevel = Math.min(100, GAS_THRESHOLD + 30);
        showAlert('Gas Leak Detected!', 'Emergency protocol activated: Gas Leak.', 'danger');
        addAlert('Simulated Gas Leak.', 'danger');
        closeGasValveManually();
        updateSensorDisplay();
        
    }

    function simulateHighTemp() {
        temperature = Math.min(100, TEMP_THRESHOLD + 40);
        showAlert('High Temperature Detected!', 'Emergency protocol activated: High Temperature.', 'danger');
        addAlert('Simulated High Temperature.', 'danger');
        ventilationOn = false;
        toggleVentilation();
        updateSensorDisplay();
        
    }

    function simulateSmoke() {
        smokeLevel = Math.min(100, SMOKE_THRESHOLD + 40);
        showAlert('Smoke Detected!', 'Emergency protocol activated: Smoke.', 'danger');
        addAlert('Simulated Smoke Detected.', 'danger');
        ventilationOn = false;
        toggleVentilation();
        updateSensorDisplay();
        
    }

    function toggleVentilation() {
        ventilationOn = !ventilationOn;
        const message = ventilationOn ? 'Ventilation turned ON manually.' : 'Ventilation turned OFF manually.';
        addAlert(message, 'info');
        const ventilationOnButton = document.getElementById('ventilation-on');
        const ventilationOffButton = document.getElementById('ventilation-off');
        if (ventilationOn) {
            ventilationOnButton.classList.add('active');
            ventilationOffButton.classList.remove('active');
        } else {
            ventilationOnButton.classList.remove('active');
            ventilationOffButton.classList.add('active');
        }
    }

    function updateGasValveStatusDisplay() {
        const valveStatusElement = document.getElementById('valve-status');
        const valveBadgeElement = document.getElementById('valve-badge');
        const statusText = gasValveOpen ? 'Open' : 'Closed';
        const badgeClass = `sensor-badge badge-${gasValveOpen ? 'success' : 'danger'}`;
        const badgeHTML = `<i class="fas fa-${gasValveOpen ? 'check-circle' : 'times-circle'}"></i> <span>${statusText}</span>`;
    
        console.log('updateGasValveStatusDisplay called. gasValveOpen:', gasValveOpen, 'Status Text:', statusText, 'Badge Class:', badgeClass, 'Badge HTML:', badgeHTML);
    
        if (valveStatusElement) {
            valveStatusElement.textContent = statusText;
        } else {
            console.error('Element with ID "valve-status" not found!');
        }
    
        if (valveBadgeElement) {
            valveBadgeElement.className = badgeClass;
            valveBadgeElement.innerHTML = badgeHTML;
        } else {
            console.error('Element with ID "valve-badge" not found!');
        }
    }
    
    function openGasValveManually() {
        gasValveOpen = true;
        updateGasValveStatusDisplay();
        addAlert('Gas Valve Opened Manually.', 'info');
        console.log('openGasValveManually called. gasValveOpen:', gasValveOpen);
    }
    
    function closeGasValveManually() {
        gasValveOpen = false;
        updateGasValveStatusDisplay();
        addAlert('Gas Valve Closed Manually.', 'warning');
        console.log('closeGasValveManually called. gasValveOpen:', gasValveOpen);
    }

    function resetAlarmManually() {
        alarmActive = false;
        addAlert('Alarm System Reset Manually.', 'info');
        document.getElementById('alert-modal').style.display = 'none'; // Close modal if open
    }

    function triggerEmergencyManually() {
        showAlert('Manual Emergency Triggered!', 'Manual emergency protocol initiated.', 'danger');
        addAlert('Manual emergency protocol initiated.', 'danger');
    }

    function contactSupportManually() {
        addAlert('Contacting support...', 'info');
        // In a real system, you would initiate a support contact here
    }

    // Function to add a new alert to the list
    function addAlert(message, type) {
        const alertsLists = document.querySelectorAll('.alerts-list'); // Selects all alert lists
        const alertHTML = `
            <div class="alert-item alert-${type}">
                <div class="alert-icon">
                    <i class="fas fa-${type === 'info' ? 'info' : (type === 'warning' ? 'exclamation-triangle' : 'fire-extinguisher')}"></i>
                </div>
                <div class="alert-content">
                    <div class="alert-message">${message}</div>
                    <div class="alert-time">${new Date().toLocaleTimeString()}</div>
                </div>
            </div>
        `;

        alertsLists.forEach(list => {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = alertHTML;
            list.prepend(tempDiv.firstElementChild); // Adds the alert to the top of the list
        });
    }

    // Example alert
    addAlert('System started', 'info');

    // Automatic problem handling toggle
    const autoFixToggle = document.getElementById('auto-fix-toggle');
    const autoFixStatus = document.querySelector('.auto-fix-status');

    document.querySelector('.btn-primary').addEventListener('click', exportAlerts);

    function exportAlerts() {
        const alertItems = document.querySelectorAll('.alerts-list .alert-item');
        let reportText = "System Alerts Report:\n\n";
    
        alertItems.forEach(item => {
            const messageElement = item.querySelector('.alert-message');
            const timeElement = item.querySelector('.alert-time');
            if (messageElement && timeElement) {
                reportText += `Message: ${messageElement.textContent}\n`;
                reportText += `Time: ${timeElement.textContent}\n`;
                reportText += "---\n";
            }
        });
    
        if (alertItems.length === 0) {
            reportText += "No alerts in the system.\n";
        }
    
        const filename = 'alerts_report.txt';
        const blob = new Blob([reportText], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    
        addAlert('Exporting alerts report.', 'info');
    }

    autoFixToggle.addEventListener('change', function() {
        autoFixStatus.textContent = this.checked ? 'Enabled' : 'Disabled';
        autoFixStatus.className = `auto-fix-status ${this.checked ? 'enabled' : 'disabled'}`;
    });

    // Control button functionality
    document.getElementById('ventilation-on').addEventListener('click', toggleVentilation);
    document.getElementById('ventilation-off').addEventListener('click', toggleVentilation);
    document.getElementById('valve-open').addEventListener('click', openGasValveManually);
    document.getElementById('valve-close').addEventListener('click', closeGasValveManually);
    document.getElementById('alarm-silence').addEventListener('click', resetAlarmManually);
    document.getElementById('reset-alarm').addEventListener('click', resetAlarmManually);
    document.getElementById('trigger-emergency').addEventListener('click', triggerEmergencyManually);
    document.getElementById('contact-support').addEventListener('click', contactSupportManually);
    document.getElementById('refresh-btn').addEventListener('click', () => {
        updateSensorData();
        addAlert('Dashboard data refreshed.', 'info');
    });

    // Simulation buttons
    const btnGasLeak = document.getElementById('btn-simulate-gas-leak');
    if (btnGasLeak) {
        btnGasLeak.addEventListener('click', () => {
            simulateGasLeak();
        });
    }

    const btnHighTemp = document.getElementById('btn-simulate-high-temp');
    if (btnHighTemp) {
        btnHighTemp.addEventListener('click', () => {
            simulateHighTemp();
        });
    }

    const btnSmoke = document.getElementById('btn-simulate-smoke');
    if (btnSmoke) {
        btnSmoke.addEventListener('click', () => {
            simulateSmoke();
        });
    }


    // Tab navigation
    const tabLinks = document.querySelectorAll('.sidebar-menu a');
    const tabContents = document.querySelectorAll('.main-content > div');

    tabLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const tabId = this.getAttribute('data-tab');

            tabContents.forEach(content => {
                content.style.display = 'none';
            });

            tabLinks.forEach(tabLink => {
                tabLink.classList.remove('active');
            });

            document.getElementById(tabId).style.display = 'block';
            this.classList.add('active');
        });
    });

    // Alert modal functionality
    const alertModal = document.getElementById('alert-modal');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const modalMessage = document.getElementById('modal-message');

    function showAlert(title, message, type) {
        const modalTitleElement = alertModal.querySelector('.modal-title');
        const modalIconElement = alertModal.querySelector('.modal-icon i');
        modalTitleElement.textContent = title;
        modalMessage.textContent = message;

        alertModal.className = 'modal'; // Reset classes
        alertModal.classList.add(type === 'danger' ? 'alert-danger' : (type === 'warning' ? 'alert-warning' : ''));

        modalIconElement.className = `fas fa-${type === 'danger' ? 'exclamation-triangle' : (type === 'warning' ? 'exclamation-circle' : 'info-circle')}`;

        alertModal.style.display = 'flex';
    }

    modalCloseBtn.addEventListener('click', () => {
        alertModal.style.display = 'none';
        document.getElementById('fix-progress-steps').style.display = 'none';
        // Reset progress steps
        document.querySelectorAll('.step-status').forEach(el => {
            el.textContent = '';
            el.className = 'step-status step-pending';
        });
    });

    window.addEventListener('click', (event) => {
        if (event.target === alertModal) {
            alertModal.style.display = 'none';
            document.getElementById('fix-progress-steps').style.display = 'none';
            // Reset progress steps
            document.querySelectorAll('.step-status').forEach(el => {
                el.textContent = '';
                el.className = 'step-status step-pending';
            });
        }
    });
});

const gasData = [], smokeData = [], tempData = [], timeLabels = [];
const maxPoints = 10;

function showAnalytics() {
    document.getElementById("analytics-content").style.display = "block";
    if (document.getElementById("gasChart").children.length === 0) {
        initCharts();
    }
}

function initCharts() {
    Plotly.newPlot('gasChart', [{
        x: timeLabels, y: gasData, mode: 'lines+markers', line: { color: '#3498db' }, fill: 'tozeroy'
    }], { title: 'Gas Level (%)' });

    Plotly.newPlot('smokeChart', [{
        x: timeLabels, y: smokeData, mode: 'lines+markers', line: { color: '#9b59b6' }, fill: 'tozeroy'
    }], { title: 'Smoke Density (%)' });

    Plotly.newPlot('tempChart', [{
        x: timeLabels, y: tempData, mode: 'lines+markers', line: { color: '#e67e22' }, fill: 'tozeroy'
    }], { title: 'Temperature (°C)' });
}

function addDataToCharts(gas, smoke, temp) {
    const now = new Date().toLocaleTimeString();
    timeLabels.push(now);
    gasData.push(gas);
    smokeData.push(smoke);
    tempData.push(temp);
    if (timeLabels.length > maxPoints) {
        timeLabels.shift(); gasData.shift(); smokeData.shift(); tempData.shift();
    }
    Plotly.update('gasChart', { x: [timeLabels], y: [gasData] });
    Plotly.update('smokeChart', { x: [timeLabels], y: [smokeData] });
    Plotly.update('tempChart', { x: [timeLabels], y: [tempData] });
}
function getRandomValue(min, max) {
    return Math.random() * (max - min) + min;
}
showAnalytics();

setInterval(() => {
    addDataToCharts(gasLevel, smokeLevel, temperature);
}, 1000);
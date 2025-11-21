from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Dashboard"])

html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EcoTrack Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; background: #f4f4f9; color: #333; }
        header { background: #2c3e50; color: white; padding: 1rem; display: flex; justify-content: space-between; align-items: center; }
        .container { padding: 20px; max-width: 1200px; margin: 0 auto; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        h2, h3 { margin-top: 0; color: #2c3e50; }
        
        /* Formulaires */
        .form-group { margin-bottom: 10px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, button, select { padding: 10px; width: 100%; box-sizing: border-box; border-radius: 4px; border: 1px solid #ddd; }
        
        /* Boutons */
        button { background: #27ae60; color: white; border: none; cursor: pointer; font-weight: bold; margin-top: 5px;}
        button:hover { background: #219150; }
        button.delete-btn { background: #e74c3c; width: auto; padding: 5px 10px; font-size: 0.9em; }
        button.delete-btn:hover { background: #c0392b; }
        
        /* Tableau */
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; }
        
        /* Utilitaires */
        .hidden { display: none; }
        .error { color: #e74c3c; margin-top: 10px; font-weight: bold; }
        .success { color: #27ae60; margin-top: 10px; font-weight: bold; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>

<header>
    <h1> EcoTrack Dashboard</h1>
    <div id="userInfo" class="hidden">
        <span id="userEmail"></span>
        <button onclick="logout()" style="background: #c0392b; width: auto; margin-left: 10px;">Déconnexion</button>
    </div>
</header>

<div class="container">
    
    <!-- SECTION 1: LOGIN -->
    <div id="loginSection" class="card" style="max-width: 400px; margin: 50px auto;">
        <h2> Connexion</h2>
        <div class="form-group">
            <label>Email</label>
            <input type="text" id="email" value="student@ecotrack.com">
        </div>
        <div class="form-group">
            <label>Mot de passe</label>
            <input type="password" id="password" value="password123">
        </div>
        <button onclick="login()">Se connecter</button>
        <div id="loginError" class="error"></div>
    </div>

    <!-- SECTION 2: DASHBOARD -->
    <div id="dashboardSection" class="hidden">
        
        <div class="grid">
            <!-- Formulaire d'ajout (Requirement: "Formulaire pour créer un élément") -->
            <div class="card">
                <h3> Ajouter une mesure (Admin)</h3>
                <div class="form-group">
                    <label>Zone ID (ex: 1 pour Paris)</label>
                    <input type="number" id="newZoneId" value="1">
                </div>
                <div class="form-group">
                    <label>Type</label>
                    <select id="newType">
                        <option value="temperature">Température</option>
                        <option value="electricity_consumption">Électricité</option>
                        <option value="air_quality_pm25">Qualité Air</option>
                    </select>
                </div>
                <div class="form-group">
                    <div class="grid" style="gap: 10px;">
                        <input type="number" id="newValue" placeholder="Valeur (ex: 22.5)" step="0.1">
                        <input type="text" id="newUnit" placeholder="Unité (ex: °C)">
                    </div>
                </div>
                <button onclick="createIndicator()">Ajouter</button>
                <div id="createMsg"></div>
            </div>

            <!-- Filtres -->
            <div class="card">
                <h3> Filtres</h3>
                <label>Zone</label>
                <select id="filterZone" onchange="fetchIndicators()">
                    <option value="">Toutes les zones</option>
                    <option value="1">Paris (ID: 1)</option>
                </select>
                <label style="margin-top: 10px;">Type d'indicateur</label>
                <select id="filterType" onchange="fetchIndicators()">
                    <option value="">Tous les types</option>
                    <option value="temperature">Température</option>
                    <option value="electricity_consumption">Électricité</option>
                    <option value="air_quality_pm25">Qualité Air</option>
                </select>
                <button onclick="fetchIndicators()" style="background: #3498db; margin-top: 15px;">Actualiser</button>
            </div>
        </div>

        <!-- Graphique -->
        <div class="card">
            <h3> Évolution Temporelle</h3>
            <canvas id="myChart" style="max-height: 300px;"></canvas>
        </div>

        <!-- Tableau de données -->
        <div class="card">
            <h3> Derniers Relevés</h3>
            <table id="dataTable">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Zone</th>
                        <th>Type</th>
                        <th>Valeur</th>
                        <th>Unité</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
</div>

<script>
    const API_URL = "http://127.0.0.1:8000";
    let myChart = null;

    // Init
    window.onload = () => {
        const token = localStorage.getItem("token");
        if (token) showDashboard();
    };

    // --- AUTHENTIFICATION ---
    async function login() {
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const errorDiv = document.getElementById("loginError");

        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            if (!response.ok) throw new Error("Login failed");

            const data = await response.json();
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("email", email);
            showDashboard();
        } catch (err) {
            errorDiv.textContent = "Erreur : Identifiants incorrects.";
        }
    }

    function logout() {
        localStorage.removeItem("token");
        localStorage.removeItem("email");
        location.reload();
    }

    function showDashboard() {
        document.getElementById("loginSection").classList.add("hidden");
        document.getElementById("dashboardSection").classList.remove("hidden");
        document.getElementById("userInfo").classList.remove("hidden");
        document.getElementById("userEmail").textContent = localStorage.getItem("email");
        fetchIndicators();
    }

    // --- LECTURE DES DONNÉES (GET) ---
    async function fetchIndicators() {
        const token = localStorage.getItem("token");
        const zoneId = document.getElementById("filterZone").value;
        const type = document.getElementById("filterType").value;

        let url = `${API_URL}/indicators/?limit=50`;
        if (zoneId) url += `&zone_id=${zoneId}`;
        if (type) url += `&type=${type}`;

        try {
            const response = await fetch(url, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.status === 401) { logout(); return; }
            
            const data = await response.json();
            updateTable(data);
            updateChart(data);
        } catch (e) {
            console.error("Erreur fetch:", e);
        }
    }

    function updateTable(data) {
        const tbody = document.querySelector("#dataTable tbody");
        tbody.innerHTML = "";
        data.forEach(item => {
            const date = new Date(item.timestamp).toLocaleString();
            const row = `<tr>
                <td>${date}</td>
                <td>${item.zone_id}</td>
                <td>${item.type}</td>
                <td><strong>${item.value}</strong></td>
                <td>${item.unit}</td>
                <td><button class="delete-btn" onclick="deleteIndicator(${item.id})">Supprimer</button></td>
            </tr>`;
            tbody.innerHTML += row;
        });
    }

    function updateChart(data) {
        const ctx = document.getElementById('myChart').getContext('2d');
        const chartData = [...data].reverse(); // Chronologique
        
        if (myChart) myChart.destroy();

        myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.map(d => new Date(d.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})),
                datasets: [{
                    label: 'Valeur',
                    data: chartData.map(d => d.value),
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // --- CRÉATION (POST) ---
    async function createIndicator() {
        const token = localStorage.getItem("token");
        const msgDiv = document.getElementById("createMsg");
        
        const payload = {
            zone_id: parseInt(document.getElementById("newZoneId").value),
            type: document.getElementById("newType").value,
            value: parseFloat(document.getElementById("newValue").value),
            unit: document.getElementById("newUnit").value
        };

        if (!payload.value || !payload.unit) {
            msgDiv.innerHTML = "<span class='error'>Remplissez tous les champs !</span>";
            return;
        }

        const response = await fetch(`${API_URL}/indicators/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            msgDiv.innerHTML = "<span class='success'>Ajouté avec succès !</span>";
            fetchIndicators(); // Rafraîchir la liste
        } else {
            const err = await response.json();
            // Gestion d'erreur 403 si pas admin
            if (response.status === 403) {
                 msgDiv.innerHTML = "<span class='error'>Erreur : Réservé aux Admins !</span>";
            } else {
                 msgDiv.innerHTML = `<span class='error'>Erreur : ${err.detail}</span>`;
            }
        }
    }

    // --- SUPPRESSION (DELETE) ---
    async function deleteIndicator(id) {
        if (!confirm("Voulez-vous vraiment supprimer ce relevé ?")) return;
        
        const token = localStorage.getItem("token");
        const response = await fetch(`${API_URL}/indicators/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            fetchIndicators();
        } else {
            alert("Erreur : Impossible de supprimer (Êtes-vous Admin ?)");
        }
    }
</script>

</body>
</html>
"""

@router.get("/dashboard", response_class=HTMLResponse)
def read_dashboard():
    return html_content
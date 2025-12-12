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
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background-color: #f3f4f6; font-family: 'Segoe UI', sans-serif; }
        .hidden { display: none; }
        .card { background: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .tab-active { border-bottom: 2px solid #2563eb; color: #2563eb; font-weight: bold; }
        .tab-inactive { color: #6b7280; cursor: pointer; }
    </style>
</head>
<body class="text-slate-800">

    <!-- --- AUTH SECTION (LOGIN / REGISTER) --- -->
    <div id="authSection" class="min-h-screen flex items-center justify-center">
        <div class="card w-full max-w-md space-y-6">
            
            <!-- Tabs -->
            <div class="flex border-b border-gray-200">
                <div id="tabLogin" onclick="switchAuthMode('login')" class="w-1/2 py-2 text-center tab-active cursor-pointer">Connexion</div>
                <div id="tabRegister" onclick="switchAuthMode('register')" class="w-1/2 py-2 text-center tab-inactive hover:text-blue-500">Inscription</div>
            </div>

            <h1 id="authTitle" class="text-2xl font-bold text-center text-slate-700">Bienvenue sur EcoTrack</h1>

            <!-- Form -->
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-slate-700">Email</label>
                    <input type="text" id="email" placeholder="exemple@ecotrack.com" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border focus:ring-blue-500 focus:border-blue-500">
                </div>
                <div>
                    <label class="block text-sm font-medium text-slate-700">Mot de passe</label>
                    <input type="password" id="password" placeholder="********" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border focus:ring-blue-500 focus:border-blue-500">
                </div>

                <!-- Champ Role (Visible seulement en Inscription) -->
                <div id="roleField" class="hidden">
                    <label class="block text-sm font-medium text-slate-700">Rôle souhaité</label>
                    <select id="roleSelect" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border bg-white focus:ring-blue-500 focus:border-blue-500">
                        <option value="user">Utilisateur (Consultation)</option>
                        <option value="admin">Administrateur (Gestion complète)</option>
                    </select>
                </div>

                <button id="authButton" onclick="handleAuth()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition">
                    Se connecter
                </button>
                
                <!-- Feedback Messages -->
                <div id="authMessage" class="hidden p-2 rounded text-sm text-center"></div>
            </div>
        </div>
    </div>

    <!-- --- DASHBOARD SECTION --- -->
    <div id="dashboardSection" class="hidden min-h-screen pb-10">
        <!-- Navbar -->
        <nav class="bg-slate-800 text-white shadow-lg mb-8">
            <div class="max-w-7xl mx-auto px-4 py-4 flex flex-col md:flex-row justify-between items-center gap-4">
                <div class="flex items-center gap-3">
                    <span class="text-xl font-bold text-green-400">EcoTrack Monitor</span>
                    <span id="roleBadge" class="text-xs font-bold px-2 py-1 rounded bg-gray-600 text-gray-200 uppercase tracking-wider">Chargement...</span>
                </div>
                <div class="flex items-center gap-4">
                    <!-- Zone dynamique des boutons (Demander Admin uniquement) -->
                    <div id="roleActions"></div>
                    <span id="userEmail" class="text-sm text-slate-300 hidden md:inline opacity-75"></span>
                    <button onclick="logout()" class="bg-red-500 hover:bg-red-600 px-3 py-1 rounded text-sm font-semibold transition">Déconnexion</button>
                </div>
            </div>
        </nav>

        <main class="max-w-7xl mx-auto px-4 space-y-6">
            <!-- Graphs & Tables -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="card flex flex-col items-center">
                    <h3 class="text-lg font-bold text-slate-700 mb-4 w-full text-left">Répartition par Type</h3>
                    <div class="w-64 h-64 relative"><canvas id="distributionChart"></canvas></div>
                </div>
                <div class="card flex flex-col justify-center">
                    <h3 class="text-lg font-bold text-slate-700 mb-4">Filtres</h3>
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-slate-600">Zone</label>
                            <select id="filterZone" class="w-full border rounded p-2 mt-1 bg-slate-50" onchange="fetchIndicators()">
                                <option value="">Toutes les zones</option>
                                <option value="1">Paris (ID: 1)</option>
                                <option value="2">Lyon (ID: 2)</option>
                                <option value="3">Marseille (ID: 3)</option>
                            </select>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-slate-600">Période</label>
                                <select id="filterPeriod" class="w-full border rounded p-2 mt-1 bg-slate-50" onchange="applyClientFilters()">
                                    <option value="all">Tout l'historique</option>
                                    <option value="day">Aujourd'hui</option>
                                    <option value="week">7 derniers jours</option>
                                    <option value="month">30 derniers jours</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-slate-600">Type</label>
                                <select id="filterType" class="w-full border rounded p-2 mt-1 bg-slate-50" onchange="applyClientFilters()">
                                    <option value="">Tous les types</option>
                                    <option value="temperature">Température</option>
                                    <option value="electricity_consumption">Électricité</option>
                                    <option value="air_quality_pm25">Qualité Air</option>
                                </select>
                            </div>
                        </div>
                        <button onclick="fetchIndicators()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded transition">Actualiser les données (API)</button>
                    </div>
                </div>
            </div>
            <div class="card">
                <h3 class="text-lg font-bold text-slate-700 mb-4">Évolution Temporelle</h3>
                <div class="h-72 w-full"><canvas id="evolutionChart"></canvas></div>
            </div>
            <div class="card overflow-hidden">
                <h3 class="text-lg font-bold text-slate-700 mb-4">Derniers Relevés</h3>
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-slate-200">
                        <thead class="bg-slate-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase">Date</th>
                                <th class="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase">Zone</th>
                                <th class="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase">Type</th>
                                <th class="px-6 py-3 text-right text-xs font-bold text-slate-500 uppercase">Valeur</th>
                                <th class="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase">Unité</th>
                            </tr>
                        </thead>
                        <tbody id="tableBody" class="bg-white divide-y divide-slate-200"></tbody>
                    </table>
                </div>
                <div id="showMoreContainer" class="text-center mt-4 hidden">
                    <button onclick="showMore()" class="text-blue-600 hover:text-blue-800 font-semibold text-sm">▼ Afficher plus de résultats</button>
                </div>
            </div>
        </main>
    </div>

    <script>
        const API_URL = "http://127.0.0.1:8000";
        let rawApiData = [], filteredData = [], statsData = [];
        let displayedCount = 10;
        let currentUser = null;
        let isLoginMode = true;

        // --- INIT ---
        window.onload = () => {
            const token = localStorage.getItem("token");
            if (token) showDashboard();
        };

        // --- AUTH UI LOGIC ---
        function switchAuthMode(mode) {
            const tabLogin = document.getElementById("tabLogin");
            const tabRegister = document.getElementById("tabRegister");
            const authButton = document.getElementById("authButton");
            const roleField = document.getElementById("roleField");
            const msg = document.getElementById("authMessage");

            msg.classList.add("hidden"); 

            if (mode === 'login') {
                isLoginMode = true;
                tabLogin.className = "w-1/2 py-2 text-center tab-active cursor-pointer";
                tabRegister.className = "w-1/2 py-2 text-center tab-inactive hover:text-blue-500";
                authButton.textContent = "Se connecter";
                roleField.classList.add("hidden");
            } else {
                isLoginMode = false;
                tabLogin.className = "w-1/2 py-2 text-center tab-inactive hover:text-blue-500";
                tabRegister.className = "w-1/2 py-2 text-center tab-active cursor-pointer";
                authButton.textContent = "S'inscrire";
                roleField.classList.remove("hidden");
            }
        }

        async function handleAuth() {
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            if (!email || !password) {
                showMessage("Veuillez remplir tous les champs.", "error");
                return;
            }

            if (isLoginMode) {
                // LOGIN
                const formData = new URLSearchParams();
                formData.append('username', email);
                formData.append('password', password);

                try {
                    const res = await fetch(`${API_URL}/auth/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: formData
                    });

                    if (res.ok) {
                        const data = await res.json();
                        localStorage.setItem("token", data.access_token);
                        localStorage.setItem("email", email);
                        showDashboard();
                    } else {
                        showMessage("Email ou mot de passe incorrect.", "error");
                    }
                } catch (e) {
                    showMessage("Erreur de connexion au serveur.", "error");
                }

            } else {
                // REGISTER
                const role = document.getElementById("roleSelect").value;
                const payload = {
                    email: email,
                    password: password,
                    role: role 
                };

                try {
                    const res = await fetch(`${API_URL}/users/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });

                    if (res.ok) {
                        showMessage("Compte créé avec succès ! Connectez-vous.", "success");
                        setTimeout(() => switchAuthMode('login'), 1500);
                    } else {
                        const err = await res.json();
                        showMessage(`Erreur : ${err.detail || "Inscription impossible"}`, "error");
                    }
                } catch (e) {
                    showMessage("Erreur de connexion au serveur.", "error");
                }
            }
        }

        function showMessage(text, type) {
            const msg = document.getElementById("authMessage");
            msg.textContent = text;
            msg.classList.remove("hidden", "bg-red-100", "text-red-700", "bg-green-100", "text-green-700");
            
            if (type === "error") {
                msg.classList.add("bg-red-100", "text-red-700");
            } else {
                msg.classList.add("bg-green-100", "text-green-700");
            }
        }

        function logout() {
            localStorage.clear();
            location.reload();
        }

        // --- DASHBOARD LOGIC ---
        async function fetchUserProfile() {
            try {
                const res = await fetch(`${API_URL}/users/me`, { headers: { 'Authorization': `Bearer ${localStorage.getItem("token")}` } });
                if (res.ok) { currentUser = await res.json(); updateUserUI(); }
            } catch (e) {}
        }

        function updateUserUI() {
            if (!currentUser) return;
            document.getElementById("userEmail").textContent = currentUser.email;
            
            // Badge
            const badge = document.getElementById("roleBadge");
            const isAdmin = currentUser.role === 'admin';
            badge.textContent = isAdmin ? "ADMINISTRATEUR" : "UTILISATEUR";
            badge.className = isAdmin ? "text-xs font-bold px-2 py-1 rounded bg-yellow-500 text-white uppercase tracking-wider shadow-sm" : "text-xs font-bold px-2 py-1 rounded bg-blue-500 text-white uppercase tracking-wider shadow-sm";
            
            // Boutons d'action
            const actionsDiv = document.getElementById("roleActions");
            actionsDiv.innerHTML = "";
            
            // Suppression du Switch Admin/User. 
            // On garde seulement "Demander Admin" pour les users simples au cas où.
            if (!isAdmin) {
                actionsDiv.innerHTML = `<button onclick="askAdmin()" class="bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-1 rounded text-sm font-bold transition shadow">✋ Demander Admin</button>`;
            }
        }

        async function askAdmin() {
            const res = await fetch(`${API_URL}/users/me/request-admin`, { method: 'POST', headers: {'Authorization': `Bearer ${localStorage.getItem("token")}`} });
            if(res.ok) alert("Demande envoyée");
        }

        function showDashboard() {
            document.getElementById("authSection").classList.add("hidden");
            document.getElementById("dashboardSection").classList.remove("hidden");
            fetchUserProfile();
            fetchIndicators();
        }

        // --- DATA & GRAPHS ---
        async function fetchIndicators() {
            const z = document.getElementById("filterZone").value;
            let url = `${API_URL}/indicators/?limit=1000${z ? '&zone_id='+z : ''}`;
            try {
                const res = await fetch(url, { headers: { 'Authorization': `Bearer ${localStorage.getItem("token")}` } });
                if(res.status === 401) { logout(); return; }
                rawApiData = await res.json();
                applyClientFilters();
            } catch(e){}
        }

        function applyClientFilters() {
            const period = document.getElementById("filterPeriod").value;
            const type = document.getElementById("filterType").value;
            const now = new Date(); const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            let timeFiltered = rawApiData.filter(i => {
                const d = new Date(i.timestamp);
                if(period==='day') return d>=startOfDay;
                if(period==='week') return d>=new Date(now.setDate(now.getDate()-7));
                if(period==='month') return d>=new Date(now.setDate(now.getDate()-30));
                return true;
            });
            statsData = [...timeFiltered];
            filteredData = type ? timeFiltered.filter(i=>(i.indicator_type||i.type)===type) : [...timeFiltered];
            displayedCount = 10;
            renderTable(); renderCharts();
        }

        function renderTable() {
            const tbody = document.getElementById("tableBody"); tbody.innerHTML="";
            const data = filteredData.slice(0, displayedCount);
            if(!data.length) tbody.innerHTML=`<tr><td colspan="5" class="text-center py-4 text-slate-500">Aucune donnée</td></tr>`;
            data.forEach(i => {
                tbody.insertAdjacentHTML('beforeend', `<tr class="hover:bg-slate-50 transition"><td class="px-6 py-4 text-sm text-slate-700">${new Date(i.timestamp).toLocaleString()}</td><td class="px-6 py-4 text-sm text-slate-600"><span class="bg-gray-100 px-2 py-1 rounded text-xs font-bold">Zone ${i.zone_id}</span></td><td class="px-6 py-4 text-sm text-slate-600">${i.indicator_type||i.type}</td><td class="px-6 py-4 text-sm font-bold text-slate-900 text-right">${i.value}</td><td class="px-6 py-4 text-sm text-slate-500">${i.unit}</td></tr>`);
            });
            document.getElementById("showMoreContainer").classList.toggle("hidden", filteredData.length <= displayedCount);
        }
        function showMore() { displayedCount+=10; renderTable(); }

        let chartEvo, chartDist;
        function renderCharts() {
            const ctxEvo = document.getElementById('evolutionChart').getContext('2d');
            const chrono = [...filteredData].reverse();
            if(chartEvo) chartEvo.destroy();
            chartEvo = new Chart(ctxEvo, { type:'line', data:{labels:chrono.map(d=>new Date(d.timestamp).toLocaleTimeString()), datasets:[{label:'Valeur', data:chrono.map(d=>d.value), borderColor:'#2563eb', backgroundColor:'rgba(37,99,235,0.1)', fill:true}]}, options:{maintainAspectRatio:false}});

            const ctxDist = document.getElementById('distributionChart').getContext('2d');
            const counts={}; statsData.forEach(d=>{const t=d.indicator_type||d.type; counts[t]=(counts[t]||0)+1;});
            if(chartDist) chartDist.destroy();
            chartDist = new Chart(ctxDist, {type:'doughnut', data:{labels:Object.keys(counts), datasets:[{data:Object.values(counts), backgroundColor:['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6']}]}, options:{maintainAspectRatio:false, plugins:{legend:{position:'bottom'}}}});
        }
    </script>
</body>
</html>
"""

@router.get("/dashboard", response_class=HTMLResponse)
def read_dashboard():
    return html_content



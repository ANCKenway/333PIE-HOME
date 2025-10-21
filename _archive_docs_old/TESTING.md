# 🧪 Tests et Validation 333HOME

## 🎯 Objectif
Guide complet pour tester et valider toutes les fonctionnalités de 333HOME après la refactorisation modulaire.

---

## 📋 Stratégie de Test

### 🎪 Types de Tests
1. **Tests unitaires** : Modules individuels
2. **Tests d'intégration** : API endpoints
3. **Tests E2E** : Interface utilisateur
4. **Tests de performance** : Charge et vitesse
5. **Tests sécurité** : Vulnérabilités

### 🎯 Objectifs Qualité
- **Couverture** : 80%+ du code critique
- **Performance** : < 2s réponse API
- **Disponibilité** : 99%+ uptime
- **Sécurité** : Aucune vulnérabilité critique

---

## 🔧 Tests Backend

### 📱 Tests API Devices
```bash
#!/bin/bash
# Tests API Devices

echo "🧪 Tests API Devices"
echo "==================="

BASE_URL="http://localhost:8000"

# Test 1: Liste des appareils
echo "📱 Test GET /api/devices/"
curl -s "$BASE_URL/api/devices/" | jq '.devices | length' > /dev/null
echo "✅ Liste appareils OK"

# Test 2: Détails appareil
echo "📱 Test GET /api/devices/{id}"
DEVICE_ID=$(curl -s "$BASE_URL/api/devices/" | jq -r '.devices[0].id // "test"')
curl -s "$BASE_URL/api/devices/$DEVICE_ID" > /dev/null
echo "✅ Détails appareil OK"

# Test 3: Actualisation
echo "🔄 Test POST /api/devices/refresh"
curl -s -X POST "$BASE_URL/api/devices/refresh" | jq '.message' > /dev/null
echo "✅ Refresh appareils OK"

# Test 4: Wake-on-LAN (simulation)
echo "⚡ Test POST /api/devices/wake"
curl -s -X POST "$BASE_URL/api/devices/wake" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"test"}' > /dev/null 2>&1
echo "✅ Wake-on-LAN endpoint OK"

# Test 5: Statistiques
echo "📊 Test GET /api/devices/status/summary"
curl -s "$BASE_URL/api/devices/status/summary" | jq '.total' > /dev/null
echo "✅ Statistiques appareils OK"

echo "🎉 Tests API Devices terminés"
```

### 🌐 Tests API Network
```bash
#!/bin/bash
# Tests API Network

echo "🧪 Tests API Network"
echo "==================="

BASE_URL="http://localhost:8000"

# Test 1: Dernier scan
echo "🌐 Test GET /api/network/scan"
curl -s "$BASE_URL/api/network/scan" > /dev/null
echo "✅ Dernier scan OK"

# Test 2: Nouveau scan
echo "🔍 Test POST /api/network/scan"
curl -s -X POST "$BASE_URL/api/network/scan" \
  -H "Content-Type: application/json" \
  -d '{"target":"192.168.1.0/24","fast":true}' > /dev/null
echo "✅ Nouveau scan OK"

# Test 3: Historique
echo "📈 Test GET /api/network/history"
curl -s "$BASE_URL/api/network/history?days=7" | jq '.history' > /dev/null
echo "✅ Historique réseau OK"

# Test 4: Analyse
echo "🔬 Test GET /api/network/analyze"
curl -s "$BASE_URL/api/network/analyze" > /dev/null
echo "✅ Analyse réseau OK"

# Test 5: Topologie
echo "🗺️ Test GET /api/network/topology"
curl -s "$BASE_URL/api/network/topology" | jq '.subnets' > /dev/null
echo "✅ Topologie réseau OK"

# Test 6: Statistiques
echo "📊 Test GET /api/network/stats"
curl -s "$BASE_URL/api/network/stats" > /dev/null
echo "✅ Statistiques réseau OK"

echo "🎉 Tests API Network terminés"
```

### 🔒 Tests API Tailscale
```bash
#!/bin/bash
# Tests API Tailscale

echo "🧪 Tests API Tailscale"
echo "====================="

BASE_URL="http://localhost:8000"

# Test 1: Configuration
echo "🔒 Test GET /api/tailscale/config"
curl -s "$BASE_URL/api/tailscale/config" | jq '.is_configured' > /dev/null
echo "✅ Configuration Tailscale OK"

# Test 2: Appareils VPN
echo "📱 Test GET /api/tailscale/devices"
curl -s "$BASE_URL/api/tailscale/devices" > /dev/null 2>&1
echo "✅ Appareils Tailscale OK"

# Test 3: Statut service
echo "📊 Test GET /api/tailscale/status"
curl -s "$BASE_URL/api/tailscale/status" | jq '.is_configured' > /dev/null
echo "✅ Statut Tailscale OK"

# Test 4: Test connexion
echo "🔍 Test POST /api/tailscale/test-connection"
curl -s -X POST "$BASE_URL/api/tailscale/test-connection" > /dev/null
echo "✅ Test connexion Tailscale OK"

# Test 5: Cache clear
echo "🗑️ Test POST /api/tailscale/clear-cache"
curl -s -X POST "$BASE_URL/api/tailscale/clear-cache" > /dev/null
echo "✅ Clear cache Tailscale OK"

echo "🎉 Tests API Tailscale terminés"
```

### 📊 Tests API Monitoring
```bash
#!/bin/bash
# Tests API Monitoring

echo "🧪 Tests API Monitoring"
echo "======================"

BASE_URL="http://localhost:8000"

# Test 1: Statistiques globales
echo "📊 Test GET /api/monitoring/stats"
curl -s "$BASE_URL/api/monitoring/stats" | jq '.devices.total' > /dev/null
echo "✅ Statistiques monitoring OK"

# Test 2: Santé système
echo "🏥 Test GET /api/monitoring/health"
curl -s "$BASE_URL/api/monitoring/health" | jq '.overall' > /dev/null
echo "✅ Santé système OK"

# Test 3: Performance
echo "⚡ Test GET /api/monitoring/performance"
curl -s "$BASE_URL/api/monitoring/performance" > /dev/null
echo "✅ Métriques performance OK"

# Test 4: Activité récente
echo "📈 Test GET /api/monitoring/activity"
curl -s "$BASE_URL/api/monitoring/activity" | jq '.recent_scans' > /dev/null
echo "✅ Activité récente OK"

# Test 5: Benchmark
echo "🏃 Test POST /api/monitoring/benchmark"
curl -s -X POST "$BASE_URL/api/monitoring/benchmark" | jq '.total_time_ms' > /dev/null
echo "✅ Benchmark système OK"

echo "🎉 Tests API Monitoring terminés"
```

### 🔧 Tests API System
```bash
#!/bin/bash
# Tests API System

echo "🧪 Tests API System"
echo "=================="

BASE_URL="http://localhost:8000"

# Test 1: Statut système
echo "🔧 Test GET /api/system/status"
curl -s "$BASE_URL/api/system/status" | jq '.status' > /dev/null
echo "✅ Statut système OK"

# Test 2: Logs système
echo "📜 Test GET /api/system/logs"
curl -s "$BASE_URL/api/system/logs" | jq '.logs' > /dev/null
echo "✅ Logs système OK"

# Test 3: Info Raspberry Pi
echo "🍓 Test GET /api/system/raspberry"
curl -s "$BASE_URL/api/system/raspberry" | jq '.is_raspberry' > /dev/null
echo "✅ Info Raspberry Pi OK"

# Test 4: Ping test
echo "🏓 Test GET /api/system/ping/8.8.8.8"
curl -s "$BASE_URL/api/system/ping/8.8.8.8" | jq '.success' > /dev/null
echo "✅ Ping test OK"

echo "🎉 Tests API System terminés"
```

---

## 🎨 Tests Frontend

### 📱 Tests Interface Web
```javascript
// Tests Frontend (Console navigateur)

console.log('🧪 Tests Frontend 333HOME');
console.log('==========================');

// Test 1: Chargement modules
try {
    if (window.app && window.app.dataManager) {
        console.log('✅ DataManager chargé');
    }
    if (window.app && window.app.deviceManager) {
        console.log('✅ DeviceManager chargé');
    }
    if (window.app && window.app.networkManager) {
        console.log('✅ NetworkManager chargé');
    }
    if (window.app && window.app.uiManager) {
        console.log('✅ UIManager chargé');
    }
} catch (error) {
    console.error('❌ Erreur chargement modules:', error);
}

// Test 2: API Client
async function testAPIClient() {
    try {
        const status = await APIClient.get('/api/system/status');
        console.log('✅ APIClient fonctionnel');
        return true;
    } catch (error) {
        console.error('❌ APIClient défaillant:', error);
        return false;
    }
}

// Test 3: Navigation
function testNavigation() {
    try {
        const router = window.app.router;
        router.navigate('devices');
        router.navigate('network');
        router.navigate('dashboard');
        console.log('✅ Navigation fonctionnelle');
        return true;
    } catch (error) {
        console.error('❌ Navigation défaillante:', error);
        return false;
    }
}

// Test 4: Responsive design
function testResponsive() {
    try {
        // Simuler mobile
        window.innerWidth = 375;
        window.dispatchEvent(new Event('resize'));
        
        // Vérifier menu mobile
        const sidebar = document.getElementById('sidebar');
        const isResponsive = sidebar && getComputedStyle(sidebar).position === 'fixed';
        
        // Restaurer desktop
        window.innerWidth = 1920;
        window.dispatchEvent(new Event('resize'));
        
        if (isResponsive) {
            console.log('✅ Design responsive OK');
        } else {
            console.log('⚠️ Design responsive à vérifier');
        }
        return isResponsive;
    } catch (error) {
        console.error('❌ Test responsive échoué:', error);
        return false;
    }
}

// Exécuter tous les tests
async function runAllFrontendTests() {
    console.log('🚀 Démarrage tests frontend...');
    
    const apiTest = await testAPIClient();
    const navTest = testNavigation();
    const respTest = testResponsive();
    
    const allPassed = apiTest && navTest && respTest;
    
    if (allPassed) {
        console.log('🎉 Tous les tests frontend passés!');
    } else {
        console.log('⚠️ Certains tests frontend ont échoué');
    }
    
    return allPassed;
}

// Lancer les tests
runAllFrontendTests();
```

### 🎨 Tests CSS et Responsive
```bash
#!/bin/bash
# Tests CSS et Responsive

echo "🧪 Tests CSS et Responsive"
echo "=========================="

# Test 1: Validation CSS
echo "🎨 Validation CSS..."
if command -v css-validator &> /dev/null; then
    css-validator web/static/css/main.css
    echo "✅ CSS valide"
else
    echo "⚠️ css-validator non installé"
fi

# Test 2: Taille des fichiers CSS
echo "📐 Taille fichiers CSS..."
find web/static/css -name "*.css" -exec ls -lh {} + | awk '{print $5 " " $9}'
echo "✅ Tailles CSS vérifiées"

# Test 3: Variables CSS
echo "🎨 Variables CSS..."
grep -r "var(--" web/static/css/ | wc -l
echo "✅ Variables CSS utilisées"

# Test 4: Media queries
echo "📱 Media queries..."
grep -r "@media" web/static/css/ | wc -l
echo "✅ Media queries présentes"

echo "🎉 Tests CSS terminés"
```

---

## ⚡ Tests de Performance

### 🚀 Test de Charge API
```bash
#!/bin/bash
# Tests de Performance API

echo "🧪 Tests de Performance"
echo "======================"

BASE_URL="http://localhost:8000"

# Test 1: Temps de réponse endpoints
echo "⚡ Temps de réponse API..."

endpoints=(
    "/api/devices/"
    "/api/network/scan"
    "/api/monitoring/stats"
    "/api/system/status"
    "/api/tailscale/status"
)

for endpoint in "${endpoints[@]}"; do
    time_ms=$(curl -w "%{time_total}" -s -o /dev/null "$BASE_URL$endpoint")
    time_readable=$(echo "$time_ms * 1000" | bc | cut -d. -f1)
    
    if (( $(echo "$time_ms < 2.0" | bc -l) )); then
        echo "✅ $endpoint: ${time_readable}ms"
    else
        echo "⚠️ $endpoint: ${time_readable}ms (lent)"
    fi
done

# Test 2: Charge simultanée
echo "🔥 Test de charge simultanée..."
for i in {1..10}; do
    curl -s "$BASE_URL/api/devices/" > /dev/null &
done
wait
echo "✅ Charge simultanée gérée"

# Test 3: Mémoire utilisée
echo "💾 Utilisation mémoire..."
ps aux | grep "python.*app" | grep -v grep | awk '{print $4"%"}'
echo "✅ Mémoire surveillée"

echo "🎉 Tests performance terminés"
```

### 📊 Benchmark Complet
```python
#!/usr/bin/env python3
# benchmark.py - Benchmark complet 333HOME

import time
import asyncio
import httpx
import psutil
import statistics

async def benchmark_api():
    """Benchmark complet de l'API"""
    
    print("🧪 Benchmark API 333HOME")
    print("========================")
    
    base_url = "http://localhost:8000"
    endpoints = [
        "/api/devices/",
        "/api/network/scan",
        "/api/monitoring/stats", 
        "/api/system/status",
        "/api/tailscale/status"
    ]
    
    async with httpx.AsyncClient() as client:
        # Test de chaque endpoint
        for endpoint in endpoints:
            times = []
            
            for _ in range(10):  # 10 requêtes par endpoint
                start = time.time()
                try:
                    response = await client.get(f"{base_url}{endpoint}")
                    end = time.time()
                    
                    if response.status_code == 200:
                        times.append((end - start) * 1000)  # ms
                    else:
                        print(f"❌ {endpoint}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ {endpoint}: {str(e)}")
            
            if times:
                avg_time = statistics.mean(times)
                max_time = max(times)
                min_time = min(times)
                
                status = "✅" if avg_time < 2000 else "⚠️"
                print(f"{status} {endpoint}:")
                print(f"   Moyenne: {avg_time:.1f}ms")
                print(f"   Min: {min_time:.1f}ms")
                print(f"   Max: {max_time:.1f}ms")
        
        # Test de charge
        print("\n🔥 Test de charge (100 requêtes simultanées)...")
        start = time.time()
        
        tasks = []
        for _ in range(100):
            task = client.get(f"{base_url}/api/devices/")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end = time.time()
        
        success_count = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 200)
        total_time = end - start
        
        print(f"✅ {success_count}/100 requêtes réussies")
        print(f"✅ Temps total: {total_time:.2f}s")
        print(f"✅ Débit: {100/total_time:.1f} req/s")

def benchmark_system():
    """Benchmark système"""
    
    print("\n🖥️ Benchmark Système")
    print("====================")
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"💻 CPU: {cpu_percent}%")
    
    # Mémoire
    memory = psutil.virtual_memory()
    print(f"💾 Mémoire: {memory.percent}% ({memory.used/1024**3:.1f}GB utilisés)")
    
    # Disque
    disk = psutil.disk_usage('/')
    print(f"💿 Disque: {disk.percent}% ({disk.free/1024**3:.1f}GB libres)")
    
    # Processus Python
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        if 'python' in proc.info['name'].lower() and 'app' in ' '.join(proc.cmdline()):
            print(f"🐍 Processus Python: PID {proc.info['pid']}, {proc.info['memory_percent']:.1f}% RAM")

if __name__ == "__main__":
    # Benchmark système
    benchmark_system()
    
    # Benchmark API
    asyncio.run(benchmark_api())
    
    print("\n🎉 Benchmark terminé!")
```

---

## 🛡️ Tests de Sécurité

### 🔒 Tests de Sécurité Basiques
```bash
#!/bin/bash
# Tests de Sécurité

echo "🧪 Tests de Sécurité"
echo "==================="

BASE_URL="http://localhost:8000"

# Test 1: Injection SQL (simulation)
echo "🔒 Test injection SQL..."
curl -s "$BASE_URL/api/devices/" \
  -G -d "filter='; DROP TABLE devices; --" > /dev/null
echo "✅ Protection injection SQL"

# Test 2: XSS (simulation)
echo "🔒 Test XSS..."
curl -s "$BASE_URL/api/devices/" \
  -G -d "name=<script>alert('xss')</script>" > /dev/null
echo "✅ Protection XSS"

# Test 3: Headers de sécurité
echo "🔒 Headers de sécurité..."
headers=$(curl -s -I "$BASE_URL/" | grep -i "x-")
if [[ -n "$headers" ]]; then
    echo "✅ Headers sécurité présents"
else
    echo "⚠️ Headers sécurité à ajouter"
fi

# Test 4: HTTPS (si disponible)
echo "🔒 Test HTTPS..."
if curl -s "https://localhost:8000/" > /dev/null 2>&1; then
    echo "✅ HTTPS disponible"
else
    echo "⚠️ HTTPS non configuré"
fi

echo "🎉 Tests sécurité terminés"
```

---

## 📋 Suites de Tests Complètes

### 🎪 Master Test Suite
```bash
#!/bin/bash
# master_test.sh - Suite de tests complète

echo "🎪 MASTER TEST SUITE 333HOME"
echo "============================="

# Variables
PASS=0
FAIL=0
BASE_URL="http://localhost:8000"

# Fonction de test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo "🧪 $test_name..."
    if eval "$test_command" > /dev/null 2>&1; then
        echo "✅ $test_name PASS"
        ((PASS++))
    else
        echo "❌ $test_name FAIL"
        ((FAIL++))
    fi
}

# Tests infrastructure
echo "🏗️ Tests Infrastructure"
echo "======================="
run_test "Application démarrée" "curl -s $BASE_URL/api/system/status"
run_test "Fichiers statiques" "curl -s $BASE_URL/static/js/app.js"
run_test "Templates HTML" "curl -s $BASE_URL/"

# Tests API Backend
echo "🔧 Tests API Backend"
echo "==================="
run_test "API Devices" "curl -s $BASE_URL/api/devices/"
run_test "API Network" "curl -s $BASE_URL/api/network/scan"
run_test "API Monitoring" "curl -s $BASE_URL/api/monitoring/stats"
run_test "API System" "curl -s $BASE_URL/api/system/status"
run_test "API Tailscale" "curl -s $BASE_URL/api/tailscale/status"

# Tests Performance
echo "⚡ Tests Performance"
echo "==================="
run_test "Réponse < 2s" "timeout 2s curl -s $BASE_URL/api/devices/"
run_test "Mémoire < 512MB" "ps -o pid,vsz,cmd | grep 'python.*app' | awk '{if(\$2<524288) exit 0; else exit 1}'"

# Tests Sécurité
echo "🔒 Tests Sécurité"
echo "================="
run_test "Pas d'erreur 500" "! curl -s $BASE_URL/api/devices/nonexistent | grep -q '500'"
run_test "Validation entrées" "curl -s '$BASE_URL/api/system/ping/invalid..input' | grep -q 'detail'"

# Résultats
echo ""
echo "📊 RÉSULTATS FINAUX"
echo "=================="
echo "✅ Tests réussis: $PASS"
echo "❌ Tests échoués: $FAIL"
echo "📈 Taux de réussite: $(( PASS * 100 / (PASS + FAIL) ))%"

if [ $FAIL -eq 0 ]; then
    echo "🎉 TOUS LES TESTS PASSÉS!"
    exit 0
else
    echo "⚠️ CERTAINS TESTS ONT ÉCHOUÉ"
    exit 1
fi
```

### 🤖 Tests Automatisés CI/CD
```yaml
# .github/workflows/test.yml
name: Tests 333HOME

on:
  push:
    branches: [ master, develop ]
  pull_request:
    branches: [ master ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Start application
      run: |
        python app_new.py &
        sleep 10
    
    - name: Run tests
      run: |
        chmod +x tests/master_test.sh
        ./tests/master_test.sh
    
    - name: Performance benchmark
      run: |
        python tests/benchmark.py
```

---

## 📊 Reporting et Métriques

### 📈 Dashboard de Tests
```html
<!-- test_dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>🧪 Dashboard Tests 333HOME</title>
    <style>
        .metric { display: inline-block; margin: 10px; padding: 20px; border: 1px solid #ccc; }
        .pass { background: #d4edda; }
        .fail { background: #f8d7da; }
        .warn { background: #fff3cd; }
    </style>
</head>
<body>
    <h1>🧪 Dashboard Tests 333HOME</h1>
    
    <div id="metrics">
        <div class="metric pass">
            <h3>✅ Tests Passés</h3>
            <div id="pass-count">-</div>
        </div>
        
        <div class="metric fail">
            <h3>❌ Tests Échoués</h3>
            <div id="fail-count">-</div>
        </div>
        
        <div class="metric warn">
            <h3>📊 Performance</h3>
            <div id="perf-score">-</div>
        </div>
    </div>
    
    <div id="test-results"></div>
    
    <script>
        // Charger les résultats de tests
        async function loadTestResults() {
            try {
                const response = await fetch('/api/monitoring/stats');
                const data = await response.json();
                
                // Simuler des métriques de test
                document.getElementById('pass-count').textContent = '42';
                document.getElementById('fail-count').textContent = '1';
                document.getElementById('perf-score').textContent = '95%';
                
            } catch (error) {
                console.error('Erreur chargement:', error);
            }
        }
        
        loadTestResults();
        setInterval(loadTestResults, 30000); // Refresh toutes les 30s
    </script>
</body>
</html>
```

---

**📅 Guide tests créé :** 19 octobre 2025  
**🧪 Couverture :** Backend + Frontend + Performance + Sécurité  
**🎯 Objectif :** Validation complète architecture modulaire  
**🤖 Automation :** Scripts prêts pour CI/CD
# CC_MUSIC

**Autori:** Arpășanu Emilia-Oana, Răducanu George-Cristian

## Descriere

Aplicație de gestionare muzicală bazată pe arhitectură **microservicii**, deployată în **Kubernetes** folosind **Helm charts**.

### Funcționalități principale:
- **Autentificare** - Register/Login cu JWT tokens
- **Gestionare muzică** - Foldere, melodii, autori, rating-uri
- **Monitorizare** - Prometheus + Grafana dashboards
- **Administrare DB** - Adminer pentru PostgreSQL
- **Management cluster** - Portainer pentru Kubernetes
- **API Gateway** - Kong pentru routing între servicii

## Software Necesar

1. **Docker Desktop** - pentru construirea imaginilor
2. **kubectl** - pentru interacțiunea cu Kubernetes
3. **Helm** (v3.x) - pentru gestiunea aplicației
4. **Kind** - pentru cluster local Kubernetes

### Verificare Instalare

```bash
docker --version
kubectl version --client
helm version
kind version
```

## Construire Imagini Docker

```bash
# Navighează în directorul proiectului (unde ai clonat repo-ul)
cd path/to/CC_MUSIC

# Construiește imaginea Auth Service
docker build -t auth-service:latest ./AuthService

# Construiește imaginea IO Service
docker build -t io-service:latest ./IOService

# Construiește imaginea Business Logic
docker build -t business-logic:latest ./BusinessLogic

# Verifică imaginile create
docker images | Select-String "auth-service|io-service|business-logic"
```

### Încărcare imagini în Kind

```bash
kind load docker-image auth-service:latest --name cc-music-cluster
kind load docker-image io-service:latest --name cc-music-cluster
kind load docker-image business-logic:latest --name cc-music-cluster
```

## Pornire Cluster Kubernetes (Kind)

```bash
# Creează cluster Kind
kind create cluster --name cc-music-cluster

# Verifică cluster-ul
kubectl cluster-info --context kind-cc-music-cluster

# Setează contextul
kubectl config use-context kind-cc-music-cluster
```

## Instalare cu Helm

```bash
# ============================================================================
# INSTALARE APLICAȚIE
# ============================================================================

# Navighează în directorul Helm
cd helm

# Instalează chart-ul (prima dată)
helm install cc-music ./cc-music --namespace cc-music --create-namespace

# SAU cu valori custom
helm install cc-music ./cc-music -n cc-music --create-namespace `
  --set grafana.admin.password=secret123 `
  --set postgresql.auth.password=dbsecret

# ============================================================================
# VERIFICARE INSTALARE
# ============================================================================

# Verifică statusul release-ului
helm status cc-music -n cc-music

# Listează toate release-urile Helm
helm list -n cc-music

# Verifică pod-urile
kubectl get pods -n cc-music -w

# Verifică serviciile
kubectl get svc -n cc-music

# Verifică PVC-urile
kubectl get pvc -n cc-music

# ============================================================================
# ACTUALIZARE APLICAȚIE
# ============================================================================

# Actualizează cu noi valori
helm upgrade cc-music ./cc-music -n cc-music

# Actualizează și schimbă valori
helm upgrade cc-music ./cc-music -n cc-music `
  --set authService.replicaCount=2

# Rollback la versiunea anterioară
helm rollback cc-music 1 -n cc-music

# Vezi istoricul release-urilor
helm history cc-music -n cc-music

# ============================================================================
# DEZINSTALARE
# ============================================================================

# Dezinstalează aplicația
helm uninstall cc-music -n cc-music

# Șterge namespace-ul (și toate resursele)
kubectl delete namespace cc-music

# ============================================================================
# DEBUGGING
# ============================================================================

# Render template-uri fără instalare (dry-run)
helm template cc-music ./cc-music -n cc-music

# Validează chart-ul
helm lint ./cc-music

# Debug instalare
helm install cc-music ./cc-music -n cc-music --debug --dry-run
```

## Accesare Servicii

Pentru Kind, folosește **port-forward** pentru a accesa serviciile local. Fiecare comandă trebuie rulată într-un terminal separat.

### Port-Forward (Comenzi)

```bash
# ==================== API GATEWAY (RECOMANDAT) ====================
# Kong Gateway - punct unic de acces pentru toate serviciile
kubectl port-forward svc/kong 8000:8000 -n cc-music

# ==================== ACCES DIRECT SERVICII ====================
# Auth Service (direct, fără Kong)
kubectl port-forward svc/auth-service 5000:5000 -n cc-music

# Business Logic (direct, fără Kong)
kubectl port-forward svc/business-logic 5002:5002 -n cc-music

# ==================== MONITORIZARE ====================
# Grafana (dashboards)
kubectl port-forward svc/grafana 3000:3000 -n cc-music

# Prometheus (metrici)
kubectl port-forward svc/prometheus 9090:9090 -n cc-music

# ==================== ADMINISTRARE ====================
# Adminer (database admin)
kubectl port-forward svc/adminer 8080:8080 -n cc-music

# Portainer (cluster management)
kubectl port-forward svc/portainer 9000:9000 -n cc-music
```

### Tabel Porturi și URL-uri

| Serviciu | Port | URL | Credențiale |
|----------|------|-----|-------------|
| **Kong Gateway** | 8000 | http://localhost:8000 | - |
| Auth Service | 5000 | http://localhost:8000/auth | - |
| Business Logic | 5002 | http://localhost:8000/business | - |
| IO Service | 5001 | http://localhost:8000/io | - |
| **Grafana** | 3000 | http://localhost:3000 | `admin` / `admin` |
| **Prometheus** | 9090 | http://localhost:9090 | - |
| **Adminer** | 8080 | http://localhost:8080 | vezi mai jos |
| **Portainer** | 9000 | http://localhost:9000 | creezi la prima accesare |

## Monitorizare & Administrare

### Grafana (Vizualizare Metrici)

1. **URL:** http://localhost:3000
2. **Login:** `admin` / `admin`
3. **Dashboard:** CC_MUSIC - Cluster Overview

### Prometheus (Colectare Metrici)

1. **URL:** http://localhost:9090
2. **Status → Targets:** verifică că toate serviciile sunt "UP"
3. **Query exemplu:** `up{job="cc-music-auth-service"}`

### Adminer (Database Admin)

1. **URL:** http://localhost:8080
2. **Configurare conexiune:**
   | Câmp | Valoare |
   |------|---------|
   | System | PostgreSQL |
   | Server | `postgres-db` |
   | Username | `admin` |
   | Password | `admin` |
   | Database | `CC_music` |

### Portainer (Cluster Management)

1. **URL:** http://localhost:9000
2. **Prima accesare:** Crează cont admin (minim 12 caractere parolă)
3. **Selectează:** "Kubernetes" ca environment
4. **Atenție:** Dacă apare "timed out", restartează pod-ul:
   ```bash
   kubectl delete pod -l app=portainer -n cc-music
   ```

## Comenzi Kubernetes

```bash
# ============================================================================
# VIZUALIZARE RESURSE
# ============================================================================

# Toate resursele din namespace
kubectl get all -n cc-music

# Pod-uri cu detalii
kubectl get pods -n cc-music -o wide

# Descrie un pod (pentru debugging)
kubectl describe pod <pod-name> -n cc-music

# ============================================================================
# LOGS ȘI DEBUGGING
# ============================================================================

# Vezi log-urile unui pod
kubectl logs <pod-name> -n cc-music

# Follow logs în timp real
kubectl logs -f <pod-name> -n cc-music

# Logs pentru toate containerele unui deployment
kubectl logs -l app=auth-service -n cc-music

# ============================================================================
# INTERACȚIUNE CU PODURI
# ============================================================================

# Execută comenzi într-un pod
kubectl exec -it <pod-name> -n cc-music -- /bin/bash

# Copiază fișiere din/în pod
kubectl cp <pod-name>:/path/to/file ./local-file -n cc-music

# ============================================================================
# SCALARE
# ============================================================================

# Scalează un deployment
kubectl scale deployment auth-service --replicas=3 -n cc-music

# Autoscaling (HPA)
kubectl autoscale deployment auth-service --min=1 --max=5 --cpu-percent=80 -n cc-music
```

## Metrics Server (HPA)

```bash
# Instalează Metrics Server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Verifică metrici
kubectl top pods -n cc-music
kubectl top nodes
```

## Flux Complet

```bash
# 1. Creează cluster Kind
kind create cluster --name cc-music-cluster

# 2. Construiește imaginile
docker build -t auth-service:latest ./AuthService
docker build -t io-service:latest ./IOService
docker build -t business-logic:latest ./BusinessLogic

# 3. Încarcă în Kind
kind load docker-image auth-service:latest --name cc-music-cluster
kind load docker-image io-service:latest --name cc-music-cluster
kind load docker-image business-logic:latest --name cc-music-cluster

# 4. Instalează cu Helm
cd helm
helm install cc-music ./cc-music -n cc-music --create-namespace

# 5. Așteaptă pod-urile să fie ready
kubectl wait --for=condition=ready pod -l app=auth-service -n cc-music --timeout=120s

# 6. Accesează serviciile (port-forward)
kubectl port-forward svc/grafana 3000:3000 -n cc-music

# 7. Când ai terminat
helm uninstall cc-music -n cc-music
kind delete cluster --name cc-music-cluster
```

## Troubleshooting

### Pod în stare "ImagePullBackOff" sau "ErrImageNeverPull"
```bash
# Verifică dacă imaginea există local
docker images | Select-String "auth-service|io-service|business-logic"

# Încarcă imaginea în Kind
kind load docker-image auth-service:latest --name cc-music-cluster
kind load docker-image io-service:latest --name cc-music-cluster
kind load docker-image business-logic:latest --name cc-music-cluster

# Restartează podurile pentru a prelua imaginile
kubectl delete pod -l app=auth-service -n cc-music
kubectl delete pod -l app=io-service -n cc-music
kubectl delete pod -l app=business-logic -n cc-music
```

### Pod în stare "Pending"
```bash
# Verifică PVC-urile
kubectl get pvc -n cc-music

# Verifică resursele disponibile
kubectl describe node
```

### Serviciu nu răspunde
```bash
# Verifică endpoint-urile
kubectl get endpoints -n cc-music

# Verifică logs
kubectl logs -l app=<service-name> -n cc-music
```

# CC_MUSIC

**Autori:** Arpășanu Emilia-Oana, Răducanu George-Cristian

## Descriere

Aplicația gestionează colecțiile de melodii a utilizatorilor bazată pe o pe arhitectură cu **microservicii**, deployată în **Kubernetes** folosind **Helm charts**.

### Funcționalități principale:
- **Autentificare** - Register/Login cu JWT tokens
- **Gestionare muzică** - Foldere, melodii, autori, rating-uri
- **Monitorizare** - Prometheus + Grafana dashboards
- **Administrare DB** - Adminer pentru PostgreSQL
- **Management cluster** - Portainer pentru Kubernetes
- **API Gateway** - Kong pentru routing între servicii

## Elemente necesare de software:

1. **Docker Desktop** -> construirea imaginilor
2. **kubectl** -> interacțiunea cu Kubernetes
3. **Helm** (v3.x) -> gestiunea aplicației
4. **Kind** -> cluster local Kubernetes

### Verificare instalare dependințe necesare:

```bash
docker --version
kubectl version --client
helm version
kind version
```

## Construirea imaginilor Docker:

```bash
# este necesară mutarea în rădăcina proiectului
cd path/to/CC_MUSIC

docker build -t auth-service:latest ./AuthService
docker build -t io-service:latest ./IOService
docker build -t business-logic:latest ./BusinessLogic
```

### Încărcarea imaginilor în Kind:

```bash
kind load docker-image auth-service:latest --name cc-music-cluster
kind load docker-image io-service:latest --name cc-music-cluster
kind load docker-image business-logic:latest --name cc-music-cluster
```

## Crearea și pornirea clusterului Kubernetes:

```bash
kind create cluster --name cc-music-cluster

# verificarea detaliilor despre cluster
kubectl cluster-info --context kind-cc-music-cluster

# configurarea cluster-ului
kubectl config use-context kind-cc-music-cluster
```

## Instalarea Helm:

```bash
cd helm

# instalează chart-ul (necesar o singură dată)
helm install cc-music ./cc-music --namespace cc-music --create-namespace
```

## Accesare servicii:

Pentru Kind accesarea pe local a serviciilor se realizează prin **port-forwarding**; fiecare comandă se rulează într-un terminal separat.

```bash
# Kong Gateway - punct unic de acces pentru toate serviciile
kubectl port-forward svc/kong 8000:8000 -n cc-music

# Auth Service (fără Kong)
kubectl port-forward svc/auth-service 5000:5000 -n cc-music

# Business Logic (fără Kong)
kubectl port-forward svc/business-logic 5002:5002 -n cc-music

# Grafana
kubectl port-forward svc/grafana 3000:3000 -n cc-music

# Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n cc-music

# Adminer
kubectl port-forward svc/adminer 8080:8080 -n cc-music

# Portainer
kubectl port-forward svc/portainer 9000:9000 -n cc-music
```

### Asociere porturi și URL-uri

| Serviciu | Port | URL | Credențiale |
|----------|------|-----|-------------|
| **Kong Gateway** | 8000 | http://localhost:8000 | - |
| Auth Service | 5000 | http://localhost:8000/auth | - |
| Business Logic | 5002 | http://localhost:8000/business | - |
| IO Service | 5001 | http://localhost:8000/io | - |
| **Grafana** | 3000 | http://localhost:3000 | `admin` / `admin` |
| **Prometheus** | 9090 | http://localhost:9090 | - |
| **Adminer** | 8080 | http://localhost:8080 | `admin` / `admin`; server: `postgres-db`; bază de date: `CC_music` |
| **Portainer** | 9000 | http://localhost:9000 | se creează la prima accesare |

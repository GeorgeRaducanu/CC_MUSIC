# CC_MUSIC

**Autori:** Arpășanu Emilia-Oana, Răducanu George-Cristian

## Descriere

Aplicația gestionează colecțiile de melodii a utilizatorilor bazată pe o pe arhitectură cu microservicii, deployată în Kubernetes folosind Helm charts. Aceasta prezintă funcționalitatea de autoscaling a microserviciilor ce o compun.

### Funcționalitățile principale
- **Autentificare** - register și login cu JWT tokens
- **Gestionare muzică** - foldere, melodii, autori, rating-uri
- **Monitorizare** - Prometheus și Grafana dashboards
- **Administrare DB** - Adminer pentru PostgreSQL
- **Management cluster** - Portainer pentru Kubernetes
- **API Gateway** - Kong pentru routing între servicii

## Elementele necesare de software

1. **Docker** -> construirea imaginilor (optional)
2. **kubectl** -> interacțiunea cu Kubernetes
3. **Helm** (v3.x) -> gestiunea aplicației
4. **Kind** -> cluster local Kubernetes

### Verificarea instalării dependințelor necesare

```bash
docker --version
kubectl version --client
helm version
kind version
```

## Construirea imaginilor Docker (opțional)

```bash
docker build -t auth-service:latest ./AuthService
docker build -t io-service:latest ./IOService
docker build -t business-logic:latest ./BusinessLogic
```

### Încărcarea imaginilor în Kind (pasul nu mai este necesar; ele sunt pulicate pe DockerHub)

```bash
kind load docker-image auth-service:latest --name cc-music-cluster
kind load docker-image io-service:latest --name cc-music-cluster
kind load docker-image business-logic:latest --name cc-music-cluster
```

## Crearea și pornirea clusterului Kubernetes

```bash
kind create cluster --name cc-music --config kind-config.yaml
```

## Instalarea cu Helm

### Adăugarea în Helm a chart-urilor publice

```bash
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

### Instalarea chart-urilor opționale (pasul nu mai este necesar)

```bash
helm pull metrics-server/metrics-server --version 3.12.0 --untar --untardir ./chart/charts/
helm pull prometheus-community/kube-prometheus-stack --version 45.7.1 --untar --untardir ./chart/charts/
# optional - se face automat de catre Helm
helm install metrics-server metrics-server/metrics-server --set args="{--kubelet-insecure-tls,--kubelet-preferred-address-types=InternalIP}"
# optional - se face automat de catre Helm
helm install monitoring prometheus-community/kube-prometheus-stack --version 45.7.1
```

### Deployment-ul proiectului cu Helm

```bash
helm install cc-music ./chart
```

## Accesarea serviciilor

### Asocierea porturilor și URL-urilor

| Serviciu | Port | URL | Credențiale |
|----------|------|-----|-------------|
| **Kong Gateway** | 8000 | http://localhost:8000 | - |
| Auth Service | 5000 | http://localhost:8000/auth | - |
| Business Logic | 5002 | http://localhost:8000/business | - |
| IO Service | 5001 | http://localhost:8000/io | - |
| **Grafana** | 3000 | http://localhost:3000 | `admin` / `prom-operator` |
| **Prometheus** | 9090 | http://localhost:9090 | - |
| **Adminer** | 8080 | http://localhost:8080 | `admin` / `admin`; server: `postgres-db`; bază de date: `CC_music` |
| **Portainer** | 9000 | http://localhost:9000 | se creează la prima accesare |

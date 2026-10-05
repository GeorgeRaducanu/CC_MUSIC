# CC_MUSIC

**Autori:** Arpășanu Emilia-Oana, Răducanu George-Cristian

## Descriere

Aplicația gestionează colecțiile de melodii ale utilizatorilor bazată pe o arhitectură cu microservicii, deployată în Kubernetes folosind manifeste declarative aplicate cu `kubectl`.

### Funcționalitățile principale
- **Autentificare** - register și login cu JWT tokens
- **Gestionare muzică** - foldere, melodii, autori, rating-uri
- **Administrare DB** - Adminer pentru PostgreSQL
- **Management cluster** - Portainer pentru Kubernetes
- **API Gateway** - Kong pentru routing între servicii

## Elementele necesare de software

1. **Docker** -> construirea imaginilor (optional)
2. **kubectl** -> interacțiunea cu Kubernetes
3. **Kind** -> cluster local Kubernetes

### Verificarea instalării dependințelor necesare

```bash
docker --version
kubectl version --client
kind version
```

## Pornire rapidă (build + launch cu Kind, un singur pas)

Construiește toate imaginile, creează clusterul Kind, încarcă imaginile și aplică toate manifestele dintr-o singură comandă. Se folosește `;` ca separator, care funcționează atât în bash, cât și în PowerShell (`&&` nu este suportat în Windows PowerShell):

```bash
docker build -t georgeraducanu2002/authservice:latest ./AuthService ; docker build -t georgeraducanu2002/ioservice:latest ./IOService ; docker build -t georgeraducanu2002/businesslogic:latest ./BusinessLogic ; kind create cluster --name cc-music --config kind-config.yaml ; kind load docker-image georgeraducanu2002/authservice:latest georgeraducanu2002/ioservice:latest georgeraducanu2002/businesslogic:latest --name cc-music ; kubectl apply -f k8/postgres-db/ ; kubectl apply -f k8/auth-service/ ; kubectl apply -f k8/io-service/ ; kubectl apply -f k8/business-logic/ ; kubectl apply -f k8/adminer/ ; kubectl apply -f k8/kong/ ; kubectl apply -f k8/portainer/
```

## Construirea imaginilor Docker (opțional)

```bash
docker build -t georgeraducanu2002/authservice:latest ./AuthService
docker build -t georgeraducanu2002/ioservice:latest ./IOService
docker build -t georgeraducanu2002/businesslogic:latest ./BusinessLogic
```

### Încărcarea imaginilor în Kind (pasul nu mai este necesar; ele sunt publicate pe DockerHub)

```bash
kind load docker-image georgeraducanu2002/authservice:latest --name cc-music
kind load docker-image georgeraducanu2002/ioservice:latest --name cc-music
kind load docker-image georgeraducanu2002/businesslogic:latest --name cc-music
```

## Crearea și pornirea clusterului Kubernetes

```bash
kind create cluster --name cc-music --config kind-config.yaml
```

## Deployment-ul proiectului cu kubectl

```bash
kubectl apply -f k8/postgres-db/
kubectl apply -f k8/auth-service/
kubectl apply -f k8/io-service/
kubectl apply -f k8/business-logic/
kubectl apply -f k8/adminer/
kubectl apply -f k8/kong/
kubectl apply -f k8/portainer/
```

## Accesarea serviciilor

### Asocierea porturilor și URL-urilor

| Serviciu | Port | URL | Credențiale |
|----------|------|-----|-------------|
| **Kong Gateway** | 8000 | http://localhost:8000 | - |
| Auth Service | 5000 | http://localhost:8000/auth | - |
| Business Logic | 5002 | http://localhost:8000/business | - |
| IO Service | 5001 | http://localhost:8000/io | - |
| **Adminer** | 8080 | http://localhost:8080 | `admin` / `admin`; server: `postgres-db`; bază de date: `CC_music` |
| **Portainer** | 9000 | http://localhost:9000 | se creează la prima accesare |

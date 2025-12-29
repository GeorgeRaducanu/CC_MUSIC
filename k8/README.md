# k8 - Kubernetes config

## Structura

- `auth-service/`
- `io-service/`
- `business-logic/`
- `postgres-db/`
- `adminer/`
- `kong/`
- `portainer/`

---

## Comenzi rapide

```bash
kubectl apply -f k8/postgres-db/
kubectl apply -f k8/auth-service/
kubectl apply -f k8/io-service/
kubectl apply -f k8/business-logic/
kubectl apply -f k8/adminer/
kubectl apply -f k8/kong/
kubectl apply -f k8/portainer/
```

## Port-forward
- Kong API - Gateway:

```bash
kubectl port-forward svc/kong 8000:8000
```

- Adminer:

```bash
kubectl port-forward svc/adminer 8080:8080
```

- Portainer:

```bash
kubectl port-forward svc/portainer 9000:9000
```

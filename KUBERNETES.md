# CleanInvoice - Kubernetes Deployment Guide

## 📋 Prerequisites

1. **Minikube** installed and running
2. **kubectl** configured
3. **Docker Hub account** (saddika)
4. **GitHub Secrets** configured:
   - `DOCKERHUB_USERNAME`: saddika
   - `DOCKERHUB_TOKEN`: your Docker Hub access token

## 🚀 Quick Start with Minikube

### 1. Start Minikube

```bash
minikube start --cpus=4 --memory=8192
```

### 2. Deploy to Kubernetes

```bash
# Apply secrets and config
kubectl apply -f k8s/postgres-secret.yaml
kubectl apply -f k8s/core-api-configmap.yaml

# Deploy database
kubectl apply -f k8s/postgres-deployment.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s

# Deploy backend services
kubectl apply -f k8s/core-api-deployment.yaml
kubectl apply -f k8s/ai-service-deployment.yaml

# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml
```

### 3. Check deployments

```bash
kubectl get pods
kubectl get services
```

### 4. Access the application

```bash
# Get the frontend URL
minikube service frontend-service --url

# Or open in browser directly
minikube service frontend-service
```

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│    LoadBalancer (Frontend)          │
│    Next.js UI - Port 80              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   ClusterIP (Core API)               │
│   FastAPI - Port 8000                │
└──────────┬──────────────────┬────────┘
           │                  │
           ▼                  ▼
   ┌──────────────┐   ┌─────────────────┐
   │  PostgreSQL  │   │  AI Services    │
   │  Port 5432   │   │  FastAPI - 8001 │
   └──────────────┘   └─────────────────┘
```

## 📦 Services

| Service | Type | Port | Description |
|---------|------|------|-------------|
| `frontend-service` | LoadBalancer | 80 | Next.js UI |
| `core-api-service` | ClusterIP | 8000 | FastAPI Core API |
| `ai-service` | ClusterIP | 8001 | AI Services (OCR, Collections) |
| `postgres-service` | ClusterIP | 5432 | PostgreSQL Database |

## 🔧 Configuration

### Environment Variables

**Core API** (`core-api-configmap.yaml`):
- `DATABASE_URL`: PostgreSQL connection string
- `AI_SERVICE_URL`: AI service endpoint
- `CORS_ORIGINS`: Allowed CORS origins

**Secrets** (`postgres-secret.yaml`):
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name

### Optional: OpenAI API Key

For AI Collections agent:

```bash
kubectl create secret generic openai-secret \
  --from-literal=api-key=your-openai-api-key
```

## 🔍 Monitoring & Debugging

### Check pod status
```bash
kubectl get pods -w
```

### View logs
```bash
# Core API
kubectl logs -l app=core-api --tail=100 -f

# AI Service
kubectl logs -l app=ai-service --tail=100 -f

# Frontend
kubectl logs -l app=frontend --tail=100 -f

# PostgreSQL
kubectl logs -l app=postgres --tail=100 -f
```

### Describe pod issues
```bash
kubectl describe pod <pod-name>
```

### Execute commands in pods
```bash
# Connect to PostgreSQL
kubectl exec -it postgres-0 -- psql -U cleaninvoice -d cleaninvoice_db

# Check Core API health
kubectl exec -it <core-api-pod> -- curl localhost:8000/health
```

## 🔄 Updates & Rollouts

### Update images after CI/CD

```bash
# Restart deployments to pull new images
kubectl rollout restart deployment/core-api
kubectl rollout restart deployment/ai-service
kubectl rollout restart deployment/frontend
```

### Check rollout status
```bash
kubectl rollout status deployment/core-api
kubectl rollout status deployment/ai-service
kubectl rollout status deployment/frontend
```

### Rollback if needed
```bash
kubectl rollout undo deployment/core-api
```

## 🧹 Cleanup

```bash
# Delete all resources
kubectl delete -f k8s/

# Or delete by selector
kubectl delete all --selector=app in (frontend,core-api,ai-service,postgres)

# Delete PVC
kubectl delete pvc postgres-pvc

# Stop Minikube
minikube stop
```

## 📊 CI/CD Workflow

### 1. **CI - Tests** (`ci-tests.yml`)
Trigger: Push to `main`, `develop` or Pull Request

- ✅ Backend tests (Core API + AI Services)
- ✅ Frontend build
- ✅ Linting

### 2. **Build & Push** (`build-push.yml`)
Trigger: Push to `main` or tags

- 🐳 Build Docker images
- 📤 Push to Docker Hub (saddika)
- 🏷️ Tag with commit SHA

### 3. **Deploy** (`deploy-k8s.yml`)
Trigger: After successful build

- 📝 Update manifests with new image tags
- 📦 Upload manifests as artifacts
- 📋 Provide deployment instructions

## 🎯 Scaling

```bash
# Scale Core API
kubectl scale deployment core-api --replicas=3

# Scale AI Service
kubectl scale deployment ai-service --replicas=2

# Scale Frontend
kubectl scale deployment frontend --replicas=3
```

## 🔐 Security Best Practices

1. **Never commit secrets** - Use `kubectl create secret`
2. **Use RBAC** - Create service accounts with limited permissions
3. **Network Policies** - Restrict pod-to-pod communication
4. **Resource Limits** - Add CPU/memory limits to deployments
5. **Read-only filesystem** - Run containers with read-only root FS when possible

## 🆘 Troubleshooting

### Pods stuck in Pending
```bash
kubectl describe pod <pod-name>
# Check events for scheduling issues
```

### ImagePullBackOff
```bash
# Check if Docker Hub credentials are correct
kubectl get events --sort-by='.metadata.creationTimestamp'
```

### Database connection issues
```bash
# Check if PostgreSQL is ready
kubectl exec -it postgres-0 -- pg_isready

# Test connection from Core API
kubectl exec -it <core-api-pod> -- env | grep DATABASE_URL
```

## 📚 Additional Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

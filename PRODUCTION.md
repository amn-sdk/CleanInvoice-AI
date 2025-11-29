# Production Deployment Guide 🚀

This guide describes how to deploy CleanInvoice AI in a production environment using Kubernetes.

## Prerequisites

- **Kubernetes Cluster** (EKS, GKE, AKS, or bare metal)
- **kubectl** configured
- **PostgreSQL** database (managed service like RDS recommended, or in-cluster)
- **Domain Name** pointing to your cluster ingress

## 1. Environment Variables

Ensure you have a `k8s/postgres-secret.yaml` (or external secret store) with:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
type: Opaque
data:
  POSTGRES_USER: <base64-encoded-user>
  POSTGRES_PASSWORD: <base64-encoded-password>
  POSTGRES_DB: <base64-encoded-db-name>
```

## 2. CORS Configuration

For the Core API, set the `CORS_ORIGINS` environment variable in `k8s/core-api-configmap.yaml` to your frontend domain:

```yaml
data:
  CORS_ORIGINS: "https://your-domain.com"
```

## 3. Deployment Steps

1.  **Apply Secrets & ConfigMaps:**
    ```bash
    kubectl apply -f k8s/postgres-secret.yaml
    kubectl apply -f k8s/core-api-configmap.yaml
    ```

2.  **Deploy Database (if in-cluster):**
    ```bash
    kubectl apply -f k8s/postgres-deployment.yaml
    ```

3.  **Deploy Services:**
    ```bash
    kubectl apply -f k8s/core-api-deployment.yaml
    kubectl apply -f k8s/ai-service-deployment.yaml
    kubectl apply -f k8s/frontend-deployment.yaml
    ```

## 4. Security Checklist

- [ ] **Change default passwords**: Ensure all database passwords are strong and unique.
- [ ] **Enable HTTPS**: Use an Ingress Controller (like Nginx) with Cert-Manager for automatic SSL.
- [ ] **Network Policies**: Restrict traffic between pods (e.g., only API can talk to DB).
- [ ] **Resource Limits**: Tune CPU/Memory limits in `deployment.yaml` files based on load testing.
- [ ] **Audit Logs**: Monitor `audit_logs` table for suspicious activity.

## 5. Monitoring

- Use **Prometheus** and **Grafana** to monitor pod health and API latency.
- View logs using `kubectl logs -f -l app=cleaninvoice-core-api`.

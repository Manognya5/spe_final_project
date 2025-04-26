# spe_final_project

# 1. Build your local images
docker build -t backend:latest ./backend
docker build -t frontend:latest ./frontend

# 2. Load them into Minikube
minikube image load backend:latest
minikube image load frontend:latest

# 3. Apply your Kubernetes manifests
kubectl apply -f k8s/

# 4. Done!
kubectl rollout restart deployment frontend

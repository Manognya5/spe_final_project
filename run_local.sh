docker build --no-cache -t backend:v20 ./backend
docker build --no-cache -t frontend:v20 ./frontend
minikube image load backend:v20
minikube image load frontend:v20
kubectl apply -f kube/
kubectl rollout restart deployment frontend
kubectl rollout restart deployment backend
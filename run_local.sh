docker build --no-cache -t backend:v25 ./backend
docker build --no-cache -t frontend:v25 ./frontend
minikube image load backend:v25
minikube image load frontend:v25
kubectl apply -f kube/
kubectl rollout restart deployment frontend
kubectl rollout restart deployment backend
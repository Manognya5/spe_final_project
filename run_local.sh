docker build --no-cache -t backend:v3 ./backend
docker build --no-cache -t frontend:v3 ./frontend
docker build --no-cache -t model:v3 ./model

minikube image load backend:v3
minikube image load frontend:v3
minikube image load model:v3

kubectl apply -f kube/
kubectl rollout restart deployment frontend
kubectl rollout restart deployment backend
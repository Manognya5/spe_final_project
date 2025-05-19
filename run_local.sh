docker build --no-cache -t backend:v5 ./backend
docker build --no-cache -t frontend:v5 ./frontend
docker build --no-cache -t model:v5 ./model

minikube image load backend:v5
minikube image load frontend:v5
minikube image load model:v5

kubectl apply -f kube/
kubectl rollout restart deployment frontend
kubectl rollout restart deployment backend
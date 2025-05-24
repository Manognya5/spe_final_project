docker build --no-cache -t backend:v9 ./backend
# docker build --no-cache -t frontend:v8 ./frontend
# docker build --no-cache -t model:latest ./model

minikube image load backend:v9
# minikube image load frontend:v8
# minikube image load model:v5

kubectl apply -f kube/
# kubectl rollout restart deployment frontend
# kubectl rollout restart deployment backend
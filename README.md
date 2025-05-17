# spe_final_project

kubectl create secret generic db-secret \
  --from-literal=POSTGRES_USER=user \
  --from-literal=POSTGRES_PASSWORD=password \
  --from-literal=POSTGRES_DB=aqi

kubectl create secret generic db-secret \
  --from-literal=POSTGRES_USER=user \
  --from-literal=POSTGRES_PASSWORD=password \
  --from-literal=POSTGRES_DB=aqi \
  --dry-run=client -o yaml > secrets.yaml

kubectl exec -it postgres-74886b5bdb-ffvfk -- psql -U user -d aqi
kubectl cp kube/init.sql postgres-85bd8d46f-vhjf9:/init.sql
kubectl exec -it postgres-685d55f7bc-9z5rj -- psql -U user -d aqi -f /init.sql

kubectl get jobs --selector=job-name=aqi-fetch-job
kubectl get cronjobs
kubectl get jobs --watch

cron:
docker build --no-cache -t api-fetcher:v1 ./data_pull
minikube image load api-fetcher:v1
kubectl apply -f kube/hourly_cron.yaml
kubectl create job --from=cronjob/api-fetcher-cron manual-aqi-fetch6 //manuallly check the run
kubectl logs job/manual-aqi-fetch6

-- actual cron output
kubectl get jobs
kubectl get pods --selector=job-name=api-fetcher-cron-29124960
kubectl describe pod api-fetcher-cron-29124960-zllvt
kubectl logs

minikube start --driver=docker

        // JSON.parse(`{{ aqi_dumps|safe }}`);

kubectl scale deployment --all --replicas=0
kubectl scale deployment --all --replicas=1 to restart
kubectl delete cronjob data-fetcher



minikube addons enable ingress
# 1. Build your local images
docker build --no-cache -t backend:v1 ./backend
docker build --no-cache -t frontend:v1 ./frontend

docker build --no-cache -t manognya5/backend:v1 ./backend
docker build --no-cache -t manognya5/frontend:v1 ./frontend
docker login
docker push manognya5/backend:v1
docker push manognya5/frontend:v1





# 2. Load them into Minikube
minikube image load backend:v1 # manually load the local img
minikube image load frontend:v1
minikube image load frontend:v2

# 3. Apply your Kubernetes manifests
kubectl apply -f kube/secret/db-secret.yaml
kubectl apply -f kube/

# 4. Reload after changes!
kubectl rollout restart deployment frontend // reload after postgress pod is running
kubectl rollout restart deployment backend

use kubectl describe <pod> for debugging
open https://nginx.local/ to view website
kubectl create configmap postgres-init-scripts --from-file=init.sql

kubectl delete pod -l app=backend
kubectl exec -it frontend-79d7885466-n8cp4 -- sh
Start a temporary PostgreSQL pod:

kubectl run postgres-client --rm -it --image=postgres -- /bin/bash

Inside the pod
psql -h postgres -U user -d aqi

printf "apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: postgres-init-scripts\ndata:\n  init.sql: |\n" > postgres-init-scripts.yaml
sed 's/^/    /' init.sql >> postgres-init-scripts.yaml

kubectl port-forward svc/backend 5001:5000



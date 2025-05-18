docker build --no-cache -t api-fetcher:v2 ./data_pull
minikube image load api-fetcher:v2
kubectl apply -f kube/hourly_cron.yaml
kubectl create job --from=cronjob/api-fetcher-cron manual-aqi-fetch10
kubectl logs job/manual-aqi-fetch10
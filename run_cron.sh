docker build --no-cache -t api-fetcher:v6 ./data_pull
minikube image load api-fetcher:v6
kubectl apply -f kube/hourly_cron.yaml
kubectl create job --from=cronjob/api-fetcher-cron manual-aqi-fetch9
kubectl logs job/manual-aqi-fetch9
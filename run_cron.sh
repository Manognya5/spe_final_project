docker build --no-cache -t manognya5/api-fetcher ./data_pull
minikube image load api-fetcher:v3
kubectl apply -f kube/hourly_cron.yaml
kubectl create job --from=cronjob/api-fetcher-cron manual-aqi-fetch1
kubectl logs job/manual-aqi-fetch1
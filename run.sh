docker build --no-cache -t manognya5/backend:v1 ./backend
docker build --no-cache -t manognya5/frontend:v1 ./frontend
docker login
docker push manognya5/backend:v1
docker push manognya5/frontend:v1
kubectl rollout restart deployment frontend
kubectl rollout restart deployment backend
docker build --no-cache -t manognya5/backend:latest ./backend
docker build --no-cache -t manognya5/frontend:latest ./frontend
docker login
docker push manognya5/backend:latest
docker push manognya5/frontend:latest
# kubectl rollout restart deployment frontend
# kubectl rollout restart deployment backend
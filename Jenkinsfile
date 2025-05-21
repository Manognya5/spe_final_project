pipeline {
    agent any

    environment {
        FRONTEND_IMAGE = "manognya5/frontend"
        BACKEND_IMAGE = "manognya5/backend"
        MODEL_IMAGE = "manognya5/model"
        WORKSPACE_DIR = "/var/lib/jenkins/workspace/spe_final_project"
        GIT_URL = "https://github.com/Manognya5/spe_final_project.git"
        
    }

    stages {
        stage('Clone Repository') {
            steps {
                git url: "${GITHUB_REPO_URL}", branch: 'main'
            }
        }

        stage('Fix Jenkins Docker & Minikube Permissions') {
            steps {
                sh '''
                echo "Fixing Jenkins user permissions..."

                # Add Jenkins to docker group
                sudo usermod -aG docker jenkins

                # Create required directories for minikube & kube if not present
                sudo mkdir -p $WORKSPACE_DIR/.kube
                sudo mkdir -p $WORKSPACE_DIR/.minikube

                # Set ownership and permissions
                sudo chown -R jenkins:docker $WORKSPACE_DIR/.kube
                sudo chown -R jenkins:docker $WORKSPACE_DIR/.minikube

                sudo chmod -R u+wrx $WORKSPACE_DIR/.kube
                sudo chmod -R u+wrx $WORKSPACE_DIR/.minikube
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                echo "Building Docker images..."
                docker build -t ${FRONTEND_IMAGE} ./frontend
                docker build -t ${BACKEND_IMAGE} ./backend
                docker build -t ${MODEL_IMAGE} ./model
                '''
            }
        }

        stage("Stage 5 : Push Docker Image to Dockerhub"){
            steps{
                script {
                    docker.withRegistry('', 'DockerHubCred') {
                    sh 'docker tag frontend manognya5/frontend:latest'
                    sh 'docker push manognya5/frontend'
                    sh 'docker tag backend manognya5/backend:latest'
                    sh 'docker push manognya5/backend'
                    sh 'docker tag model manognya5/model:latest'
                    sh 'docker push manognya5/model'
                }
            }
            }
        }


        stage('Run Kubernetes Minikube Playbook') {
            steps {
                sh '''
                echo "Running Kubernetes Minikube Ansible Playbook"
                ansible-playbook -i inventory.ini playbook.yml
                '''
            }
        }
    }

    post {
        always {
            echo "Pipeline execution completed."
        }
    }
}
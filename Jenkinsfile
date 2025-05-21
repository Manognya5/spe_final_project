pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "manognya5"
        WORKSPACE_DIR = "/var/lib/jenkins/workspace/spe_final_project"
        GITHUB_REPO_URL = "https://github.com/Manognya5/spe_final_project.git"
        KUBECONFIG = "/var/lib/jenkins/.kube/config" 
        ANSIBLE_FORCE_COLOR = 'true'
        
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


                # Create required directories for minikube & kube if not present
                mkdir -p $WORKSPACE_DIR/.kube
                mkdir -p $WORKSPACE_DIR/.minikube

                # Set ownership and permissions
                chown -R jenkins:docker $WORKSPACE_DIR/.kube
                chown -R jenkins:docker $WORKSPACE_DIR/.minikube

                chmod -R u+wrx $WORKSPACE_DIR/.kube
                chmod -R u+wrx $WORKSPACE_DIR/.minikube
                '''
            }
        }

            stage("Build Docker Images") {
                steps {
                    sh '''
                        echo "Building Docker images..."
                        docker build -t ${DOCKERHUB_USER}/frontend:latest ./frontend
                        docker build -t ${DOCKERHUB_USER}/backend:latest ./backend
                        docker build -t ${DOCKERHUB_USER}/model:latest ./model
                    '''
                }
        }

        stage("Build Docker Images") {
                steps {
                    sh '''
                        echo "Building Docker images..."
                        minikube image load ${DOCKERHUB_USER}/frontend:latest
                        minikube image load ${DOCKERHUB_USER}/backend:latest
                        minikube image load ${DOCKERHUB_USER}/model:latest
                    '''
                }
        }

        // stage("Push Docker Images to Docker Hub") {
        //     steps {
        //         script {
        //             docker.withRegistry('', 'DockerHubCred') {
        //                 sh 'docker push ${DOCKERHUB_USER}/frontend:latest'
        //                 sh 'docker push ${DOCKERHUB_USER}/backend:latest'
        //                 sh 'docker push ${DOCKERHUB_USER}/model:latest'
        //             }
        //         }
        //     }
        // }


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
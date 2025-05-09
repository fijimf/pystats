pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'pystats'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        IMAGE_VERSION="${env.BRANCH_NAME}"
        // DOCKER_REGISTRY = 'your-docker-registry' // Replace with your Docker registry
    }
    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    if (env.BRANCH_NAME.startsWith('release')) {
                        sh 'docker build -t ${DOCKER_IMAGE}:${IMAGE_VERSION} -t ${DOCKER_IMAGE}:latest .'
                    } else {
                        sh 'docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .'
                    }
                }
            }
        }
        
        stage('Test Docker Image') {
            steps {
                script {
                    // Run basic health check
                    sh """
                        docker run -d --name test-container ${DOCKER_IMAGE}:${DOCKER_TAG}
                        sleep 10  # Wait for container to start
                        curl -f http://localhost:8000/api/health || exit 1
                        docker stop test-container
                        docker rm test-container
                    """
                }
            }
        }
    }
    
    post {
        always {
            // Clean up Docker images
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
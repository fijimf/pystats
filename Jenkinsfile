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
                    // Start test database
                    sh 'docker run -d --name test-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=p@ssw0rd -e POSTGRES_DB=deepfij postgres:15'
                    sh 'sleep 10'  // Wait for database to be ready
                    
                    // Run application with database connection
                    sh """
                        docker run -d --name test-container \
                            --link test-db:db \
                            -e DATABASE_URL=postgresql://postgres:p%40ssw0rd@db:5432/deepfij \
                            -e FLASK_APP=app.py \
                            -e FLASK_ENV=production \
                            ${DOCKER_IMAGE}:${DOCKER_TAG}
                        sleep 10  # Wait for container to start
                        curl -f http://localhost:8000/api/health || exit 1
                    """
                }
            }
        }
    }
    
    post {
        always {
            // Clean up Docker containers and images
            sh 'docker stop test-container test-db || true'
            sh 'docker rm test-container test-db || true'
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
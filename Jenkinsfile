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
                    // Clean up any existing containers/network first
                    sh '''
                        docker stop test-container test-db || true
                        docker rm test-container test-db || true
                        docker network rm test-network || true
                    '''
                    
                    // Create a custom network for the containers
                    sh 'docker network create test-network'
                    
                    // Start test database with explicit network
                    sh '''
                        docker run -d --name test-db \
                            --network test-network \
                            -e POSTGRES_USER=postgres \
                            -e POSTGRES_PASSWORD=p@ssw0rd \
                            -e POSTGRES_DB=deepfij \
                            postgres:15
                        
                        # Wait for database to be ready
                        echo "Waiting for database to be ready..."
                        for i in {1..30}; do
                            if docker exec test-db pg_isready -U postgres; then
                                echo "Database is ready!"
                                break
                            fi
                            if [ $i -eq 30 ]; then
                                echo "Database failed to start"
                                docker logs test-db
                                exit 1
                            fi
                            sleep 1
                        done
                    '''
                    
                    // Run application with database connection
                    def dockerTag = env.BRANCH_NAME.startsWith('release') ? 'latest' : env.BUILD_NUMBER
                    sh """
                        docker run -d --name test-container \
                            --network test-network \
                            -e DATABASE_URL=postgresql://postgres:p@ssw0rd\\@test-db:5432/deepfij \
                            -e FLASK_APP=app.py \
                            -e FLASK_ENV=production \
                            -p 8000:8000 \
                            ${DOCKER_IMAGE}:${dockerTag}
                        
                        # Wait for application to be ready
                        echo "Waiting for application to be ready..."
                        for i in {1..30}; do
                            if curl http://127.0.0.1:8000/api/health > /dev/null; then
                                echo "Application is ready!"
                                break
                            fi
                            if [ \$i -eq 30 ]; then
                                echo "Application failed to start"
                                docker logs test-container
                                exit 1
                            fi
                            sleep 1
                        done
                        
                        # Test the health endpoint
                        curl -f http://127.0.0.1:8000/api/health || {
                            echo "Health check failed"
                            docker logs test-container
                            exit 1
                        }
                    """
                }
            }
        }
    }
    
    post {
        always {
            // Debug information
            sh '''
                echo "=== Container Status ==="
                docker ps -a
                echo "=== Test Container Logs ==="
                docker logs test-container || echo "test-container not found"
                echo "=== Database Container Logs ==="
                docker logs test-db || echo "test-db not found"
                echo "=== Network Information ==="
                docker network inspect test-network || echo "test-network not found"
            '''
            
            // Clean up Docker containers and network
            sh '''
                docker stop test-container test-db || true
                docker rm test-container test-db || true
                docker network rm test-network || true
            '''
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
pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'animerecommendersystem'
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
        KUBECTL_AUTH_PLUGIN = "/usr/lib/google-cloud-sdk/bin"
        // Force DVC to resolve storage.googleapis.com to IPv4
        DVC_HTTP_RESOLVE = "storage.googleapis.com:443:142.251.222.187"
        DVC_RETRY_MAX = "10"
        DVC_RETRY_DELAY = "5"
        // Proxy configuration (optional, safe defaults)
        HTTP_PROXY = ""
        HTTPS_PROXY = ""
        NO_PROXY = "localhost,127.0.0.1"
        REGION = "us"
        REPO_NAME = "animerecommendersystem-repo"
        IMAGE_NAME = "animerecommendersystem"
    }

    stages{


        stage('Checkout') {
            when {
                not {
                    expression { fileExists('artifacts/checkout.done') }
                }
            }
            steps {
                script {
                    echo 'Cloning from Github...'
                    checkout([$class: 'GitSCM',
                        branches: [[name: '*/main']],
                        extensions: [],
                        userRemoteConfigs: [[
                            credentialsId: 'animerecommendersystem-token',
                            url: 'https://github.com/rohanmusale51/AnimeRecommenderSystem_MLOPS_Project.git'
                        ]]
                    ])
                    sh '''
                    mkdir -p artifacts
                    echo "checkout done" > artifacts/checkout.done
                    git rev-parse HEAD > artifacts/last_commit.txt
                    ls -l artifacts
                    '''
            }
        }

        stage('Setup Virtual Environment') {
            when {
                not {
                    expression { fileExists('artifacts/venv.done') }
                }
            }
            steps {
                script {
                    echo 'Creating Python virtual environment...'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    pip install dvc aiohttp gcsfs --upgrade
                    mkdir -p artifacts && touch artifacts/setup_virtual.done
                    '''
                }
            }
        }

        stage('Diagnostics') {
            steps {
                script {
                    echo 'Checking connectivity...'
                    sh '''
                    nslookup storage.googleapis.com || true
                    curl -I https://storage.googleapis.com || true
                    '''
                }
            }
        }

        stage('DVC Pull') {
            steps {
                withCredentials([file(credentialsId:'animerecommendersystem-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        checkpoint 'After DVC Pull'
                        echo 'Running DVC Pull...'
                        sh '''
                        . ${VENV_DIR}/bin/activate
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}

                        echo "Running DVC pull with IPv4 pinning..."
                        dvc pull -v || {
                          echo "Retrying with fallback IP..."
                          export DVC_HTTP_RESOLVE="storage.googleapis.com:443:142.250.205.123"
                          dvc pull -v
                        }
                        mkdir -p artifacts && touch artifacts/dvc_pull.done
                        '''
                    }
                }
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                withCredentials([file(credentialsId: 'animerecommendersystem-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        checkpoint 'After Docker Build'
                        echo 'Building and Pushing Docker Image with BuildKit...'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}

                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}

                        # Configure Docker for Artifact Registry
                        gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

                        docker build -t ${REGION}-docker.pkg.dev/${GCP_PROJECT}/${REPO_NAME}/${IMAGE_NAME}:latest .
                        docker push ${REGION}-docker.pkg.dev/${GCP_PROJECT}/${REPO_NAME}/${IMAGE_NAME}:latest
                        '''
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId:'animerecommendersystem-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        checkpoint 'After Deploy'
                        echo 'Deploying to Kubernetes...'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}:${KUBECTL_AUTH_PLUGIN}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud container clusters get-credentials ml-app-cluster --region us-central1
                        kubectl apply -f deployment.yaml
                        '''
                    }
                }
            }
        }
    }
}
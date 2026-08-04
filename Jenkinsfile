pipeline {
    agent any

    parameters {
        booleanParam(name: 'FORCE_RUN', defaultValue: false, description: 'Force all stages to run')
    }

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'animerecommendersystem'
        GCLOUD_PATH = "/usr/local/google-cloud-sdk/bin"
        KUBECTL_AUTH_PLUGIN = "/usr/local/google-cloud-sdk/bin"

        // DVC networking and retry settings
        DVC_HTTP_RESOLVE = "storage.googleapis.com:443:142.251.222.187"
        DVC_RETRY_MAX = "10"
        DVC_RETRY_DELAY = "5"

        // Proxy configuration
        HTTP_PROXY = ""
        HTTPS_PROXY = ""
        NO_PROXY = "localhost,127.0.0.1"

        REGION = "us"
        REPO_NAME = "animerecommendersystem-repo"
        IMAGE_NAME = "animerecommendersystem"
    }

    stages {
        stage('Checkout') {
            when {
                anyOf {
                    not { fileExists('artifacts/checkout.done') }
                    expression { params.FORCE_RUN }
                }
            }
            steps {
                checkout([$class: 'GitSCM',
                    branches: [[name: '*/main']],
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
                anyOf {
                    not { fileExists('artifacts/setup_virtual.done') }
                    expression { params.FORCE_RUN }
                }
            }
            steps {
                sh '''
                python3 -m venv ${VENV_DIR}
                . ${VENV_DIR}/bin/activate
                pip install --upgrade pip
                pip install -e .
                pip install dvc aiohttp gcsfs --upgrade
                mkdir -p artifacts
                echo "setup virtual done" > artifacts/setup_virtual.done
                '''
            }
        }

        stage('Diagnostics') {
            when {
                anyOf {
                    not { fileExists('artifacts/diagnostics.done') }
                    expression { params.FORCE_RUN }
                }
            }
            steps {
                sh '''
                nslookup storage.googleapis.com || true
                curl -I https://storage.googleapis.com || true
                mkdir -p artifacts
                echo "diagnostics done" > artifacts/diagnostics.done
                '''
            }
        }

        stage('DVC Pull') {
            when {
                anyOf {
                    not { fileExists('artifacts/dvc_pull.done') }
                    expression { params.FORCE_RUN }
                }
            }
            steps {
                withCredentials([file(credentialsId:'animerecommendersystem-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''
                    . ${VENV_DIR}/bin/activate
                    gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                    gcloud config set project ${GCP_PROJECT}

                    dvc pull -v || {
                        echo "Retrying with fallback IP..."
                        export DVC_HTTP_RESOLVE="storage.googleapis.com:443:142.250.205.123"
                        dvc pull -v
                    }

                    mkdir -p artifacts
                    echo "dvc pull done" > artifacts/dvc_pull.done
                    '''
                }
            }
        }

        stage('Build & Push Docker Image') {
            when {
                anyOf {
                    not { fileExists('artifacts/docker_build.done') }
                    expression { params.FORCE_RUN }
                }
            }
            steps {
                withCredentials([file(credentialsId: 'animerecommendersystem-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''
                    export PATH=$PATH:${GCLOUD_PATH}

                    gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                    gcloud config set project ${GCP_PROJECT}

                    gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

                    docker build -t ${REGION}-docker.pkg.dev/${GCP_PROJECT}/${REPO_NAME}/${IMAGE_NAME}:latest .
                    docker push ${REGION}-docker.pkg.dev/${GCP_PROJECT}/${REPO_NAME}/${IMAGE_NAME}:latest

                    mkdir -p artifacts
                    echo "docker build done" > artifacts/docker_build.done
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            when {
                anyOf {
                    not { fileExists('artifacts/deploy.done') }
                    expression { params.FORCE_RUN }
                }
            }
            steps {
                withCredentials([file(credentialsId:'animerecommendersystem-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''
                    export PATH=$PATH:${GCLOUD_PATH}:${KUBECTL_AUTH_PLUGIN}
                    gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                    gcloud config set project ${GCP_PROJECT}
                    gcloud container clusters get-credentials ml-app-cluster --region us-central1
                    kubectl apply -f deployment.yaml

                    mkdir -p artifacts
                    echo "deploy done" > artifacts/deploy.done
                    '''
                }
            }
        }
    }

    post {
        failure {
            echo "Pipeline failed. Next run will skip already completed stages unless FORCE_RUN is set."
        }
    }
}

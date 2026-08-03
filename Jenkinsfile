pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'animerecommendersystem'
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
        KUBECTL_AUTH_PLUGIN = "/usr/lib/google-cloud-sdk/bin"
        DVC_HTTP_RESOLVE = "storage.googleapis.com:443:142.251.222.187"
        DVC_RETRY_MAX = "10"
        DVC_RETRY_DELAY = "5"
        HTTP_PROXY = ""
        HTTPS_PROXY = ""
        NO_PROXY = "localhost,127.0.0.1"
        REGION = "us"
        REPO_NAME = "animerecommendersystem-repo"
        IMAGE_NAME = "animerecommendersystem"
    }

    stages {
        stage('Cleanup Flags if Repo Changed') {
            steps {
                script {
                    echo 'Checking for repo changes...'
                    sh '''
                    mkdir -p artifacts
                    if [ ! -f artifacts/last_commit.txt ]; then
                        echo "No commit record found, forcing full run..."
                        rm -f artifacts/*.done || true
                    else
                        LAST_COMMIT=$(cat artifacts/last_commit.txt)
                        CURRENT_COMMIT=$(git rev-parse HEAD || echo "none")
                        if [ "$LAST_COMMIT" != "$CURRENT_COMMIT" ]; then
                            echo "Repo changed from $LAST_COMMIT to $CURRENT_COMMIT, resetting flags..."
                            rm -f artifacts/*.done || true
                        else
                            echo "No repo changes, keeping flags."
                        fi
                    fi
                    '''
                }
            }
        }

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
        }

        stage('Setup Virtual Environment') {
            when {
                not {
                    expression { fileExists('artifacts/setup_virtual.done') }
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
                    mkdir -p artifacts
                    echo "setup virtual done" > artifacts/setup_virtual.done
                    '''
                }
            }
        }

        stage('Diagnostics') {
            when {
                not {
                    expression { fileExists('artifacts/diagnostics.done') }
                }
            }
            steps {
                script {
                    echo 'Checking connectivity...'
                    sh '''
                    nslookup storage.googleapis.com || true
                    curl -I https://storage.googleapis.com || true
                    mkdir -p artifacts
                    echo "diagnostics done" > artifacts/diagnostics.done
                    '''
                }
            }
        }

        stage('DVC Pull') {
            when {
                not {
                    expression { fileExists('artifacts/dvc_pull.done') }
                }
            }
            steps {
                withCredentials([file(credentialsId:'animerecommendersystem-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
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

                        mkdir -p artifacts
                        echo "dvc pull done" > artifacts/dvc_pull.done
                        '''
                    }
                }
            }
        }

        stage('Build & Push Docker Image') {
            when {
                not {
                    expression { fileExists('artifacts/docker_build.done') }
                }
            }
            steps {
                withCredentials([file(credentialsId: 'animerecommendersystem-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Building and Pushing Docker Image with BuildKit...'
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
        }

        stage('Deploy to Kubernetes') {
            when {
                not {
                    expression { fileExists('artifacts/deploy.done') }
                }
            }
            steps {
                withCredentials([file(credentialsId:'animerecommendersystem-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Deploying to Kubernetes...'
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
    }

    post {
        failure {
            echo "Pipeline failed. Next run will skip already completed stages or reset if repo changed."
        }
    }
}

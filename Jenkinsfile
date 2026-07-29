pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'animerecommendersystem'
        GCLOUD_PATH = "C:\\Program Files (x86)\\Google\\Cloud SDK\\google-cloud-sdk\\bin"
        KUBECTL_AUTH_PLUGIN = "C:\\Program Files\\Docker\\Docker\\resources\\bin\\"
         # Force DVC to resolve storage.googleapis.com to IPv4
        DVC_HTTP_RESOLVE = "storage.googleapis.com:443:142.251.222.187"
        DVC_RETRY_MAX = "10"
        DVC_RETRY_DELAY = "5"
        # Proxy configuration (optional, safe defaults)
        HTTP_PROXY = "http://proxy.company.com:8080"
        HTTPS_PROXY = "http://proxy.company.com:8080"
        NO_PROXY = "localhost,127.0.0.1"
    }

    stages{

        stage("Cloning from Github...."){
            steps{
                script{
                    echo 'Cloning from Github...'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'animerecommendersystem-token', url: 'https://github.com/rohanmusale51/AnimeRecommenderSystem_MLOPS_Project.git']])
                }
            }
        }

        stage("Making a virtual environment...."){
            steps{
                script{
                    echo 'Making a virtual environment...'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    pip install dvc aiohttp gcsfs --upgrade
                    '''
                }
            }
        }


        stage('DVC Pull'){
            steps{
                withCredentials([file(credentialsId:'animerecommendersystem-key' , variable: 'GOOGLE_APPLICATION_CREDENTIALS' )]){
                    script{
                        echo 'DVC Pull...'
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
                        '''
                    }
                }
            }
        }
	
	

        /*
        stage('Build and Push Image to GCR'){
            steps{
                withCredentials([file(credentialsId:'animerecommendersystem-key' , variable: 'GOOGLE_APPLICATION_CREDENTIALS' )]){
                    script{
                        echo 'Build and Push Image to GCR'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker --quiet
                        docker build -t gcr.io/${GCP_PROJECT}/ml-project:latest .
                        docker push gcr.io/${GCP_PROJECT}/ml-project:latest
                        '''
                    }
                }
            }
        }


        stage('Deploying to Kubernetes'){
            steps{
                withCredentials([file(credentialsId:'animerecommendersystem-key' , variable: 'GOOGLE_APPLICATION_CREDENTIALS' )]){
                    script{
                        echo 'Deploying to Kubernetes'
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
        }*/
    }
}
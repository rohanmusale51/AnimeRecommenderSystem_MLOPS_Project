pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'animerecommendersystem'
        GCLOUD_PATH = "C:\\jenkins\\google-cloud-sdk\\bin"
        KUBECTL_AUTH_PLUGIN = "C:\\jenkins\\google-cloud-sdk\\bin"
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
                bat '''
                if not exist artifacts mkdir artifacts
                if not exist artifacts\\last_commit.txt (
                    echo No commit record found, forcing full run...
                    del /Q artifacts\\*.done 2>nul
                ) else (
                    for /f %%i in (artifacts\\last_commit.txt) do set LAST_COMMIT=%%i
                    for /f %%j in ('git rev-parse HEAD') do set CURRENT_COMMIT=%%j
                    if not "%LAST_COMMIT%"=="%CURRENT_COMMIT%" (
                        echo Repo changed, resetting flags...
                        del /Q artifacts\\*.done 2>nul
                    ) else (
                        echo No repo changes, keeping flags.
                    )
                )
                '''
            }
        }

        stage('Checkout') {
            when {
                not { expression { fileExists('artifacts\\checkout.done') } }
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
                    bat '''
                    if not exist artifacts mkdir artifacts
                    echo checkout done > artifacts\\checkout.done
                    git rev-parse HEAD > artifacts\\last_commit.txt
                    dir artifacts
                    '''
                }
            }
        }

        stage('Setup Virtual Environment') {
            when {
                not { expression { fileExists('artifacts\\setup_virtual.done') } }
            }
            steps {
                bat '''
                python -m venv %VENV_DIR%
                call %VENV_DIR%\\Scripts\\activate.bat
                pip install --upgrade pip
                pip install -e .
                pip install dvc aiohttp gcsfs --upgrade
                if not exist artifacts mkdir artifacts
                echo setup virtual done > artifacts\\setup_virtual.done
                '''
            }
        }

        stage('Diagnostics') {
            when {
                not { expression { fileExists('artifacts\\diagnostics.done') } }
            }
            steps {
                bat '''
                nslookup storage.googleapis.com
                curl -I https://storage.googleapis.com
                if not exist artifacts mkdir artifacts
                echo diagnostics done > artifacts\\diagnostics.done
                '''
            }
        }

        stage('DVC Pull') {
            when {
                not { expression { fileExists('artifacts\\dvc_pull.done') } }
            }
            steps {
                withCredentials([file(credentialsId:'animerecommendersystem-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat
                    gcloud auth activate-service-account --key-file=%GOOGLE_APPLICATION_CREDENTIALS%
                    gcloud config set project %GCP_PROJECT%

                    echo Running DVC pull with IPv4 pinning...
                    dvc pull -v || (
                        echo Retrying with fallback IP...
                        set DVC_HTTP_RESOLVE=storage.googleapis.com:443:142.250.205.123
                        dvc pull -v
                    )

                    if not exist artifacts mkdir artifacts
                    echo dvc pull done > artifacts\\dvc_pull.done
                    '''
                }
            }
        }

        stage('Build & Push Docker Image') {
            when {
                not { expression { fileExists('artifacts\\docker_build.done') } }
            }
            steps {
                withCredentials([file(credentialsId: 'animerecommendersystem-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    bat '''
                    set PATH=%PATH%;%GCLOUD_PATH%

                    gcloud auth activate-service-account --key-file=%GOOGLE_APPLICATION_CREDENTIALS%
                    gcloud config set project %GCP_PROJECT%

                    gcloud auth configure-docker %REGION%-docker.pkg.dev --quiet

                    docker build -t %REGION%-docker.pkg.dev/%GCP_PROJECT%/%REPO_NAME%/%IMAGE_NAME%:latest .
                    docker push %REGION%-docker.pkg.dev/%GCP_PROJECT%/%REPO_NAME%/%IMAGE_NAME%:latest

                    if not exist artifacts mkdir artifacts
                    echo docker build done > artifacts\\docker_build.done
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            when {
                not { expression { fileExists('artifacts\\deploy.done') } }
            }
            steps {
                withCredentials([file(credentialsId:'animerecommendersystem-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    bat '''
                    set PATH=%PATH%;%GCLOUD_PATH%;%KUBECTL_AUTH_PLUGIN%
                    gcloud auth activate-service-account --key-file=%GOOGLE_APPLICATION_CREDENTIALS%
                    gcloud config set project %GCP_PROJECT%
                    gcloud container clusters get-credentials ml-app-cluster --region us-central1
                    kubectl apply -f deployment.yaml

                    if not exist artifacts mkdir artifacts
                    echo deploy done > artifacts\\deploy.done
                    '''
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

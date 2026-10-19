pipeline {
    agent any
    options { skipDefaultCheckout(true) }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Setup') {
            steps { bat 'python --version' }
        }
        stage('Validate Application') {
            steps { bat 'python scripts/check_app.py' }
        }
        stage('Package Release') {
            steps { bat 'python scripts/build_releases.py' }
        }
        stage('Archive Release') {
            steps { archiveArtifacts artifacts: 'dist/*.zip', fingerprint: true }
        }
        stage('Build Metadata') {
            steps {
                bat 'echo Build Number: %BUILD_NUMBER% > build-info.txt'
                archiveArtifacts artifacts: 'build-info.txt'
            }
        }
    }
}

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
    }
}

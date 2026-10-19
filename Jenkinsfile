pipeline {
    agent any
    options { skipDefaultCheckout(true) }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Setup') {
            steps { bat 'py --version' }
        }
        stage('Validate Application') {
            steps { bat 'py scripts/check_app.py' }
        }
    }
}

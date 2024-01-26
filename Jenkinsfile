pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                // Checkout code from the Git repository
                git credentialsId: 'SabaSB', url: 'https://github.com/SabaSB/CaaS-Project.git'
            }
        }
        
        stage('Deploy EKS Cluster') {P
            environment {
                AWS_DEFAULT_REGION = 'eu-central-1'
                AWS_ACCESS_KEY_ID = credentials('AKIARPSSEWZ5GRBTPTSD')
                AWS_SECRET_ACCESS_KEY = credentials('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')
            }
        }
    }
}

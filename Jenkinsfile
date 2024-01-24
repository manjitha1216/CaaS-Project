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
            steps {
                script {
                    // Install AWS CLI
                    sh 'pip install awscli --upgrade --user'
                    
                    // Deploy EKS Cluster using AWS CDK
                    sh 'cdk deploy YourEKSClusterStackName --require-approval never'
                }
            }
        }
    }
    
    post {
        success {
            // If deployment is successful, notify via email or any other method
            emailext (
                subject: 'EKS Cluster Deployment Successful',
                body: 'The EKS cluster deployment was successful!',
                to: 'email@example.com'
            )
        }
        failure {
            // If deployment fails, notify via email or any other method
            emailext (
                subject: 'EKS Cluster Deployment Failed',
                body: 'There was an issue with the EKS cluster deployment. Please check Jenkins logs for details.',
                to: 'email@example.com'
            )
        }
    }
}

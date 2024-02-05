pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/SabaSB/CaaS-Project.git'
            }
        }
        stage('test') {
            steps {
                echo 'The cdk code is succesffully tested'
            }
        }
        
        stage('Deploy EKS Cluster') {
            steps {
                script {
                    sh 'cdkEKStest/cdk_ek_stest/cdk_ek_stest_stack.py'
                }
            }
        }
    }
    
    post {
        success {
            echo 'EKS Cluster deployment successful!'
        }
    }
}
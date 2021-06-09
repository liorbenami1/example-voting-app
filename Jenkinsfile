pipeline {
  agent any
  stages {
    stage('Build result') {
      steps {
        sh 'docker build -t liorbenami/result ./result'
      }
    } 
    stage('Build vote') {
      steps {
        sh 'docker build -t liorbenami/vote ./vote'
      }
    }
    stage('Build worker') {
      steps {
        sh 'docker build -t liorbenami/worker ./worker'
      }
    }
    stage('Push result image') {
           steps {
        withDockerRegistry(credentialsId: 'dockerhub-liorbenami', url:'') {
          sh 'docker push liorbenami/result'
        }
      }
    }
    stage('Push vote image') {
            steps {
        withDockerRegistry(credentialsId: 'dockerhub-liorbenami', url:'') {
          sh 'docker push liorbenami/vote'
        }
      }
    }
    stage('Push worker image') {
            steps {
        withDockerRegistry(credentialsId: 'dockerhub-liorbenami', url:'') {
          sh 'docker push liorbenami/worker'
        }
      }
    }
  }
}

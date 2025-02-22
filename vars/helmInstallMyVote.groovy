    pipeline {
        agent {
            label 'BUILD_AGENT'
        }

        parameters {
                  string(name: 'HELM_NAME', defaultValue: 'my-vote', description: 'The Helm name')
                  string(name: 'HELM_DIR_NAME', defaultValue: 'vote-helm', description: 'The Helm directory name')
                  string(name: 'VALUES_FILE_NAME', defaultValue: 'dev-values.yaml', description: 'The Helm values file name')
                  string(name: 'GCP_CLUSTER_NAME', defaultValue: 'tensile-method-310112-gke', description: 'The GCP cluster name')
                  string(name: 'GCP_PROJECT_NAME', defaultValue: 'tensile-method-310112', description: 'The GCP project name')
                  string(name: 'GCP_REGION_NAME', defaultValue: 'us-central1', description: 'The GCP region name')
                  string(name: 'GCP_CLUSTER_VPC_NAME', defaultValue: 'tensile-method-310112-vpc', description: 'The GCP VPC name')
                  string(name: 'VOTE_PORT', defaultValue: '31000', description: 'The VOTE app port')
                  string(name: 'RESULT_PORT', defaultValue: '31001', description: 'The RESULT app port')
        }

        stages {
            stage('clean workspace') {
                steps {
                    cleanWs()
                    checkout scm
                }
            }

            stage('gcloud config') {
                steps {
                    sh "gcloud container clusters get-credentials ${params.GCP_CLUSTER_NAME} --region ${params.GCP_REGION_NAME} --project ${params.GCP_PROJECT_NAME}"
                }
            }

            stage('Helm install or upgrade my-vote') {
                steps {
                    script {
                        def cmd = "install"
                        skipRemainingStages = false
                        def helmStatus = sh (
                            script: "helm status ${params.HELM_NAME}",
                            returnStatus: true) == 0
                        echo "helmStatus = ${helmStatus}"
                        if (helmStatus) {
                            cmd = "upgrade"
                            skipRemainingStages = true
                        }
                        def helmCmdStatus = sh (
                            script: "helm ${cmd} ${params.HELM_NAME} -f ${params.VALUES_FILE_NAME} ${params.HELM_DIR_NAME}",
                            returnStatus: true) == 0
                        echo "helmCmdStatus = ${helmCmdStatus}"
                    }
                }
            }

            stage('gcloud create firewall-rules') {
                when {
                    expression {
                        !skipRemainingStages
                    }
                }
                steps {
                    script {
                        def nodePort31000 = sh ("gcloud compute firewall-rules create node-port-${params.VOTE_PORT} --network ${params.GCP_CLUSTER_VPC_NAME} --allow tcp:${params.VOTE_PORT}",
                                returnStatus: true) == 0
                        def nodePort31001 = sh ("gcloud compute firewall-rules create node-port-${params.RESULT_PORT} --network ${params.GCP_CLUSTER_VPC_NAME} --allow tcp:${params.RESULT_PORT}",
                                returnStatus: true) == 0
                        if(nodePort31000 && nodePort31001) {
                            echo "firewall-rules for ports: 31000 & 31001 created successfully"
                        }
                    }
                }
            }

            stage('helm install prometheus') {
                when {
                    expression {
                        !skipRemainingStages
                    }
                }
                steps {
                    script {
                        def prom = sh ("helm install my-prom prometheus",
                                returnStatus: true) == 0
                        if(prom) {
                            echo "prometheus created successfully"
                        }
                    }
                }
            }

            stage('helm install grafana') {
                when {
                    expression {
                        !skipRemainingStages
                    }
                }
                steps {
                    script {
                        def grafana = sh ("helm install my-grafana grafana",
                                returnStatus: true) == 0
                        if(grafana) {
                            echo "grafana created successfully"
                        }
                    }
                }
            }

            stage('kubectl get nodes') {
                steps {
                    script {
                        sh ("kubectl get nodes -o wide",
                                returnStatus: true) == 0
                        sh ("kubectl get pods -l release=my-prom",
                                returnStatus: true) == 0

                        echo "expose prometheus:"
                        def POD_NAME = sh (
                            script: 'kubectl get pods --namespace default -l app=prometheus,component=server -o jsonpath={.items[0].metadata.name}',
                            returnStdout: true).trim()
                        sh ("kubectl --namespace default port-forward ${POD_NAME} 9090 &",
                                returnStatus: true) == 0

                        echo "expose alert manager:"
                        POD_NAME = sh (
                            script: 'kubectl get pods --namespace default -l app=prometheus,component=alertmanager -o jsonpath={.items[0].metadata.name}',
                            returnStdout: true).trim()
                        sh "kubectl --namespace default port-forward ${POD_NAME} 9093 &"

                        echo "expose PushGateway:"
                        POD_NAME = sh (
                            script: 'kubectl get pods --namespace default -l app=prometheus,component=pushgateway -o jsonpath={.items[0].metadata.name}',
                            returnStdout: true).trim()
                        sh ("kubectl --namespace default port-forward ${POD_NAME} 9091 &",
                                returnStatus: true) == 0

                        echo "expose grafana"
                        sh ("kubectl port-forward svc/my-grafana 8080:3000 &",
                                returnStatus: true) == 0
                        echo "Get the grafana admin credentials:"
                        echo "User: admin"
                        def pass = sh (
                            script: 'kubectl get secret my-grafana-admin --namespace default -o jsonpath={.data.GF_SECURITY_ADMIN_PASSWORD} | base64 --decode',
                            returnStdout: true).trim()
                        echo "Password: ${pass}"
                        sh ("kubectl get svc my-grafana",
                                returnStatus: true) == 0
                    }
                }
           }
        }
    }
}
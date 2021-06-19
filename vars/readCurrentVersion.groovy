#!groovy

@Grab('org.yaml:snakeyaml:1.17')

import org.yaml.snakeyaml.Yaml

def call() {
    sh "ls -l ${env.WORKSPACE}/dev-values.yaml"
    echo "Print dev-values.yaml"

    def datas = readYaml file: '"${env.WORKSPACE}"/dev-values.yaml'
    //Yaml parser = new Yaml()
    //List example = parser.load(("${env.WORKSPACE}/dev-values.yaml" as File).text)

    datas.each{println it.subject}
}


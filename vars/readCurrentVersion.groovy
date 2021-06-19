#!groovy

@Grab('org.yaml:snakeyaml:1.17')

import org.yaml.snakeyaml.Yaml

def call() {
    Yaml parser = new Yaml()
    List example = parser.load(("${env.WORKSPACE}/dev-values.yaml" as File).text)

    echo "Print dev-values.yaml"
    example.each{println it.subject}
}


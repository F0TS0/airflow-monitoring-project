terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}

resource "docker_network" "airflow_network" {
  name = "airflow_network"
}

resource "docker_image" "smtp4dev" {
  name = "rnwood/smtp4dev"
}

resource "docker_container" "postgres" {
  name    = "postgres"
  image   = "postgres:13"
  restart = "always"

  env = [
    "POSTGRES_USER=airflow",
    "POSTGRES_PASSWORD=airflow",
    "POSTGRES_DB=airflow"
  ]

  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U airflow"]
    interval = "10s"
    retries  = 5
  }

  ports {
    internal = 5432
    external = 5432
  }

  networks_advanced {
    name = docker_network.airflow_network.name
  }
}

resource "docker_container" "smtp4dev" {
  name    = "smtp4dev"
  image   = docker_image.smtp4dev.name
  restart = "always"

  ports {
    internal = 25
    external = 25
  }

  ports {
    internal = 80
    external = 5050
  }

  networks_advanced {
    name = docker_network.airflow_network.name
  }
}

resource "docker_container" "airflow" {
  name    = "airflow"
  image   = "apache/airflow:2.8.0"
  restart = "always"

  depends_on = [
    docker_container.postgres,
    docker_container.smtp4dev
  ]

  ports {
    internal = 8080
    external = 8080
  }

  volumes {
    host_path      = abspath("${path.module}/../dags")
    container_path = "/opt/airflow/dags"
  }

  command = ["airflow", "standalone"]

  networks_advanced {
    name = docker_network.airflow_network.name
  }
}

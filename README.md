# Airflow Memory Monitor Setup

This project sets up Apache Airflow using Terraform and configures it with Ansible. A DAG is included to monitor Airflow's memory usage and send an alert email if it exceeds 50 MB.

## Requirements

- Docker
- Terraform
- Ansible

## Setup Instructions

### 1. Terraform Setup

Run the following commands to create the required containers and network:

```
cd terraform
terraform init
terraform apply
```

This will start containers for:

- Postgres
- SMTP4Dev (for test emails)
- Airflow

### 2. Configure Airflow with Ansible

Run the Ansible playbook to configure Airflow:

```
cd ../ansible
ansible-playbook provision-airflow.yml -i inventory --ask-become-pass
```

This will:

- Set Airflow environment variables
- Create the required Docker network
- Remove old containers if needed
- Launch the Airflow container
- Wait for Postgres to become ready
- Initialize the Airflow metadata database
- Create an Airflow user with:
  - Username: Admin
  - Password: Admin

### 3. DAG for Memory Monitoring

A DAG named `memory_alert_email_dag` runs every minute. It checks the memory usage of the Airflow process. If it goes above 50 MB, it sends an email using SMTP4Dev.

To view the email, open your browser and go to:

```
http://localhost:5050
```

### 4. Accessing Airflow UI

Go to:

```
http://localhost:8080
```

Log in with:

- Username: Admin
- Password: Admin

If you're unsure about the password, you can always retrieve it by accessing the container:

```
docker exec -it airflow bash
```

---

That's it! Your Airflow system is now up and monitoring. Happy automating!

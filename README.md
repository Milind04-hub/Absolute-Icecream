# Absolute Icecream

Premium direct-to-consumer ice cream storefront built with Flask.

## Technology

- Python 3.10+
- Flask, Jinja2, SQLAlchemy, and Flask-Migrate
- SQLite for local development; PostgreSQL is supported for deployment
- Redis and Celery for background tasks
- HTML, CSS, and JavaScript

## Local development

### Requirements

Install Git and Python 3.10 or later. On Windows, install Python with the
Python Launcher (`py`) enabled. PostgreSQL and Redis are not needed for a basic
local run; the development settings use SQLite.

### macOS

1. Clone the repository (replace the placeholder with the repository URL):

	```sh
	git clone <repository-url> absolute-icecream
	cd absolute-icecream
	```

2. Create a virtual environment and install project requirements:

	```sh
	python3 -m venv .venv
	source .venv/bin/activate
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt
	```

3. Make a private local environment file:

	```sh
	cp .env.example .env
	```

	Edit `.env`. Set a unique, strong `SECRET_KEY` and `ADMIN_PASSWORD` for your
	local environment. Do not commit `.env` or use development secrets in
	production.

4. Apply database migrations and start Flask:

	```sh
	flask --app run.py db upgrade
	flask --app run.py --debug run
	```

5. Visit <http://127.0.0.1:5000>. Stop the server with Control-C. Run tests
	from the activated virtual environment with:

	```sh
	python -m pytest
	```

### Windows (PowerShell)

1. Clone the repository and enter its directory:

	```powershell
	git clone <repository-url> absolute-icecream
	Set-Location absolute-icecream
	```

2. Create a virtual environment, activate it, and install dependencies:

	```powershell
	py -3 -m venv .venv
	.\.venv\Scripts\Activate.ps1
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt
	```

	If PowerShell prevents activation, use `\.venv\Scripts\python.exe -m pip`
	for the pip commands and `\.venv\Scripts\python.exe -m flask` for Flask
	commands; activation is optional.

3. Create a private local environment file:

	```powershell
	Copy-Item .env.example .env
	```

	Edit `.env`. Set a unique, strong `SECRET_KEY` and `ADMIN_PASSWORD` for your
	local environment. Do not commit `.env` or use development secrets in
	production.

4. Apply database migrations and start Flask:

	```powershell
	python -m flask --app run.py db upgrade
	python -m flask --app run.py --debug run
	```

5. Visit <http://127.0.0.1:5000>. Stop the server with Control-C. Run tests
	from the activated virtual environment with:

	```powershell
	python -m pytest
	```

### Optional sample data

To populate local development data, launch the Flask shell after setting up
`.env`:

```sh
flask --app run.py shell
```

Then, at the Python prompt, run:

```python
from app.seed.seed_products import seed_products
seed_products()

from app.seed.admin import create_initial_admin
create_initial_admin()
```

On Windows, start the shell with `python -m flask --app run.py shell`. The
admin account is created using the `ADMIN_NAME`, `ADMIN_EMAIL`, and
`ADMIN_PASSWORD` values in `.env`. Only use non-production credentials locally.

## Keeping secrets out of Git

- `.env` and other local environment files, local databases, virtual
  environments, and common private key/credential files are excluded by
  `.gitignore`.
- `.env.example` is a placeholder template and remains trackable. Never put
  real passwords, API keys, tokens, or production database URLs in it.
- Before pushing changes, review `git status` and the staged diff for secrets.
  Ignore rules do not remove files already tracked or erase committed secrets
  from repository history. If a secret was exposed, revoke or rotate it.

## Optional Docker setup

Docker Compose can start the web app with PostgreSQL and Redis. Create `.env`
from `.env.example` first, replace local credentials, then run:

```sh
docker compose up --build
```

The app is available at <http://127.0.0.1:5000>. Stop the stack with
`docker compose down`; add `--volumes` only if you also intend to delete the
local PostgreSQL data volume.

## Free hosting on Render (demo)

This is the quickest way to get a public link for the storefront and the
product report QR codes.

1. Push this repository to GitHub.
2. On [render.com](https://render.com), sign in with GitHub and choose
   **New > Blueprint**, select this repository, then **Apply**. Render reads
   `render.yaml` and creates a free web service.
3. Wait for the first deploy to finish, then open the service URL, for
   example `https://absolute-icecream.onrender.com`.
4. Check a report page: `/reports/dark-chocolate`. The "Opens" line under the
   QR must show your public `https://` address.

How the QR codes stay correct: report links are built from `PUBLIC_BASE_URL`
if you set it (use this for a custom domain), otherwise from Render's own
`RENDER_EXTERNAL_URL`. They are never built from `127.0.0.1` or an internal
host. `TRUST_PROXY_HEADERS=1` lets Flask see the real `https` address behind
Render's proxy.

Print-ready QR images for every flavour:

```sh
flask --app run.py export-qr --base-url https://absolute-icecream.onrender.com
```

This writes one PNG per product to `qr_exports/`.

Notes for the free tier:

- The service sleeps after about 15 minutes without visits, and the next
  visit takes up to a minute to wake it. Open the site a few minutes before a
  live demo.
- The demo uses SQLite on a temporary disk, so orders and accounts reset on
  every restart; products are re-seeded automatically by
  `scripts/bootstrap.py`. Use a hosted PostgreSQL `DATABASE_URL` for anything
  that must persist.
- `SHOW_SAMPLE_LAB_REPORTS=1` shows clearly labelled sample lab results from
  `app/data/lab_reports.py`. Set it to `0` (the default) for a real launch and
  replace the sample data with verified results.

## AWS hosting (ECS Fargate)

The AWS deployment files are in `deploy/aws/terraform`. They provision an
HTTPS Application Load Balancer, ECS Fargate web service, private encrypted
RDS PostgreSQL database, ECR repository, CloudWatch logs, and a Secrets Manager
secret for the Flask signing key and database URL. The app image is built from
the existing `Dockerfile`; no application source or local Docker Compose
configuration is changed. `.dockerignore` prevents `.env`, local databases,
and developer files from being sent in the Docker build context.

The initial ECS service count is zero intentionally. Push an image and run the
database migration as a one-off task before starting web tasks. The app's
current runtime does not use Celery tasks or require Redis, so this baseline
does not create an ElastiCache cluster. It also does not configure payments,
uploads, or object storage. Add those services only when the corresponding
application integrations are implemented.

### Prerequisites

- An AWS account with permissions to create VPC, ECS, ECR, RDS, ALB, IAM,
	CloudWatch, and Secrets Manager resources.
- AWS CLI v2 authenticated to the target account. Prefer `aws configure sso`
	and short-lived SSO credentials; do not put AWS access keys in the repo.
- Terraform 1.6 or later and Docker with Buildx.
- A domain name and an ACM certificate in the same AWS region you will deploy
	to. Request and validate the certificate before Terraform provisioning.
- AWS service quota for at least two available Availability Zones and Fargate.

### macOS provisioning and release

1. From the repository root, make the private Terraform variables file and
	 configure its AWS region and certificate ARN:

	 ```sh
	 cp deploy/aws/terraform/terraform.tfvars.example deploy/aws/terraform/terraform.tfvars
	 # Edit deploy/aws/terraform/terraform.tfvars before applying.
	 ```

2. Provision the stack with no running web tasks:

	 ```sh
	 terraform -chdir=deploy/aws/terraform init
	 terraform -chdir=deploy/aws/terraform plan -var='desired_count=0'
	 terraform -chdir=deploy/aws/terraform apply -var='desired_count=0'
	 ```

3. Build and push a unique image tag for the Fargate x86_64 runtime. Set
	 `AWS_REGION` to the same region used in `terraform.tfvars`:

	 ```sh
	 export AWS_REGION=ap-south-1
	 ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
	 ECR_URL="$(terraform -chdir=deploy/aws/terraform output -raw ecr_repository_url)"
	 IMAGE_TAG="sha-$(git rev-parse --short=7 HEAD)"
	 aws ecr get-login-password --region "$AWS_REGION" \
		 | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
	 docker buildx build --platform linux/amd64 --provenance=false \
		 --tag "$ECR_URL:$IMAGE_TAG" --push .
	 terraform -chdir=deploy/aws/terraform apply \
		 -var='desired_count=0' -var="app_image_tag=$IMAGE_TAG"
	 ```

4. Run the database migration once, before starting the service:

	 ```sh
	 TF_DIR=deploy/aws/terraform
	 CLUSTER="$(terraform -chdir="$TF_DIR" output -raw ecs_cluster_name)"
	 TASK_DEF="$(terraform -chdir="$TF_DIR" output -raw ecs_task_definition_arn)"
	 WEB_SG="$(terraform -chdir="$TF_DIR" output -raw web_security_group_id)"
	 SUBNETS="$(terraform -chdir="$TF_DIR" output -json public_subnet_ids | python3 -c 'import json,sys; print(",".join(json.load(sys.stdin)))')"
	 TASK_ARN="$(aws ecs run-task --region "$AWS_REGION" --cluster "$CLUSTER" \
		 --launch-type FARGATE --task-definition "$TASK_DEF" \
		 --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$WEB_SG],assignPublicIp=ENABLED}" \
		 --overrides '{"containerOverrides":[{"name":"web","command":["python","-m","flask","--app","run.py","db","upgrade"]}]}' \
		 --query 'tasks[0].taskArn' --output text)"
	 aws ecs wait tasks-stopped --region "$AWS_REGION" --cluster "$CLUSTER" --tasks "$TASK_ARN"
	 aws ecs describe-tasks --region "$AWS_REGION" --cluster "$CLUSTER" --tasks "$TASK_ARN" \
		 --query 'tasks[0].containers[0].[lastStatus,exitCode,reason]' --output table
	 ```

	 Continue only if the migration task stopped with exit code `0`. If the task
	 fails, inspect its `/ecs/absolute-icecream-production` CloudWatch log stream.

5. Start the web service and wait for it to become healthy:

	 ```sh
	 terraform -chdir=deploy/aws/terraform apply \
		 -var='desired_count=1' -var="app_image_tag=$IMAGE_TAG"
	 aws ecs wait services-stable --region "$AWS_REGION" \
		 --cluster "$CLUSTER" --services "$(terraform -chdir="$TF_DIR" output -raw ecs_service_name)"
	 terraform -chdir=deploy/aws/terraform output load_balancer_dns_name
	 ```

	 Create a DNS record for your hostname pointing to the ALB DNS name. Use an
	 ALIAS record for a Route 53 zone apex, or a CNAME for a subdomain. Visit the
	 hostname over HTTPS and confirm the ALB target is healthy.

### Windows (PowerShell) AWS release

Install AWS CLI v2, Terraform 1.6+, Docker Desktop with Linux containers, and
Git. Authenticate with `aws configure sso`, then run these commands from the
repository root. Copy and edit the Terraform variables template as described
above. All Terraform commands below create the infrastructure with zero web
tasks until the image and migration are ready.

```powershell
$AwsRegion = "ap-south-1" # Match aws_region in terraform.tfvars
$TfDir = "deploy/aws/terraform"
terraform -chdir=$TfDir init
terraform -chdir=$TfDir plan -var="desired_count=0"
terraform -chdir=$TfDir apply -var="desired_count=0"

$AccountId = aws sts get-caller-identity --query Account --output text
$EcrUrl = terraform -chdir=$TfDir output -raw ecr_repository_url
$ImageTag = "sha-$(git rev-parse --short=7 HEAD)"
aws ecr get-login-password --region $AwsRegion | docker login --username AWS --password-stdin "$AccountId.dkr.ecr.$AwsRegion.amazonaws.com"
docker buildx build --platform linux/amd64 --provenance=false --tag "${EcrUrl}:${ImageTag}" --push .
terraform -chdir=$TfDir apply -var="desired_count=0" -var="app_image_tag=$ImageTag"

$Cluster = terraform -chdir=$TfDir output -raw ecs_cluster_name
$TaskDefinition = terraform -chdir=$TfDir output -raw ecs_task_definition_arn
$WebSecurityGroup = terraform -chdir=$TfDir output -raw web_security_group_id
$PublicSubnets = (terraform -chdir=$TfDir output -json public_subnet_ids | ConvertFrom-Json) -join ","
$Network = "awsvpcConfiguration={subnets=[$PublicSubnets],securityGroups=[$WebSecurityGroup],assignPublicIp=ENABLED}"
$Overrides = '{"containerOverrides":[{"name":"web","command":["python","-m","flask","--app","run.py","db","upgrade"]}]}'
$MigrationTask = aws ecs run-task --region $AwsRegion --cluster $Cluster --launch-type FARGATE --task-definition $TaskDefinition --network-configuration $Network --overrides $Overrides --query "tasks[0].taskArn" --output text
aws ecs wait tasks-stopped --region $AwsRegion --cluster $Cluster --tasks $MigrationTask
aws ecs describe-tasks --region $AwsRegion --cluster $Cluster --tasks $MigrationTask --query "tasks[0].containers[0].[lastStatus,exitCode,reason]" --output table

# Only after verifying migration exit code 0:
terraform -chdir=$TfDir apply -var="desired_count=1" -var="app_image_tag=$ImageTag"
aws ecs wait services-stable --region $AwsRegion --cluster $Cluster --services (terraform -chdir=$TfDir output -raw ecs_service_name)
terraform -chdir=$TfDir output load_balancer_dns_name
```

Create the DNS record for your hostname to point to the printed ALB name. Do
not proceed to the service scale-up if the migration task exit code is not `0`.

### AWS security, state, and cost notes

- RDS is encrypted, has automated backups, and is not publicly accessible. Its
	security group accepts PostgreSQL only from the web task security group.
	Task inbound traffic is restricted to the ALB security group; HTTPS redirects
	from HTTP, and the Flask signing key/database URL come from Secrets Manager.
- Fargate tasks use public subnets/public IPs to avoid NAT Gateway charges, but
	their security group permits inbound port 5000 only from the ALB. For stricter
	egress isolation, move tasks to private subnets and provision NAT or the
	required VPC endpoints; this adds AWS resources and cost.
- Terraform state contains generated DB credentials and secret values. The
	repository ignores state, plans, and private `terraform.tfvars`, but that is
	not a substitute for secure state storage. For a team, use a dedicated,
	encrypted, versioned S3 backend with tightly restricted IAM and locking
	enabled, and never commit local state files.
- The starter defaults to one small RDS instance and no web tasks until the
	migration is complete. AWS charges for the ALB, RDS, storage/backups, logs,
	and running tasks. Review current regional pricing and quotas before apply.
- RDS deletion protection is enabled and a final snapshot is required. Plan
	backups, retention, monitoring, and recovery before production use; do not
	remove protection just to make teardown easier.
- For a deliberate full teardown only, first back up the database and run
	Terraform with `-var='desired_count=0' -var='db_deletion_protection=false'`,
	review the changes, then run `terraform destroy` with those same variable
	overrides. Preserve the final snapshot if the data may be needed.
- This Terraform setup does not create a superuser or seed catalogue data.
	Seed data/admin onboarding should be performed as a separately controlled
	one-off operation using credentials stored in AWS Secrets Manager, not in
	source control or shell history.

### Terraform files

- `deploy/aws/terraform/terraform.tfvars.example` is a safe starting template.
- `deploy/aws/terraform/main.tf` defines the network, ECS, ALB, RDS, ECR,
	Secrets Manager, IAM, and log resources.
- To destroy an environment, first scale the service to zero. Review Terraform's
	destroy plan carefully: RDS deletion protection and its final snapshot are
	intentional safeguards.
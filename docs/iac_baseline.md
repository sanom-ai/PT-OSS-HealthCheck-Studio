# IaC Baseline (Phase 1)

## Goals
Provide Terraform modules for baseline infra: VPC, managed PostgreSQL, S3-compatible object store, container registry, and CI runner.

## Minimal structure
- infra/terraform/modules/
  - network/
  - database/
  - object_storage/
  - registry/
  - ci_runner/

## Tools
- Terraform (0.15+ recommended)
- Terraform state stored in backend (S3 + Dynamo / cloud backend)
- Use GitHub Actions to run `terraform fmt`, `terraform validate`, and `terraform plan` for PRs

## Migration & DB
- Use Alembic for DB migrations
- Include terragrunt or a lightweight wrapper if multi-env orchestration required

## Next steps
- Implement `modules/database` with provider-specific managed DB resources (AWS RDS / Azure DB for Postgres)
- Provide example `dev` and `staging` workspaces

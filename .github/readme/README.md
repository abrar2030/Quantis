# GitHub Workflows

This directory contains GitHub Actions workflow configurations for continuous integration and continuous deployment (CI/CD) of the Quantis platform.

## Contents

- `ci-cd.yml`: Main CI/CD pipeline configuration that handles testing, building, and deployment processes

## CI/CD Pipeline

The CI/CD pipeline performs the following operations:

1. **API Testing**: Runs tests for the backend API components
2. **Frontend Testing**: Runs tests for the frontend application
3. **Model Testing**: Runs tests for the machine learning models
4. **Docker Building**: Builds Docker images for containerized deployment
5. **Build and Deploy**: Deploys the application when changes are pushed to main/master branches

## Usage

These workflows are automatically triggered when:

- Code is pushed to main, master, or develop branches
- Pull requests are created against main, master, or develop branches

No manual intervention is required for the workflows to run.

## Configuration

To modify the CI/CD pipeline:

1. Edit the `ci-cd.yml` file
2. Commit and push changes to the repository
3. GitHub Actions will use the updated configuration for subsequent runs

## Dependencies

The workflows depend on:

- GitHub Actions runners
- Python 3.10
- Node.js 18
- Docker Buildx

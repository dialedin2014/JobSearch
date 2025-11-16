#!/bin/bash
# GitHub Integration Test Runner
# This script runs the GitHub integration test without loading the full application

cd /workspace/backend
/workspace/.venv/bin/python run_github_test.py

# Custom Kubernetes Scheduler

## Overview
This project implements a custom secondary scheduler for Kubernetes clusters with advanced scheduling capabilities including gang scheduling and preemption support. The scheduler is designed to work alongside the default Kubernetes scheduler, providing additional scheduling strategies for specific workloads.

## Features

### Gang Scheduling
- Coordinates the scheduling of related pods as a group
- Ensures all pods in a gang are scheduled together or not at all
- Uses job-id labels to identify pod groups

### Preemption Support
- Implements priority-based pod preemption
- Handles resource conflicts by evicting lower priority pods
- Maintains system stability while maximizing resource utilization

### Priority Handling
- Respects pod priority classes
- Implements custom priority queue for pending pods
- Ensures fair scheduling based on pod priorities

## Installation

### Quick Start
Deploy the scheduler directly to your cluster:
```bash
kubectl apply -f https://raw.githubusercontent.com/roimor/roi-scheduler/refs/heads/main/deployment.yaml
```

## Usage

### Scheduling Pods with the Custom Scheduler
To use this scheduler for your pods, add the following to your pod specification:
```yaml
spec:
  schedulerName: roi-scheduler
```

## Development
The project is structured as follows:
- `scheduler.py`: Main scheduler implementation
- `gang_scheduler.py`: Gang scheduling logic
- `preemption.py`: Preemption handling
- `utils.py`: Utility functions
- `tests/`: Unit tests



# Backend Engineering Assignment:

## Hypervisor-like Service for MLOps Platform

### **Objective**

Design a backend service that manages user authentication, organization membership, cluster resource allocation, and deployment scheduling. The service will optimize for deployment priority, resource utilization, and maximizing successful deployments.

### Requirements

1. **User Authentication and Organization Management**

- **User Authentication**: Implement a basic authentication mechanism (e.g., username and password).
- **Invite Code**: Users can join an organization using an invite code.
- **Organization Membership**: Once authenticated, users are added to an organization.

2. **Cluster Management**

- **Cluster Creation**: Users can create a cluster with fixed resources (RAM, CPU, GPU).
- **Resource Management**: Track the available and allocated resources in each cluster.

3. **Deployment Management**

- **Create Deployment**: Users can create a deployment for any cluster by providing a Docker image path.
- **Resource Allocation for Deployment**: Each deployment requires a certain amount of resources (RAM, CPU, GPU).
- **Queue Deployments**: The deployment should be queued if the resources are unavailable in the cluster.
- Develop a preemption-based scheduling algorithm to prioritize high-priority deployments.

4. **Scheduling Algorithm**

- The scheduling algorithm should optimize for the following:
1. **Priority**: Higher priority deployments should be scheduled first.
2. **Resource Utilization**: Efficiently use available resources.
3. **Maximize Successful Deployments**: Maximize the number of deployments that can be successfully scheduled from the queue.

### Deliverables

1. **Code**: Provide the implementation of the backend service.
2. **Documentation**: Include documentation on how to set up and run the service.
3. **Tests**: Write unit tests for key components of the service.
4. **UML Diagram:** Include the UML diagram of the database.

### Implementation Guidelines

- Use Python as the programming language.
- You may use any web framework (e.g., Flask, FastAPI, Django).
- Store data in a simple database (e.g., SQLite, PostgreSQL).
- Use Redis, RabbitMQ, or any other queueing mechanism for scheduling.
- Focus on the management and scheduling logic, not the actual provisioning and deployment of resources.

### Evaluation Criteria

- **Correctness**: The implementation meets the requirements.
- **Code Quality**: Code is clean, readable, and well-documented.
- **Efficiency**: The scheduling algorithm effectively optimizes for priority, resource utilization, and successful deployments.
- **Testing**: Adequate unit tests are provided and they cover key scenarios.

### Bonus Points

- Implement a more advanced authentication mechanism (e.g., JWT).
- Use Docker to containerize the service.
- Add RBAC for Admin, Developer, and Viewer.
- Add support for deployment dependency management (e.g., Deployment A must complete before Deployment B starts).
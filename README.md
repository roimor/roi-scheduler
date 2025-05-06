# ssi

# Goal 
create a custom secondery scheduler for a local kubernetes cluster, which can schedule pods with schedulerName. 

## scheduler features
### Pods scheduler
    1. watch for new pending pods in the system 
    2. schedule pods in the order of their `priority` annotation (sort of all 'Pending' pods) 
        - try to bind pod (maybe multiple times)
        - if no nodes have enough resources to fit the pod
            - Simulate preemption by checking if evicting lower-priority pods would help
            - If so → preempt and schedule
            - If not → log or back off

### Gang scheduler
    watch for new jobs in the system
        - jobs will have X number of pods 
        - evalute available resources in the cluster to schedule all the pods at the same time. if there are not enough resources dont schedule any pods.
    

### Tests
    mocks for 
        1. new Pending pods with priority annotations
        2. new jobs yaml template 
        3. test for each function maybe



### script to set up the scheduler on an existing cluster 
# create_scheduler.sh $namespace
#`bash kubectl apply -f https://github.com/roimor/ssi-scheduler.yaml -n $1` 




# 📁 project layout:
# custom_k8s_scheduler/
# ├── scheduler.py
# ├── preemption.py
# ├── gang_scheduler.py
# ├── utils.py
# └── tests/
#     └── test_scheduler.py

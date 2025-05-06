from kubernetes import client, config, watch
from utils import get_pod_priority, list_unscheduled_pods, get_schedulable_nodes
from preemption import preempt_if_needed
from gang_scheduler import handle_gang_scheduling

SCHEDULER_NAME = "roi-scheduler"


def bind_pod_to_node(pod, node, v1):
    target = client.V1ObjectReference(kind="Node", api_version="v1", name=node.metadata.name)
    meta = client.V1ObjectMeta(name=pod.metadata.name, namespace=pod.metadata.namespace)
    body = client.V1Binding(target=target, metadata=meta)

    try:
        v1.create_namespaced_binding(namespace=pod.metadata.namespace, body=body)
        print(f"[Scheduler] Bound pod {pod.metadata.name} to node {node.metadata.name}")
    except client.exceptions.ApiException as e:
        print(f"[Error] Failed to bind pod {pod.metadata.name}: {e}")


def schedule():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()

    print("[Scheduler] Starting...")

    for event in w.stream(v1.list_pod_for_all_namespaces):
        pod = event['object']
        if pod.spec.scheduler_name != SCHEDULER_NAME:
            continue
        if pod.status.phase != "Pending":
            continue

        unscheduled_pods = list_unscheduled_pods(v1, SCHEDULER_NAME)
        nodes = get_schedulable_nodes(v1)

        sorted_pods = sorted(
            [p for p in unscheduled_pods if get_pod_priority(p) is not None],
            key=get_pod_priority,
            reverse=True
        )
        
        for pod in sorted_pods:
            # Skip gang if not schedulable
            if handle_gang_scheduling(pod, sorted_pods, nodes, v1):
                continue

            job_id = pod.metadata.annotations.get("job-id")
            if job_id:
                # Gang pod – schedule entire gang
                gang = [p for p in sorted_pods if p.metadata.annotations.get("job-id") == job_id]
                for p in gang:
                    for node in nodes:
                        if preempt_if_needed(p, node, v1):
                            bind_pod_to_node(p, node, v1)
                            break
                continue

            # Regular pod scheduling
            for node in nodes:
                if preempt_if_needed(pod, node, v1):
                    bind_pod_to_node(pod, node, v1)
                    break

if __name__ == "__main__":
    schedule()

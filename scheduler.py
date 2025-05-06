from kubernetes import client, config, watch
from utils import get_pod_priority, list_unscheduled_pods, get_schedulable_nodes
from preemption import preempt_if_needed
from gang_scheduler import handle_gang_scheduling

SCHEDULER_NAME = "roi-scheduler"


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

        # Gang-scheduling first
        if handle_gang_scheduling(pod, unscheduled_pods, nodes, v1):
            continue

        # Sort by priority and pick top pods
        sorted_pods = sorted(unscheduled_pods, key=get_pod_priority, reverse=True)
        top_pods = sorted_pods[:len(nodes)]

        for pod, node in zip(top_pods, nodes):
            if not preempt_if_needed(pod, node, v1):
                continue

            target = client.V1ObjectReference(kind="Node", api_version="v1", name=node.metadata.name)
            meta = client.V1ObjectMeta(name=pod.metadata.name, namespace=pod.metadata.namespace)
            body = client.V1Binding(target=target, metadata=meta)

            try:
                v1.create_namespaced_binding(namespace=pod.metadata.namespace, body=body)
                print(f"[Scheduler] Bound pod {pod.metadata.name} to node {node.metadata.name}")
            except client.exceptions.ApiException as e:
                print(f"[Error] Failed to bind pod {pod.metadata.name}: {e}")

if __name__ == "__main__":
    schedule()

def get_pod_priority(pod):
    try:
        return int(pod.metadata.annotations.get("priority", 0))
    except (AttributeError, ValueError):
        return 0


def list_unscheduled_pods(v1, scheduler_name):
    pods = v1.list_pod_for_all_namespaces().items
    return [p for p in pods if p.spec.scheduler_name == scheduler_name and p.status.phase == "Pending"]


def get_schedulable_nodes(v1):
    return [n for n in v1.list_node().items if is_node_ready(n)]


def is_node_ready(node):
    for condition in node.status.conditions:
        if condition.type == "Ready" and condition.status == "True":
            return True
    return False

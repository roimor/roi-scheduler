from utils import get_pod_priority, _get_millicores, _get_memory_bytes

def preempt_if_needed(pod, node, v1):
    # Attempts to schedule the pod on the node.
    # If there aren't enough free resources, it will try to preempt lower-priority pods to make room.
    required_cpu = _get_millicores(pod)
    required_mem = _get_memory_bytes(pod)

    running_pods = v1.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node.metadata.name}").items

    alloc_cpu = _get_millicores(node)
    alloc_mem = _get_memory_bytes(node)

    used_cpu = sum(_get_millicores(p) for p in running_pods)
    used_mem = sum(_get_memory_bytes(p) for p in running_pods)

    # If the node already has enough free resources, no need to preempt.
    if (alloc_cpu - used_cpu >= required_cpu) and (alloc_mem - used_mem >= required_mem):
        return True

    sorted_pods = sorted(running_pods, key=get_pod_priority)
    freed_cpu = alloc_cpu - used_cpu
    freed_mem = alloc_mem - used_mem

    # Try deleting lower-priority pods one by one until there's enough room.
    for victim in sorted_pods:
        if get_pod_priority(victim) >= get_pod_priority(pod):
            continue
        print(f"[Preempt] Deleting pod {victim.metadata.name} to make room for {pod.metadata.name}")
        # This is the actual preemption — delete the pod to free up resources.
        v1.delete_namespaced_pod(victim.metadata.name, victim.metadata.namespace)
        freed_cpu += _get_millicores(victim)
        freed_mem += _get_memory_bytes(victim)

        if freed_cpu >= required_cpu and freed_mem >= required_mem:
            return True

    return False

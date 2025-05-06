
# --- preemption.py ---
from utils import get_pod_priority

def preempt_if_needed(pod, node, v1):
    required_cpu = _get_millicores(pod)
    required_mem = _get_memory_bytes(pod)

    running_pods = v1.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node.metadata.name}").items

    # Simulate total allocatable resources
    alloc_cpu = _get_millicores(node)
    alloc_mem = _get_memory_bytes(node)

    used_cpu = 0
    used_mem = 0
    for p in running_pods:
        used_cpu += _get_millicores(p)
        used_mem += _get_memory_bytes(p)

    if (alloc_cpu - used_cpu >= required_cpu) and (alloc_mem - used_mem >= required_mem):
        return True  # no need to preempt

    # Try evicting lower-priority pods
    sorted_pods = sorted(running_pods, key=get_pod_priority)
    freed_cpu = alloc_cpu - used_cpu
    freed_mem = alloc_mem - used_mem

    for victim in sorted_pods:
        if get_pod_priority(victim) >= get_pod_priority(pod):
            continue
        print(f"[Preempt] Deleting pod {victim.metadata.name} to make room for {pod.metadata.name}")
        v1.delete_namespaced_pod(victim.metadata.name, victim.metadata.namespace)
        freed_cpu += _get_millicores(victim)
        freed_mem += _get_memory_bytes(victim)

        if freed_cpu >= required_cpu and freed_mem >= required_mem:
            return True

    return False


def _get_millicores(obj):
    try:
        return int(obj.spec.containers[0].resources.requests.get("cpu", "0m").replace("m", ""))
    except:
        return 0


def _get_memory_bytes(obj):
    try:
        raw = obj.spec.containers[0].resources.requests.get("memory", "0Mi")
        if raw.endswith("Mi"):
            return int(raw[:-2]) * 1024 * 1024
        elif raw.endswith("Gi"):
            return int(raw[:-2]) * 1024 * 1024 * 1024
    except:
        return 0
    return 0

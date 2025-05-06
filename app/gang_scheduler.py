from utils import _get_millicores, _get_memory_bytes

def handle_gang_scheduling(pod, unscheduled_pods, nodes, v1):
    # Gang scheduling requires all pods from a job to be schedulable together, or none.
    job_id = pod.metadata.annotations.get("job-id")
    if not job_id:
        return False

    # Get all unscheduled pods belonging to the same job
    gang = [p for p in unscheduled_pods if p.metadata.annotations.get("job-id") == job_id]

    # Sum total resource requests for the whole gang
    total_cpu = sum(_get_millicores(p) for p in gang)
    total_mem = sum(_get_memory_bytes(p) for p in gang)
    print(f"[Gang] Job {job_id} requests: CPU={total_cpu}m, Memory={total_mem / (1024 * 1024)} Mi")

    # Aggregate available resources across all ready nodes
    alloc_cpu = 0
    alloc_mem = 0
    for node in nodes:
        pods_on_node = v1.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node.metadata.name}").items
        used_cpu = sum(_get_millicores(p) for p in pods_on_node)
        used_mem = sum(_get_memory_bytes(p) for p in pods_on_node)

        alloc_cpu += _get_millicores(node) - used_cpu
        alloc_mem += _get_memory_bytes(node) - used_mem

    if alloc_cpu < total_cpu or alloc_mem < total_mem:
        print(f"[Gang] Not enough cluster resources for job {job_id}, skipping scheduling this gang.")
        return True  # skip scheduling this pod for now

    return False
# --- gang_scheduler.py ---
def handle_gang_scheduling(pod, unscheduled_pods, nodes, v1):
    job_id = pod.metadata.annotations.get("job-id")
    if not job_id:
        return False

    gang = [p for p in unscheduled_pods if p.metadata.annotations.get("job-id") == job_id]

    if len(gang) > len(nodes):
        print(f"[Gang] Not enough nodes for job {job_id}, skipping.")
        return True  # skip scheduling this pod

    # In a real case, bind them all at once here (omitted for simplicity)
    return False
# --- Integration tests (run manually with kind or minikube) ---
# You can use kubectl and subprocess in Python to test end-to-end logic
import subprocess
import time
import os
import unittest

class TestIntegrationScheduler(unittest.TestCase):

    def test_cluster_running(self):
        result = subprocess.run(["kubectl", "get", "nodes"], capture_output=True)
        self.assertEqual(result.returncode, 0)

    def test_custom_scheduler_pod_binding(self):
        pod_yaml = """
apiVersion: v1
kind: Pod
metadata:
  name: high-priority-pod
  annotations:
    priority: "100"
  labels:
    app: test
spec:
  schedulerName: roi-scheduler
  containers:
  - name: busybox
    image: busybox
    command: ["sleep", "3600"]
        """
        with open("temp-pod.yaml", "w") as f:
            f.write(pod_yaml)
        subprocess.run(["kubectl", "apply", "-f", "temp-pod.yaml"])
        time.sleep(10)  # wait for scheduler to act
        describe = subprocess.run(["kubectl", "describe", "pod", "high-priority-pod"], capture_output=True)
        os.remove("temp-pod.yaml")
        self.assertIn("Node:", describe.stdout.decode())


if __name__ == '__main__':
    unittest.main()

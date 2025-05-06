import unittest
import scheduler
from unittest.mock import patch
from types import SimpleNamespace

class TestSchedulerBinding(unittest.TestCase):
    def test_scheduler_binds_pending_pod(self):
        pod = SimpleNamespace(
            spec=SimpleNamespace(scheduler_name=scheduler.SCHEDULER_NAME),
            status=SimpleNamespace(phase='Pending'),
            metadata=SimpleNamespace(name='pod1', namespace='default', annotations={})
        )
        node = SimpleNamespace(
            metadata=SimpleNamespace(name='node1'),
            status=SimpleNamespace(conditions=[SimpleNamespace(type='Ready', status='True')])
        )
        bound = []
        class FakeV1:
            def list_pod_for_all_namespaces(self): return SimpleNamespace(items=[pod])
            def list_node(self): return SimpleNamespace(items=[node])
            def create_namespaced_binding(self, namespace, body): bound.append((namespace, body))
        class FakeWatch:
            def stream(self, _func): yield {'object': pod}
        with patch.object(scheduler.config, 'load_kube_config', lambda *args, **kwargs: None), \
             patch.object(scheduler, 'watch', SimpleNamespace(Watch=lambda: FakeWatch())), \
             patch.object(scheduler.client, 'CoreV1Api', lambda: FakeV1()):
            scheduler.schedule()
        self.assertEqual(len(bound), 1)
        ns, binding = bound[0]
        self.assertEqual(ns, 'default')
        self.assertEqual(binding.target.name, 'node1')

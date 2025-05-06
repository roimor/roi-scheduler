# --- tests/test_scheduler.py ---
import unittest
from types import SimpleNamespace
from utils import get_pod_priority


class TestSchedulerLogic(unittest.TestCase):

    def test_get_pod_priority_valid(self):
        pod = SimpleNamespace(metadata=SimpleNamespace(annotations={"priority": "5"}))
        self.assertEqual(get_pod_priority(pod), 5)

    def test_get_pod_priority_missing(self):
        pod = SimpleNamespace(metadata=SimpleNamespace(annotations={}))
        self.assertEqual(get_pod_priority(pod), 0)

    def test_get_pod_priority_invalid(self):
        pod = SimpleNamespace(metadata=SimpleNamespace(annotations={"priority": "not-an-int"}))
        self.assertEqual(get_pod_priority(pod), 0)

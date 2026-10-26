"""Offline tests: no credentials, workspace or network required."""
import os
import unittest
from unittest.mock import patch

from src.producer.efuse_producer import make_records, required_env
from src.producer.reliability_lab import build_records
from src.producer.schema_lab import make_record
from src.producer.zerobus_rest_producer import authorization_details
from src.benchmarks.benchmark import make_event


class RecordContracts(unittest.TestCase):
    def test_baseline_schema_and_unique_ids(self):
        records = make_records(10)
        self.assertEqual(len(records), 10)
        self.assertEqual(len({x["event_id"] for x in records}), 10)
        self.assertEqual(set(records[0]), {"event_id", "vehicle_id", "fuse_id", "current_a", "voltage_v", "switch_state", "event_ts"})

    def test_protocol_tagging(self):
        with patch.dict(os.environ, {"ZEROBUS_EVENT_PREFIX": "grpc-lab03-"}):
            self.assertTrue(make_records(1)[0]["event_id"].startswith("grpc-lab03-"))

    def test_missing_optional_and_new_column(self):
        self.assertNotIn("fuse_id", make_record("missing-optional"))
        self.assertIn("temperature_c", make_record("extra-before"))
        self.assertNotIn("vehicle_id", make_record("missing-required"))
        self.assertIsInstance(make_record("wrong-type")["current_a"], str)

    def test_reliability_stable_event_fields(self):
        records = build_records("replay-lab04-", 2)
        self.assertEqual(len({v["event_id"] for v in records}), 2)
        self.assertTrue(all(v["event_id"].startswith("replay-lab04-") for v in records))

    def test_benchmark_event_identity(self):
        self.assertEqual(make_event("abc", 4)["event_id"], "bench06-abc-4")

    def test_env_validation(self):
        with patch.dict(os.environ, {"DUMMY_ZEROBUS_TEST": "<not-set>"}):
            with self.assertRaises(ValueError):
                required_env("DUMMY_ZEROBUS_TEST")


class OAuthPayload(unittest.TestCase):
    def test_authorization_details(self):
        details = authorization_details("workspace.bronze.table")
        self.assertEqual(len(details), 3)
        self.assertEqual(details[-1]["operations"], ["zerobuswrite"])
        self.assertEqual(details[-1]["privileges"], ["SELECT", "MODIFY"])

    def test_invalid_target(self):
        with self.assertRaises(ValueError):
            authorization_details("not_fully_qualified")


if __name__ == "__main__":
    unittest.main()

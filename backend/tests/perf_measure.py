#!/usr/bin/env python3
"""
Phase 12.7 — Performance & Stability Measurement Harness

Measures backend performance across vault sizes: 100, 500, 1000, 5000 entries.
Communicates with the IPC bridge via stdin/stdout JSON-RPC, exactly as Tauri does.

Usage:
    cd backend
    python -m tests.perf_measure

Prerequisites:
    - A vault must already be initialized (run the app once and set a master password)
    - The master password must be provided via MYPASS_TEST_PASSWORD env var
"""

import json
import os
import subprocess
import sys
import time
import statistics
import shutil
from pathlib import Path

# ── Configuration ──
DATASET_SIZES = [100, 500, 1000, 5000]
MASTER_PASSWORD = os.environ.get("MYPASS_TEST_PASSWORD", "TestPassword123!")
SEARCH_QUERIES = ["google", "bank", "test", "xyz-no-match", "a"]
NUM_SEARCH_ITERATIONS = 5
NUM_CRUD_ITERATIONS = 10

# ── IPC Helpers ──
class IPCClient:
    """Manages a subprocess running ipc_bridge.py and sends JSON-RPC requests."""

    def __init__(self, backend_dir: str):
        self.backend_dir = backend_dir
        venv_python = os.path.join(backend_dir, "venv", "bin", "python")
        python_cmd = venv_python if os.path.exists(venv_python) else sys.executable
        self.proc = subprocess.Popen(
            [python_cmd, "-m", "ipc_bridge"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=backend_dir,
            text=True,
            bufsize=1,
        )
        self._req_id = 0

    def call(self, method: str, params: dict = None) -> dict:
        self._req_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._req_id,
            "method": method,
            "params": params or {},
        }
        self.proc.stdin.write(json.dumps(request) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("IPC bridge closed unexpectedly")
        return json.loads(line.strip())

    def call_timed(self, method: str, params: dict = None) -> tuple[dict, float]:
        """Returns (response, elapsed_ms)."""
        start = time.perf_counter()
        resp = self.call(method, params)
        elapsed = (time.perf_counter() - start) * 1000
        return resp, elapsed

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()


def generate_entry(index: int) -> dict:
    """Generate a realistic vault entry for seeding."""
    domains = [
        "google.com", "github.com", "amazon.com", "netflix.com", "apple.com",
        "twitter.com", "facebook.com", "linkedin.com", "dropbox.com", "slack.com",
        "bankofamerica.com", "chase.com", "wellsfargo.com", "paypal.com", "stripe.com",
        "reddit.com", "stackoverflow.com", "medium.com", "notion.so", "figma.com",
    ]
    categories = ["Passwords", "Banking", "Social", "Work", "Shopping", "Development"]
    domain = domains[index % len(domains)]
    cat = categories[index % len(categories)]
    return {
        "title": f"{domain.split('.')[0].title()} Account {index}",
        "username": f"user{index}@{domain}",
        "password": f"P@ssw0rd!{index:04d}#{domain[:3]}",
        "website_url": f"https://www.{domain}",
        "notes": f"Test entry #{index} for performance measurement. Category: {cat}.",
        "category": cat,
        "favorite": index % 7 == 0,
    }


def measure_phase(client: IPCClient, target_count: int, results: dict):
    """Run all measurements for a given vault size."""
    phase_key = f"{target_count}_entries"
    phase = {}
    results[phase_key] = phase

    # ── 1. Check current count ──
    resp = client.call("vault.list_entries")
    current_count = len(resp["result"]["data"]) if resp["result"]["success"] else 0

    # ── 2. Seed entries to reach target ──
    entries_to_add = target_count - current_count
    if entries_to_add > 0:
        print(f"  Seeding {entries_to_add} entries to reach {target_count}...")
        seed_start = time.perf_counter()
        for i in range(entries_to_add):
            entry = generate_entry(current_count + i)
            resp = client.call("vault.create_entry", entry)
            if not resp["result"]["success"]:
                print(f"    ERROR creating entry {i}: {resp['result'].get('error', {}).get('message')}")
                break
            if (i + 1) % 100 == 0:
                print(f"    ... {i + 1}/{entries_to_add} seeded")
        seed_elapsed = (time.perf_counter() - seed_start) * 1000
        phase["seed_time_ms"] = round(seed_elapsed, 2)
        phase["seed_per_entry_ms"] = round(seed_elapsed / entries_to_add, 2) if entries_to_add > 0 else 0
        print(f"  Seeding complete: {seed_elapsed:.0f}ms total, {seed_elapsed/max(entries_to_add,1):.1f}ms/entry")

    # ── 3. List all entries (simulates workspace render) ──
    print(f"  Measuring list_entries ({target_count} entries)...")
    list_times = []
    for _ in range(NUM_CRUD_ITERATIONS):
        _, elapsed = client.call_timed("vault.list_entries")
        list_times.append(elapsed)
    phase["list_entries"] = {
        "mean_ms": round(statistics.mean(list_times), 2),
        "median_ms": round(statistics.median(list_times), 2),
        "p95_ms": round(sorted(list_times)[int(len(list_times) * 0.95)], 2),
        "min_ms": round(min(list_times), 2),
        "max_ms": round(max(list_times), 2),
    }
    print(f"    list_entries: mean={phase['list_entries']['mean_ms']}ms, p95={phase['list_entries']['p95_ms']}ms")

    # ── 4. Search latency ──
    print(f"  Measuring search latency...")
    search_results = {}
    for query in SEARCH_QUERIES:
        times = []
        hit_counts = []
        for _ in range(NUM_SEARCH_ITERATIONS):
            # Search is done client-side in the frontend, but the bottleneck is list_all_entries + decrypt.
            # We measure list_entries (which does the decrypt) since that's the IPC call the frontend makes.
            # The frontend then filters in JS. So we measure the raw data fetch.
            start = time.perf_counter()
            resp = client.call("vault.list_entries")
            elapsed = (time.perf_counter() - start) * 1000
            # Simulate frontend-side search
            entries = resp["result"]["data"]
            q = query.lower()
            matches = [e for e in entries if q in e.get("title", "").lower() or q in e.get("username", "").lower() or q in e.get("website_url", "").lower()]
            times.append(elapsed)
            hit_counts.append(len(matches))
        search_results[query] = {
            "mean_ms": round(statistics.mean(times), 2),
            "hits": hit_counts[0],
        }
    phase["search"] = search_results
    for q, r in search_results.items():
        print(f"    search '{q}': {r['mean_ms']}ms, {r['hits']} hits")

    # ── 5. Single CRUD operations ──
    print(f"  Measuring CRUD operations...")

    # Create
    create_times = []
    created_ids = []
    for i in range(NUM_CRUD_ITERATIONS):
        entry = generate_entry(99000 + i)
        resp, elapsed = client.call_timed("vault.create_entry", entry)
        create_times.append(elapsed)
        if resp["result"]["success"]:
            created_ids.append(resp["result"]["data"]["id"])

    # Read (get single entry)
    read_times = []
    for eid in created_ids[:NUM_CRUD_ITERATIONS]:
        # There's no vault.get_entry IPC method, so we measure list + filter
        # Actually reading the IPC bridge, there's no get_entry method exposed.
        # The frontend uses list_entries and selects. So we skip individual read.
        pass

    # Update
    update_times = []
    for eid in created_ids[:NUM_CRUD_ITERATIONS]:
        resp, elapsed = client.call_timed("vault.update_entry", {
            "id": eid,
            "title": f"Updated Entry {eid}",
            "notes": "Updated during perf measurement",
        })
        update_times.append(elapsed)

    # Delete
    delete_times = []
    for eid in created_ids:
        resp, elapsed = client.call_timed("vault.delete_entry", {"id": eid})
        delete_times.append(elapsed)

    phase["crud"] = {
        "create": {
            "mean_ms": round(statistics.mean(create_times), 2),
            "max_ms": round(max(create_times), 2),
        },
        "update": {
            "mean_ms": round(statistics.mean(update_times), 2),
            "max_ms": round(max(update_times), 2),
        },
        "delete": {
            "mean_ms": round(statistics.mean(delete_times), 2),
            "max_ms": round(max(delete_times), 2),
        },
    }
    print(f"    create: {phase['crud']['create']['mean_ms']}ms avg")
    print(f"    update: {phase['crud']['update']['mean_ms']}ms avg")
    print(f"    delete: {phase['crud']['delete']['mean_ms']}ms avg")

    # ── 6. Backup export ──
    print(f"  Measuring backup export...")
    export_times = {}
    for fmt in ["json", "mypass"]:
        times = []
        for _ in range(3):
            resp, elapsed = client.call_timed("backup.export", {"format": fmt})
            times.append(elapsed)
        export_times[fmt] = {
            "mean_ms": round(statistics.mean(times), 2),
            "max_ms": round(max(times), 2),
        }
        print(f"    export {fmt}: {export_times[fmt]['mean_ms']}ms avg")
    phase["backup_export"] = export_times


def main():
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    # Normalize
    backend_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

    # build_data_path(".mypass_data") resolves to ~/  + ".mypass_data"
    # We need to use a temp directory as the base so ipc_bridge finds the DB at <base>/.mypass_data/mypass.db
    home_dir = os.path.expanduser("~")
    real_db = os.path.join(home_dir, ".mypass_data", "mypass.db")

    # Create a temp base directory. IPC bridge will look for <MYPASS_DATA_DIR>/.mypass_data/mypass.db
    import tempfile
    perf_base = tempfile.mkdtemp(prefix="mypass_perf_")
    perf_db_dir = os.path.join(perf_base, ".mypass_data")
    os.makedirs(perf_db_dir, exist_ok=True)
    perf_db = os.path.join(perf_db_dir, "mypass.db")

    # Copy real DB as starting point (so we have the vault metadata/salt)
    if os.path.exists(real_db):
        shutil.copy2(real_db, perf_db)
        print(f"Copied real DB to perf workspace: {perf_db}")
    else:
        print(f"ERROR: No vault database found at {real_db}")
        print("Please run the app and create a vault first.")
        sys.exit(1)

    # Override the data path for the IPC bridge
    os.environ["MYPASS_DATA_DIR"] = perf_base

    print("=" * 70)
    print("Phase 12.7 — Performance & Stability Measurement")
    print("=" * 70)

    client = IPCClient(backend_dir)

    try:
        # Ping
        resp = client.call("system.ping")
        print(f"IPC bridge: {resp['result']['data']['status']}")

        # Unlock
        print(f"Unlocking vault...")
        resp = client.call("auth.unlock", {"masterPassword": MASTER_PASSWORD})
        if not resp["result"]["success"]:
            print(f"ERROR: Failed to unlock vault: {resp['result'].get('error', {}).get('message')}")
            print("Set MYPASS_TEST_PASSWORD to your master password.")
            sys.exit(1)
        print("Vault unlocked successfully.")

        results = {}
        results["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        results["datasets"] = DATASET_SIZES

        for size in DATASET_SIZES:
            print(f"\n{'─' * 50}")
            print(f"DATASET: {size} entries")
            print(f"{'─' * 50}")
            measure_phase(client, size, results)

        # ── Unlock time measurement ──
        print(f"\n{'─' * 50}")
        print("UNLOCK TIME (with 5000 entries in DB)")
        print(f"{'─' * 50}")
        unlock_times = []
        for _ in range(5):
            client.call("auth.lock")
            _, elapsed = client.call_timed("auth.unlock", {"masterPassword": MASTER_PASSWORD})
            unlock_times.append(elapsed)
        results["unlock_time_5000"] = {
            "mean_ms": round(statistics.mean(unlock_times), 2),
            "median_ms": round(statistics.median(unlock_times), 2),
            "max_ms": round(max(unlock_times), 2),
        }
        print(f"  Unlock: mean={results['unlock_time_5000']['mean_ms']}ms, max={results['unlock_time_5000']['max_ms']}ms")

        # ── Save results ──
        output_path = os.path.join(backend_dir, "tests", "perf_results.json")
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_path}")

        # ── Print summary ──
        print(f"\n{'=' * 70}")
        print("SUMMARY")
        print(f"{'=' * 70}")
        print(f"{'Dataset':>10} | {'List (mean)':>12} | {'List (p95)':>12} | {'Create':>10} | {'Export .mypass':>15}")
        print(f"{'─' * 10}-+-{'─' * 12}-+-{'─' * 12}-+-{'─' * 10}-+-{'─' * 15}")
        for size in DATASET_SIZES:
            key = f"{size}_entries"
            d = results[key]
            print(f"{size:>10} | {d['list_entries']['mean_ms']:>10.1f}ms | {d['list_entries']['p95_ms']:>10.1f}ms | {d['crud']['create']['mean_ms']:>8.1f}ms | {d['backup_export']['mypass']['mean_ms']:>13.1f}ms")

    finally:
        client.close()
        # Cleanup perf DB
        if os.path.exists(perf_base):
            shutil.rmtree(perf_base)
            print(f"\nCleaned up perf workspace: {perf_base}")


if __name__ == "__main__":
    main()

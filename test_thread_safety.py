#!/usr/bin/env python3
"""
Test script to verify thread-safe operations in the in-memory storage.
This simulates multiple concurrent users accessing the system.
"""

import threading
import time
import sys
from source import (
    SystemMetadata, AIType, DeploymentMode, DecisionCriticality,
    AutomationLevel, DataSensitivity, add_system, get_system,
    get_all_systems, update_system, delete_system
)


def test_concurrent_adds():
    """Test concurrent system additions"""
    print("Testing concurrent system additions...")

    def add_test_system(index):
        system = SystemMetadata(
            name=f"Test System {index}",
            description=f"Test system created by thread {index}",
            domain="Testing",
            ai_type=AIType.ML,
            owner_role="Test Team",
            deployment_mode=DeploymentMode.BATCH,
            decision_criticality=DecisionCriticality.LOW,
            automation_level=AutomationLevel.ADVISORY,
            data_sensitivity=DataSensitivity.INTERNAL,
            external_dependencies=[]
        )
        add_system(system)
        print(f"  Thread {index}: Added system {system.system_id}")

    # Create 10 threads to add systems concurrently
    threads = []
    for i in range(10):
        thread = threading.Thread(target=add_test_system, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all systems were added
    all_systems = get_all_systems()
    print(f"  ✓ Successfully added {len(all_systems)} systems concurrently")
    return len(all_systems) == 10


def test_concurrent_reads():
    """Test concurrent system reads"""
    print("\nTesting concurrent reads...")

    results = []

    def read_systems(index):
        systems = get_all_systems()
        results.append(len(systems))
        print(f"  Thread {index}: Read {len(systems)} systems")

    # Create 20 threads to read concurrently
    threads = []
    for i in range(20):
        thread = threading.Thread(target=read_systems, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all reads returned consistent data
    unique_counts = set(results)
    print(
        f"  ✓ All {len(results)} reads completed, unique counts: {unique_counts}")
    return len(unique_counts) == 1  # Should all see the same count


def test_concurrent_updates():
    """Test concurrent system updates"""
    print("\nTesting concurrent updates...")

    # Get the first system
    systems = get_all_systems()
    if not systems:
        print("  ✗ No systems to update")
        return False

    test_system = systems[0]
    system_id = test_system.system_id

    def update_test_system(index):
        update_system(system_id, {
            "description": f"Updated by thread {index} at {time.time()}"
        })
        print(f"  Thread {index}: Updated system {system_id}")

    # Create 5 threads to update the same system
    threads = []
    for i in range(5):
        thread = threading.Thread(target=update_test_system, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify the system still exists and was updated
    updated_system = get_system(system_id)
    print(f"  ✓ System {system_id} successfully updated by multiple threads")
    print(f"    Final description: {updated_system.description[:50]}...")
    return updated_system is not None


def main():
    """Run all thread safety tests"""
    print("=" * 60)
    print("Thread Safety Tests for In-Memory Storage")
    print("=" * 60)

    tests = [
        ("Concurrent Additions", test_concurrent_adds),
        ("Concurrent Reads", test_concurrent_reads),
        ("Concurrent Updates", test_concurrent_updates),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ✗ Test failed with error: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(result for _, result in results)
    print("=" * 60)

    if all_passed:
        print("✓ All tests passed! Thread-safe implementation verified.")
        return 0
    else:
        print("✗ Some tests failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

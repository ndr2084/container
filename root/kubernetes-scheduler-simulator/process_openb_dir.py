#!/usr/bin/env python3
import argparse
import yaml
from pathlib import Path

# ---------------------------
# Utility: Add rack labels to Nodes
# ---------------------------
def add_rack_labels(nodes, rack_mod=10):
    rack_number = 0
    for node in nodes:
        node.setdefault("metadata", {})
        node["metadata"].setdefault("labels", {})
        node["metadata"]["labels"]["topology.kubernetes.io/rack"] = f"rack-{rack_number % rack_mod}"
        rack_number += 1
    return nodes

# ---------------------------
# Utility: Add topologySpreadConstraints to Pods
# ---------------------------
def add_topology_constraints(pods, topology_key="topology.kubernetes.io/rack", max_skew=1, when_unsatisfiable="ScheduleAnyway"):
    for pod in pods:
        if pod.get("kind") != "Pod":
            continue
        pod.setdefault("spec", {})
        pod["spec"]["topologySpreadConstraints"] = [{
            "maxSkew": max_skew,
            "topologyKey": topology_key,
            "whenUnsatisfiable": when_unsatisfiable,
            "labelSelector": {}  # minimal - no app grouping
        }]
    return pods

# ---------------------------
# Orchestrator
# ---------------------------
def process_directory(input_dir: str, rack_mod: int, max_skew: int):
    input_path = Path(input_dir)
    if not input_path.is_dir():
        print(f"❌ {input_dir} is not a valid directory")
        return

    # Detect files
    node_file = next(input_path.glob("openb_node_list_*.yaml"), None)
    pod_file  = next(input_path.glob("openb_pod_list_*.yaml"), None)

    if not node_file or not pod_file:
        print(f"❌ Could not find expected files in {input_dir}")
        print("   Expected:")
        print("     openb_node_list_*.yaml")
        print("     openb_pod_list_*.yaml")
        return

    print(f"✅ Found Node YAML: {node_file}")
    print(f"✅ Found Pod YAML:  {pod_file}")

    # Load Node docs
    with open(node_file, "r") as f:
        nodes = list(yaml.safe_load_all(f))

    # Load Pod docs
    with open(pod_file, "r") as f:
        pods = list(yaml.safe_load_all(f))

    # Process Nodes (add racks)
    nodes_with_racks = add_rack_labels(nodes, rack_mod=rack_mod)
    node_output_file = node_file.with_name(node_file.stem + "_with_rack-quantity"+str(rack_mod)+".yaml")
    with open(node_output_file, "w") as f:
        yaml.dump_all(nodes_with_racks, f, sort_keys=False)
    print(f"✅ Modified Node YAML → {node_output_file}")

    # Process Pods (add constraints)
    pods_with_constraints = add_topology_constraints(pods, topology_key="topology.kubernetes.io/rack", max_skew=max_skew)
    pod_output_file = pod_file.with_name(pod_file.stem + "_with_skew-value"+str(max_skew)+".yaml" )
    with open(pod_output_file, "w") as f:
        yaml.dump_all(pods_with_constraints, f, sort_keys=False)
    print(f"✅ Modified Pod YAML → {pod_output_file}")

# ---------------------------
# CLI entrypoint
# ---------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process an openb_pod_list_* directory: add rack labels to nodes & topology constraints to pods.")
    parser.add_argument("directory", help="Directory containing openb_node_list_*.yaml and openb_pod_list_*.yaml")
    parser.add_argument("--rack-mod", type=int, default=10, help="How many racks to cycle through (default 10)")
    parser.add_argument("--max-skew", type=int, default=1, help="maxSkew value for topologySpreadConstraints (default 1)")

    args = parser.parse_args()
    process_directory(args.directory, rack_mod=args.rack_mod, max_skew=args.max_skew)

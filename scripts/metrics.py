import json
import subprocess
import datetime

raw = subprocess.check_output(["kubectl", "get", "--raw", "/apis/metrics.k8s.io/v1beta1/pods"])
metrics = json.loads(raw)

output = []
timestamp = datetime.datetime.utcnow().isoformat() + "Z"

for pod in metrics["items"]:
    ns = pod["metadata"]["namespace"]
    pod_name = pod["metadata"]["name"]
    for container in pod["containers"]:
        output.append({
            "timestamp": timestamp,
            "namespace": ns,
            "pod": pod_name,
            "container": container["name"],
            "cpu": container["usage"]["cpu"],
            "memory": container["usage"]["memory"]
        })

with open("k8s_metrics1.json", "w") as f:
    for entry in output:
        f.write(json.dumps(entry) + "\n")

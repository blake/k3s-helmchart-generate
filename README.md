# k3s-helmchart-generate

[k3s](https://k3s.io) is a lightweight Kubernetes distribution from Rancher.
It ships with a [Helm controller](https://github.com/rancher/helm-controller)
which provides a simple way to manage Helm charts using Custom Resource
Definitions in Kubernetes. The documentation for using this CRD can be found in
the k3s documentation under
 [Using the helm CRD](https://rancher.com/docs/k3s/latest/en/configuration/#using-the-helm-crd).

This script creates HelmChart resource definitions for use with k3s. The command
line arguments closely resemble the behavior of `helm install` which allows
users to preserve their existing Helm chart installation workflow while
simplifying the process of generating the HelmChart CRDs for K3s.

## Requirements

* Python 3.5 or higher
* PyYAML 5.1 or higher

## Installation

First, clone the repository using `git`.

```shell
git clone https://github.com/blake/k3s-helmchart-generate.git
```

Change into the cloned directory.

```shell
cd k3s-helmchart-generate
```

### System-wide dependency installation

Execute the following commands to install `k3s-helmchart-generate`'s dependencies
into the system-wide Python library path, and make the program available for all
users of the system.

```shell
pip install --requirement requirements.txt
mv k3s-helmchart-generate/__main__.py /usr/local/bin/k3s-helmchart-generate
chmod +x /usr/local/bin/k3s-helmchart-generate
```

### Standalone application

You may also install the program as a self-contained, standalone application using
Python's [zipapp].

```shell
python -m pip install --requirement requirements.txt --target k3s-helmchart-generate
python -m zipapp k3s-helmchart-generate --compress --python="/usr/bin/env python3"
mv k3s-helmchart-generate.pyz /usr/local/bin/k3s-helmchart-generate
```

## Example usage

```shell
$ k3s-helmchart-generate stable/nginx-ingress --name nginx-ingress
---
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: nginx-ingress
  namespace: kube-system
spec:
  chart: stable/nginx-ingress

```

[zipapp]: https://docs.python.org/3/library/zipapp.html

# -*- mode: Python -*-

docker_build('shannon-tx-builder-image', '.')
k8s_yaml('kubernetes.yaml')
k8s_resource('shannon-tx-builder', port_forwards=8003)
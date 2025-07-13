# TL;DR

- `image-stream` allows you to tag and push a docker image from one place to another new repository.

# Quick start

```bash
python -m venv venv
source ./venv/bin/activate
python -m pip install -r requirements.txt
python stream.py <path to configuration>
```

# Configuration

- You can find a configuraiton example in [example-config.yaml](./example-config.yaml)

## Global configuration

- Some configurations, if unset, will be replaced with ones set by `Global Configuration` as default.

```yaml
image-stream:
    # Default registry to push new images. (Optional)
    registry: "docker.io"

    # Defualt repository to push new images. (Optional)
    repository: "lovely-docker-hub-account/my-repository"
    
    # Defualt image platform for new images. It will be set to argument '--platform'. (Optional)
    platform: "linux/amd64"
```

## Image

```yaml
image-stream:
  images:
    - name: "debian" # Customized image stream task name (Optional)
      source: "image"
      image:
        registry: "docker.io" # Image registry (Optional)
        repository: "ubuntu"  # Image repository

        # Either 'tag' or 'digest' must be set
        tag: "20.04"          # Image tag (Optional)
        # Image digest (Optional)
        digest: "sha256:8feb4d8ca5354def3d8fce243717141ce31e2c428701f6682bd2fafe15388214"
        
        # Image platform (Optional). If unset, use GlobalConfig.platfrom to ensure compatibility.
        platform: "linux/arm64"
      delivery:
        registry: "docker.io"   # New image registry (Optional)
        # New image repository
        reposiotry: "lovely-docker-hub-account/my-repository"
        tag: "ubuntu-latest"    # New image tag
        platform: "linux/arm64" # Image platform (Optional)
```

## Image from a Helm chart

- image-stream can tag and push new image whose source is defined in a Helm chart.
- To find image repository, you need to specify the path to `values.yaml` where it sets the source.

```yaml
image-stream:
  images:
    - name: "ingress-nginx" # Customized image stream task name (Optional)
      source: "helm"
      helm:
        # Helm chart repository
        repository: "https://kubernetes.github.io/ingress-nginx"
        # Name of the chart
        chart: "ingress-nginx"
        # Helm chart version (Optional)
        version: "4.12.4"
        # Image settings defined in `values.yaml`
        image:
          # Path to registry setting of source image
          registry: "global.image.registry"
          # Path to repository setting of source image
          repository: "controller.image.image"
          # Path to tag setting of source image
          tag: "controller.image.tag"
          # Path to digest setting of source image (Optional)
          digest: "controller.image.digest"
          # Path to platform of source image (Optional). If unset, use GlobalConfig.platform to ensure compatibility.
          platform: ""
      delivery:
        registry: "docker.io"   # New image registry (Optional)
        # New image repository
        reposiotry: "lovely-docker-hub-account/my-repository"
        tag: "ingress-nginx-latest" # New image tag
        platform: "linux/amd64" # Image platform (Optional)
```

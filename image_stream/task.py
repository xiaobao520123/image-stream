import os
import tempfile
import yaml
from glom import glom
from image_stream.global_config import GlobalConfig


class Source:
    image = "image"
    helm = "helm"


class Image:
    def __init__(self, registry, repository, tag, digest=None, platform=None):
        self.registry = registry if registry else ""
        self.repository = repository
        self.tag = tag
        self.digest = digest if digest else ""
        self.platform = platform


class HelmChartImageConfig:
    def __init__(self, registry, repository, tag, digest=None, platform=None):
        self.registry = registry
        self.repository = repository
        self.tag = tag
        self.digest = digest
        self.platform = platform


class HelmChart:
    def __init__(
        self,
        repository,
        chart,
        image_config,
        version=None,
    ):
        self.repository = repository
        self.chart = chart
        self.image_config = image_config
        self.version = version


class Task:
    def __init__(self, name, source, delivery):
        self.name = name
        self.source = source
        self.delivery = delivery

    def deliver(self):
        if isinstance(self.source, Image):
            self.deliver_docker_image()
        elif isinstance(self.source, HelmChart):
            self.deliver_docker_image_helm()
        else:
            raise ValueError(f"Unsupported source type: {type(self.source)}")

    def deliver_docker_image(self):
        # Make source image path
        source = self.source.repository
        if self.source.tag and len(self.source.tag) > 0:
            source = f"{self.source.repository}:{self.source.tag}"
        if self.source.digest and len(self.source.digest) > 0:
            source += f"@{self.source.digest}"
        if self.source.registry and len(self.source.registry) > 0:
            source = f"{self.source.registry}/{source}"

        # Make destination image path
        destination = self.delivery.repository
        if self.delivery.tag and len(self.delivery.tag) > 0:
            destination = f"{self.delivery.repository}:{self.delivery.tag}"
        if self.delivery.registry and len(self.delivery.registry) > 0:
            destination = f"{self.delivery.registry}/{destination}"

        self.pull_image(source, platform=self.source.platform)
        print("")
        self.tag_image(source, destination)
        print("")
        self.deliver_image(source, destination)

    def pull_image(self, image, platform=None):
        print(f"Pulling image {image}")

        cmd = f"docker pull {image}"
        if platform and len(platform) > 0:
            cmd += f" --platform {platform}"
        code = os.system(cmd)
        if code != 0:
            raise RuntimeError(f"Failed to pull image: {image}, exit code: {code}")

    def tag_image(self, source, destination):
        print(f"Tagging image {source} as {destination}")

        cmd = f"docker tag {source} {destination}"
        code = os.system(cmd)
        if code != 0:
            raise RuntimeError(
                f"Failed to tag image: {source} as {destination}, exit code: {code}"
            )

    def deliver_image(self, source, destination):
        print(f"Delivering image {source} → {destination}")

        cmd = f"docker push {destination}"
        if self.delivery.platform and len(self.delivery.platform) > 0:
            cmd += f" --platform {self.delivery.platform}"
        code = os.system(cmd)
        if code != 0:
            raise RuntimeError(
                f"Failed to deliver image: {source} to {destination}, exit code: {code}"
            )

    def deliver_docker_image_helm(self):
        helm = self.source
        image = self.find_helm_chart_image(helm)
        if not image:
            raise RuntimeError(
                f"Failed to find image for Helm chart {helm.repository}/{helm.chart}"
            )
        self.source = image
        print("")
        self.deliver_docker_image()

    def find_helm_chart_image(self, helm):
        repository = helm.repository
        chart = helm.chart
        version = helm.version
        image_config = helm.image_config

        print(f"Finding image for Helm chart {repository}/{chart}")

        # Pull Helm chart to local
        temp_dir = tempfile.mkdtemp()
        cmd = f"helm pull --repo {repository} {chart} --untar --untardir {temp_dir}"
        if version and len(version) > 0:
            cmd += f" --version {version}"
        code = os.system(cmd)
        if code != 0:
            raise RuntimeError(
                f"Failed to pull Helm chart: {repository}/{chart}, exit code: {code}"
            )

        # Find the image in the untarred chart directory
        chart_dir = os.path.join(temp_dir, chart)
        values_file = os.path.join(chart_dir, "values.yaml")
        if not os.path.exists(values_file):
            raise RuntimeError(f"Values file not found in chart directory: {chart_dir}")
        with open(values_file, "r") as f:
            values = yaml.safe_load(f)
        registry = self.expand_yaml_config(values, image_config.registry, default=None)
        repository = self.expand_yaml_config(values, image_config.repository)
        if not repository:
            raise RuntimeError(
                f"Repository not found in values.yaml for Helm chart: {chart_dir}"
            )
        tag = self.expand_yaml_config(values, image_config.tag)
        if not tag:
            raise RuntimeError(
                f"Tag not found in values.yaml for Helm chart: {chart_dir}"
            )
        digest = self.expand_yaml_config(values, image_config.digest, default=None)
        platform = self.expand_yaml_config(
            values, image_config.platform, default=GlobalConfig.platform
        )

        # Build image source
        image = Image(
            registry=registry,
            repository=repository,
            tag=tag,
            digest=digest,
            platform=platform,
        )

        return image

    def expand_yaml_config(self, values, path, default=None):
        if path and len(path) > 0:
            return glom(values, path, default=default)
        return default


class Delivery:
    def __init__(self, registry, repository, tag, platform=None):
        self.registry = registry
        self.repository = repository
        self.tag = tag
        self.platform = None

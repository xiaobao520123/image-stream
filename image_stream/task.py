import os


class Source:
    image = "image"
    helm = "helm"


class Image:
    def __init__(self, registry, repository, tag, digest=None, platform=None):
        self.registry = registry
        self.repository = repository
        self.tag = tag
        self.digest = digest
        self.platform = platform


class Task:
    def __init__(self, name, source, delivery):
        self.name = name
        self.source = source
        self.delivery = delivery

    def deliver(self):
        if isinstance(self.source, Image):
            self.deliver_docker_image()
        else:
            raise NotImplementedError("Only image source is implemented.")

    def deliver_docker_image(self):
        source = f"{self.source.registry}/{self.source.repository}:{self.source.tag}"
        if self.source.digest and len(self.source.digest) > 0:
            source += f"@{self.source.digest}"

        destination = (
            f"{self.delivery.registry}/{self.delivery.repository}:{self.delivery.tag}"
        )

        self.pull_image(source, platform=self.source.platform)
        print("")
        self.tag_image(source, destination)
        print("")
        self.deliver_image(source, destination)

    def pull_image(self, image, platform=None):
        print(f"Pulling image {image}")

        cmd = f"docker pull {image}"
        if platform:
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
        print(f"Delivering image {source} --> {destination}")

        cmd = f"docker push {destination}"
        code = os.system(cmd)
        if code != 0:
            raise RuntimeError(
                f"Failed to deliver image: {source} to {destination}, exit code: {code}"
            )


class Delivery:
    def __init__(self, registry, repository, tag):
        self.registry = registry
        self.repository = repository
        self.tag = tag

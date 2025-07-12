import argparse
from yaml import safe_load

from image_stream.global_config import GlobalConfig
from image_stream.task import *


def main():
    parser = argparse.ArgumentParser(
        description="image-stream allows you to tag and copy docker images to a specified registry."
    )
    parser.add_argument(
        "configuration",
        help="Path to the configuration file containing the registry and image details.",
    )
    args = parser.parse_args()

    print(args.configuration)

    task_config = load_config(args.configuration)
    tasks = build_tasks(task_config)
    deliver(tasks)


def load_config(file_path):
    with open(file_path, "r") as file:
        config = safe_load(file)

    config = config.get("image-stream")
    if config is None:
        raise ValueError(
            "Invalid configuration format. key: 'image-stream' is required."
        )

    GlobalConfig.registry = config.get("registry", None)
    GlobalConfig.repository = config.get("repository", None)
    return config.get("images", [])


def build_tasks(task_configs):
    tasks = []
    for task in task_configs:
        name = task.get("name")

        source_type = task.get("source")
        source = None
        if source_type == Source.image:
            source = task.get("image")
            source = Image(
                registry=source.get("registry", GlobalConfig.registry),
                repository=source.get("repository", GlobalConfig.repository),
                tag=source.get("tag"),
                digest=source.get("digest", None),
                platform=source.get("platform", None),
            )
        elif source_type == Source.helm:
            raise NotImplementedError("Helm source is not implemented yet.")
        else:
            raise ValueError(f"Invalid source: {source_type}")

        delivery = task.get("delivery")
        if not delivery:
            raise ValueError(f"{name} key 'delivery' not found.")

        delivery = Delivery(
            registry=delivery.get("registry", GlobalConfig.registry),
            repository=delivery.get("repository", GlobalConfig.repository),
            tag=delivery.get("tag"),
        )

        task = Task(
            name=name,
            source=source,
            delivery=delivery,
        )

        tasks.append(task)
    return tasks


def deliver(tasks):
    for task in tasks:
        print(f"Delivering task: {task.name}")
        task.deliver()
        print("")


if __name__ == "__main__":
    main()

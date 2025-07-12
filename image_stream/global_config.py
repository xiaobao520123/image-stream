class GlobalConfig:
    registry = None
    repository = None
    platform = None

    def print():
        if GlobalConfig.registry:
            print(f"(Global) registry={GlobalConfig.registry}")
        if GlobalConfig.repository:
            print(f"(Global) repository={GlobalConfig.repository}")
        if GlobalConfig.platform:
            print(f"(Global) platform={GlobalConfig.platform}")

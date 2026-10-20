import yaml
from pathlib import Path

OAS_FILE = "GP2/oas/api-oas.yaml"
CONFIG_FILE = "GP2/config/api-config.yaml"
OUTPUT_FILE = "GP2/generated/kong.yaml"


def route_name(api_name, path):
    return f"{api_name}-{path.strip('/').replace('/', '-')}"


def main():

    with open(OAS_FILE, "r") as f:
        oas = yaml.safe_load(f)

    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)

    api_name = config["api"]["name"]
    api_version = oas.get("info", {}).get("version", "unknown")

    backend = config["backend"]

    service = {
        "name": backend["host"],
        "host": backend["host"],
        "port": backend["port"],
        "protocol": backend["protocol"],
        "tags": [
            api_name,
            f"version-{api_version}"
        ],
        "routes": []
    }

    for path, path_item in oas.get("paths", {}).items():

        methods = []

        for method in path_item.keys():

            if method.lower() in [
                "get",
                "post",
                "put",
                "delete",
                "patch",
                "options",
                "head"
            ]:
                methods.append(method.upper())

        service["routes"].append(
            {
                "name": route_name(api_name, path),
                "paths": [path],
                "methods": methods,
                "strip_path": config["gateway"]["stripPath"],
                "tags": [
                    api_name,
                    f"version-{api_version}"
                ]
            }
        )

    kong_plugins = []

    for plugin in config.get("plugins", []):

        plugin_entry = {
            "name": plugin["name"],
            "tags": [
                api_name,
                f"version-{api_version}"
            ]
        }

        if "config" in plugin:
            plugin_entry["config"] = plugin["config"]

        kong_plugins.append(plugin_entry)

    kong_yaml = {
        "_format_version": "3.0",
        "services": [service],
        "plugins": kong_plugins
    }

    Path("GP2/generated").mkdir(
        parents=True,
        exist_ok=True
    )

    with open(OUTPUT_FILE, "w") as f:
        yaml.dump(
            kong_yaml,
            f,
            sort_keys=False
        )

    print(f"Kong config generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
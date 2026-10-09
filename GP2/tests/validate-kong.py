import yaml

with open("GP2/generated/kong.yaml") as f:
    kong = yaml.safe_load(f)

assert "_format_version" in kong
assert "services" in kong
assert "plugins" in kong

print("Kong configuration validation successful")
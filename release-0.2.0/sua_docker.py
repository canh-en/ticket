import os
import re

BASE = os.getcwd()

UPDATED = []
SKIPPED = []

for service in os.listdir(BASE):
    service_path = os.path.join(BASE, service)

    if not service.startswith("ts-") or not os.path.isdir(service_path):
        continue

    dockerfile_path = os.path.join(service_path, "Dockerfile")

    if not os.path.exists(dockerfile_path):
        SKIPPED.append(service)
        continue

    with open(dockerfile_path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # sửa ADD ./target/... → ADD ts-xxx/target/...
    new_content = re.sub(
        r'ADD\s+\./target/',
        f'ADD {service}/target/',
        content
    )

    # sửa COPY ./target/... nếu có
    new_content = re.sub(
        r'COPY\s+\./target/',
        f'COPY {service}/target/',
        new_content
    )

    if new_content != original:
        with open(dockerfile_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        UPDATED.append(service)
    else:
        SKIPPED.append(service)

# =========================
# RESULT
# =========================
print("=" * 60)
print("DONE FIX DOCKERFILES")
print("=" * 60)

print(f"\nUpdated ({len(UPDATED)}):")
for x in UPDATED:
    print("  ✔", x)

print(f"\nSkipped ({len(SKIPPED)}):")
for x in SKIPPED:
    print("  -", x)
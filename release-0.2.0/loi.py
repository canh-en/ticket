import os
import re

BASE = os.getcwd()

BAD_SERVICES = []
OK_SERVICES = []

for service in os.listdir(BASE):
    service_path = os.path.join(BASE, service)

    if not service.startswith("ts-") or not os.path.isdir(service_path):
        continue

    dockerfile = os.path.join(service_path, "Dockerfile")

    if not os.path.exists(dockerfile):
        continue

    with open(dockerfile, "r", encoding="utf-8") as f:
        content = f.read()

    # tìm COPY hoặc ADD dùng ./ (dễ lỗi khi build từ root)
    bad_patterns = re.findall(r'(ADD|COPY)\s+\./', content)

    if bad_patterns:
        BAD_SERVICES.append(service)
    else:
        OK_SERVICES.append(service)

# =========================
# OUTPUT
# =========================
print("=" * 60)
print("CHECK DOCKERFILE PATH (ROOT BUILD)")
print("=" * 60)

print(f"\n❌ Will FAIL ({len(BAD_SERVICES)}):")
for s in BAD_SERVICES:
    print("  -", s)

print(f"\n✅ Safe ({len(OK_SERVICES)}):")
for s in OK_SERVICES:
    print("  ✔", s)
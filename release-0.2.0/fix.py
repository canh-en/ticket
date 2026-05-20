import os
import re

BASE = os.getcwd()

UPDATED = []

for service in os.listdir(BASE):
    if not service.startswith("ts-"):
        continue

    dockerfile = os.path.join(BASE, service, "Dockerfile")

    if not os.path.exists(dockerfile):
        continue

    with open(dockerfile, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # =========================
    # 1. FIX "./" (python, generic)
    # =========================
    content = re.sub(
        r'(COPY|ADD)\s+\./',
        rf'\1 {service}/',
        content
    )

    # =========================
    # 2. FIX target (Java)
    # =========================
    content = re.sub(
        r'(COPY|ADD)\s+target/',
        rf'\1 {service}/target/',
        content
    )

    # =========================
    # 3. FIX UI (static + nginx)
    # =========================
    content = re.sub(
        r'COPY\s+(nginx\.conf)',
        rf'COPY {service}/\1',
        content
    )

    content = re.sub(
        r'COPY\s+(static)',
        rf'COPY {service}/\1',
        content
    )

    content = re.sub(
        r'COPY\s+(dist)',
        rf'COPY {service}/\1',
        content
    )

    # =========================
    # 4. FIX avatar kiểu ADD .
    # =========================
    content = re.sub(
        r'ADD\s+\.\s+/app/',
        rf'ADD {service}/ /app/',
        content
    )

    # =========================
    # 5. FIX requirements.txt (python)
    # =========================
    content = re.sub(
        r'COPY\s+(requirements\.txt)',
        rf'COPY {service}/\1',
        content
    )

    # =========================
    # SAVE nếu có thay đổi
    # =========================
    if content != original:
        with open(dockerfile, "w", encoding="utf-8") as f:
            f.write(content)

        UPDATED.append(service)
        print(f"✔ fixed {service}")

print("\n" + "="*50)
print(f"TOTAL FIXED: {len(UPDATED)} service(s)")
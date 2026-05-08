import os
import re

# Chạy file này ở thư mục cha chứa:
#   Augmented-TrainTicket/
#   release-0.2.0/

BASE_DIR = os.getcwd()
REPO = os.path.join(BASE_DIR, "release-0.2.0")

AGENT_REL_PATH = "/opentelemetry/opentelemetry-javaagent.jar"

UPDATED = []
SKIPPED = []

def patch_dockerfile(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # bỏ qua nếu đã patch rồi
    if "opentelemetry-javaagent.jar" in content:
        return False

    # chỉ patch image Java
    if "java" not in content.lower() and ".jar" not in content.lower():
        return False

    lines = content.splitlines()
    new_lines = []
    inserted = False

    for line in lines:
        new_lines.append(line)

        # chèn sau WORKDIR nếu có
        if (not inserted) and re.match(r"^\s*WORKDIR\s+", line, re.I):
            new_lines.append("")
            new_lines.append(
                "COPY opentelemetry-javaagent/opentelemetry-javaagent.jar "
                + AGENT_REL_PATH
            )
            new_lines.append(
                'ENV JAVA_TOOL_OPTIONS="-javaagent:/opentelemetry/opentelemetry-javaagent.jar"'
            )
            inserted = True

    # nếu không có WORKDIR thì chèn đầu file sau FROM
    if not inserted:
        newer = []
        done = False
        for line in new_lines:
            newer.append(line)
            if (not done) and re.match(r"^\s*FROM\s+", line, re.I):
                newer.append("")
                newer.append(
                    "COPY opentelemetry-javaagent/opentelemetry-javaagent.jar "
                    + AGENT_REL_PATH
                )
                newer.append(
                    'ENV JAVA_TOOL_OPTIONS="-javaagent:/opentelemetry/opentelemetry-javaagent.jar"'
                )
                done = True
        new_lines = newer

    content = "\n".join(new_lines)

    # nếu CMD java -jar thì thêm java tool options là đủ, không cần sửa CMD
    # giữ nguyên startup command

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    return False


for name in os.listdir(REPO):
    service_dir = os.path.join(REPO, name)

    if not os.path.isdir(service_dir):
        continue

    # bỏ qua folder agent
    if name == "opentelemetry-javaagent":
        continue

    # chỉ xử lý service ts-
    if not name.startswith("ts-"):
        continue

    dockerfile = os.path.join(service_dir, "Dockerfile")

    if not os.path.isfile(dockerfile):
        SKIPPED.append(name)
        continue

    try:
        changed = patch_dockerfile(dockerfile)
        if changed:
            UPDATED.append(name)
        else:
            SKIPPED.append(name)
    except Exception as e:
        SKIPPED.append(f"{name} (error: {e})")

print("=" * 60)
print("DONE PATCH DOCKERFILES")
print("=" * 60)

print(f"\nUpdated ({len(UPDATED)}):")
for x in UPDATED:
    print("  ✔", x)

print(f"\nSkipped ({len(SKIPPED)}):")
for x in SKIPPED:
    print("  -", x)
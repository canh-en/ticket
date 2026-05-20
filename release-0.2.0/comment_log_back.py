import os
import re

# Root repo hiện tại
ROOT_DIR = "."

# Pattern cần comment
PATTERN = re.compile(
    r'''<appender\s+name="OTEL"\s+class="io\.opentelemetry\.instrumentation\.logback\.v1_0\.OpenTelemetryAppender">\s*
\s*<appender-ref\s+ref="CONSOLE"\s*/>\s*
\s*</appender>''',
    re.MULTILINE
)

count = 0

for root, dirs, files in os.walk(ROOT_DIR):
    for file in files:
        if file == "logback.xml":
            filepath = os.path.join(root, file)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                match = PATTERN.search(content)

                if match:
                    original = match.group(0)

                    # Nếu chưa bị comment
                    if "<!--" not in original:
                        commented = f"<!--\n{original}\n-->"

                        new_content = content.replace(original, commented)

                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(new_content)

                        print(f"[UPDATED] {filepath}")
                        count += 1
                    else:
                        print(f"[SKIPPED - already commented] {filepath}")

            except Exception as e:
                print(f"[ERROR] {filepath}: {e}")

print(f"\nDone. Updated {count} file(s).")
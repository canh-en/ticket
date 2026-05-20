FROM eclipse-temurin:8-jre

COPY opentelemetry-javaagent/opentelemetry-javaagent.jar /opentelemetry/opentelemetry-javaagent.jar
ENV JAVA_TOOL_OPTIONS="-javaagent:/opentelemetry/opentelemetry-javaagent.jar"

RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

ADD ts-consign-price-service/target/ts-consign-price-service-1.0.jar /app/
CMD ["java", "-Xmx200m",  "-jar", "/app/ts-consign-price-service-1.0.jar"]

EXPOSE 16110
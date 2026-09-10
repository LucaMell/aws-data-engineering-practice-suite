FROM maven:3.9-eclipse-temurin-11 AS build
WORKDIR /src
COPY pom.xml .
COPY src ./src
RUN mvn -q -DskipTests package
FROM flink:1.18-java11
COPY --from=build /src/target/realtime-analytics-1.0.0.jar /opt/flink/usrlib/job.jar
CMD ["standalone-job","--job-classname","practice.RealtimeJob"]


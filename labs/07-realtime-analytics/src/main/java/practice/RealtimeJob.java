package practice;

import java.nio.charset.StandardCharsets;
import java.util.Properties;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.connectors.kinesis.FlinkKinesisConsumer;

public class RealtimeJob {
  public static void main(String[] args) throws Exception {
    String stream = System.getenv().getOrDefault("STREAM_NAME", "realtime-events-practice");
    String region = System.getenv().getOrDefault("AWS_REGION", "eu-west-1");
    Properties properties = new Properties();
    properties.setProperty("aws.region", region);
    properties.setProperty("flink.stream.initpos", "TRIM_HORIZON");
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    DataStream<String> events = env.addSource(new FlinkKinesisConsumer<>(stream, new SimpleStringSchema(), properties));
    events.map((MapFunction<String,String>) value -> value.trim()).name("normalize").print();
    // Practice checkpoint: replace print with the approved OpenSearch sink/connector and SigV4 auth.
    env.execute("realtime-analytics-practice");
  }
}


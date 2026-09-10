import pathlib
def test_job_reads_kinesis(): assert "FlinkKinesisConsumer" in (pathlib.Path(__file__).parent / "src/main/java/practice/RealtimeJob.java").read_text()

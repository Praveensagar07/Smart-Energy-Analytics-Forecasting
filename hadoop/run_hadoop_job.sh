#!/bin/bash
# ==============================================================================
# Hadoop MapReduce Job Submission Script (Hadoop Streaming)
# Smart Energy Consumption Analytics & Forecasting
# ==============================================================================

set -e

# Configuration
HADOOP_HOME=${HADOOP_HOME:-/usr/local/hadoop}
STREAMING_JAR=$(find "$HADOOP_HOME/share/hadoop/tools/lib" -name "hadoop-streaming-*.jar" | head -n 1)

if [ -z "$STREAMING_JAR" ]; then
    echo "[ERROR] Hadoop streaming jar not found in $HADOOP_HOME/share/hadoop/tools/lib"
    echo "        Please ensure HADOOP_HOME is set and Hadoop is properly installed."
    exit 1
fi

HDFS_INPUT="/smart-energy/raw/sample_household_power_consumption.txt"
HDFS_OUTPUT="/smart-energy/mapreduce/daily_consumption"
MAPPER_PATH="hadoop/mapper.py"
REDUCER_PATH="hadoop/reducer.py"

echo "=== Submitting Hadoop Streaming MapReduce Job ==="
echo "Input Path:    $HDFS_INPUT"
echo "Output Path:   $HDFS_OUTPUT"
echo "Streaming Jar: $STREAMING_JAR"

# Remove existing output directory on HDFS if present
hdfs dfs -rm -r -f "$HDFS_OUTPUT"

# Execute Hadoop Streaming MapReduce
hadoop jar "$STREAMING_JAR" \
    -D mapreduce.job.name="Smart Energy Daily Consumption Aggregator" \
    -D mapreduce.job.reduces=2 \
    -files "$MAPPER_PATH","$REDUCER_PATH" \
    -mapper "python3 mapper.py" \
    -reducer "python3 reducer.py" \
    -input "$HDFS_INPUT" \
    -output "$HDFS_OUTPUT"

echo "=== MapReduce Job Completed ==="
echo "Listing HDFS Output Directory:"
hdfs dfs -ls "$HDFS_OUTPUT"

echo "Displaying First 10 Results:"
hdfs dfs -cat "$HDFS_OUTPUT/part-*" | head -n 10

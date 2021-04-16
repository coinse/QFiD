#!/bin/bash
export JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF8
echo "Usage: ./generate_test.sh [project] [from_version] [to_version] [tool] [id] [time_budget] [seed]"
for i in $(seq $2 $3); do
  sh generate_test2.sh $1 $i $4 $5 $6 $7
done

PROJECT=$1
VERSION=$2
TOOL=$3
ID=$4
BUDGET=$5
BUGGY_TMP_DIR=/tmp/${PROJECT}-${VERSION}b
FIXED_TMP_DIR=/tmp/${PROJECT}-${VERSION}f
TEST_SUITE_FILE=$TEST_SUITE_DIR/$PROJECT/$TOOL/$ID/${PROJECT}-${VERSION}b-${TOOL}.${ID}.tar.bz2
TEST_SUITE_CONTENT=$TEST_SUITE_DIR/$PROJECT/$TOOL/$ID/${PROJECT}-${VERSION}b/

echo $PROJECT $VERSION

echo $BUGGY_TMP_DIR
if [ -d "$BUGGY_TMP_DIR" ]; then
  echo "$BUGGY_TMP_DIR exists"
else
  defects4j checkout -p ${PROJECT} -v ${VERSION}b -w $BUGGY_TMP_DIR
  if [ -d "$BUGGY_TMP_DIR" ]; then
    echo "Checkout succeed!"
  else
    exit 1
  fi
fi
cd $BUGGY_TMP_DIR

FAILING_TESTS=$BUGGY_TMP_DIR/tests.trigger
echo $(pwd)
defects4j export -p tests.trigger -o $FAILING_TESTS
echo "" >> $FAILING_TESTS

COV_DIR=$BUGGY_TMP_DIR/coverages
if [ -d "$COV_DIR" ]; then
  echo "$COV_DIR exists"
else
  mkdir $COV_DIR
fi

CLASSES_FILE=$BUGGY_TMP_DIR/classes.trigger
if [ -f "$CLASSES_FILE" ]; then
  rm $CLASSES_FILE
fi

while IFS= read -r tc
do
  cd $BUGGY_TMP_DIR
  COV_FILE="$COV_DIR/$tc.xml"
  echo $COV_FILE
  if [ -f "$COV_FILE" ]; then
    echo "$COV_FILE exists"
  else
    defects4j coverage -t "$tc"
    mv coverage.xml "$COV_DIR/$tc.xml"
  fi
  cd /home/d4j_expr && python3.6 get_covered_classes.py $COV_FILE -o $CLASSES_FILE
done < $FAILING_TESTS

cd $BUGGY_TMP_DIR
sort -u $CLASSES_FILE > $CLASSES_FILE.unique

echo "\n**************CLASSES***************"
cat $CLASSES_FILE.unique
echo "************************************\n"

if [ -f "$TEST_SUITE_FILE" ]; then
  echo "test suite exists"
else
  cd $BUGGY_TMP_DIR
  gen_tests.pl -g $TOOL -p ${PROJECT} -v ${VERSION}b -n $ID -o $TEST_SUITE_DIR -b $BUDGET -c $CLASSES_FILE.unique
  cp /home/d4j_expr/evosuite.config /home/d4j_expr/configs/evosuite.config.$ID.$BUDGET
  mv /home/evosuite-report/statistics.csv /home/evosuite-report/statistics.${PROJECT}.${VERSION}b.${TOOL}.${ID}.csv
fi

if [ -d "$TEST_SUITE_CONTENT" ]; then
  echo "already extracted"
else
  cd /home/d4j_expr/shell_scripts && sh extract_test.sh $PROJECT $VERSION $TOOL $ID $TEST_SUITE_DIR
fi


if [ -d "$FIXED_TMP_DIR" ]; then
  echo "$FIXED_TMP_DIR exists"
else
  defects4j checkout -p ${PROJECT} -v ${VERSION}f -w $FIXED_TMP_DIR
  if [ -d "$FIXED_TMP_DIR" ]; then
    echo "Checkout succeed!"
  else
    exit 1
  fi
fi

cd $FIXED_TMP_DIR
defects4j test -s $TEST_SUITE_FILE
mv failing_tests failing_tests.${TOOL}.${ID}

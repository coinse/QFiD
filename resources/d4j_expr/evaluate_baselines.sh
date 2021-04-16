for var in "$@"
do
  # python3.6 evaluate.py -i $var -s Prox
  python3.6 evaluate.py -i $var -s S3
  python3.6 evaluate.py -i $var -s S3 -n 0.1
  python3.6 evaluate.py -i $var -s S3 -n 0.3
done

for var in "$@"
do
  python3.6 evaluate.py -i $var -s S3 -n 0.5
  python3.6 evaluate.py -i $var -s S3 -n 0.7
  python3.6 evaluate.py -i $var -s S3 -n 0.9
done

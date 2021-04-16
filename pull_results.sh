docker cp $1:/root/d4j_expr/results/localisation/$2 results/$3/
cd results/$3/ && tar -czvf $2.tar.gz $2

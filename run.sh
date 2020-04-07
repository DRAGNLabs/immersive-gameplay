destination_file=results/while-you-were-gone.txt
for version in 1 2
do
  for dataset in cod warcraft handwritten generated
  do
    for weight in True False
    do
      date >> $destination_file
      python3 run_test_cases.py $version $dataset $weight >> $destination_file
    done
  done
done
echo "done!" >> $destination_file
date >> $destination_file

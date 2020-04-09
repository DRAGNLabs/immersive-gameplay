destination_file=out.txt
for version in 1 2
do
  for dataset in cod warcraft handwritten generated
  do
    date >> $destination_file
    python3 run_test_cases.py $version $dataset >> $destination_file
  done
done
echo "done!" >> $destination_file

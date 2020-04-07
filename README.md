# Immersive Gameplay Test Driver

## Contents

### run_test_cases.py
This is the main python script that runs the test cases. You can set the hyperparameters you want in the 'Hyperparameters' section 
(lines 10-15) or you can provide them as command line arguments. Usage is `python3 run_test_cases.py [infersent_version] 
[dataset] [use_weighting] `. `infersent_version` should be 1 or 2, `dataset` should be any group of test cases that has
a file for test cases and guidance data, and `use_weighting` should be either `True` or `False`.

The way I've written it, running run_test_cases.py will use all 4 command extraction methods (simple distance, translation,
PC distance, and nearest neighbor) and all 7 distance metrics (listed starting on line 53). This means it will output 4
groups of 7 pairs of numbers. Each group is an extraction method and each pair of numbers is the number of verbs and 
objects the model guessed correctly using a specific distance metric. I recommend changing this so it prints out an 
accuracy score for each command extraction method, each distance metric, and overall. It should also print the highest 
total accuracy achieved by any combination of distance metric and command extraction method (the highest pair of numbers).


### run.sh
This is a bash script that runs run_test_cases.py repeatedly and prints the results to `results/while-you-were-gone.txt`.
This is really helpful if you have a lot of long tests you want to run overnight or something like that. It uses three four
loops to let you pick which hyperparameters you want to test with. The outermost loop determines the versions of InferSent
you will use, the middle loop determines which test cases you're using, and the inner loop determines if you want to use 
weighting or not. Let me know if you need help adjusting it.


### data/
This folder has all the test cases and guidance data that `run_test_cases.py` uses. For each new test environment you make,
you should add a file called {test_environment_name}.csv to to `data/guidance_data/` and to `data/test_cases/`. The first
is the examples that your model will have access to when making predictions, and the second is what it is trying to make
predictions on. The .csv files should have one test case per line, where the test case format is {verb},{object},{utterance}.
Verbs and objects should be all lower case. It is possible to have verbs and objects that are multiple words (like 'Go to'), 
but that brings up some additional complications that you may not want to bother with. Objects can be left blank if there 
isn't an object for a specific utterance (for example, one test case could be "flee,,Get out of here"). Utterances should
not have any commas in them, and I think it works better if they don't have any punctuation at all other than apostrophes.

The `data/` folder also has a file called `test_case_generator.py` that you can use to make your own test cases if you want.
The idea is that you list out some verbs and objects, then give synonyms for each of those verbs and objects. The script 
then concatenates all possible combinations of the synonyms you provided to make a huge test set really quickly. It's not 
as high quality as test sets you'd find 'in the wild', but it can be a good starting place.

### industrial_comparisons/
This folder has the code you'll need for running your test cases through Amazon Alexa or Google Voice Assistant to see how
our model compares to theirs. You have to do a lot of setup on Google's and Amazon's websites before this code can do anything,
and it's more than I can explain here. Let me know if you want to use this part of the code base and I can walk you through
how it works. Also, the `industrial_comparisons/google_comparison/` folder has some private keys in it, so please don't
put that folder on github or anything like that :)

### resources/
This folder has a bunch of libraries and scripts Dr. Fulda sent me to make all the behind-the-scenes stuff work. You shouldn't
need to change or think about anything in there except for `weights.csv` if you want to. 

### results/
I was using this for a bunch of stuff, but all that I left was the `while-you-were-gone.txt` file, which is where the output
of `run.sh` goes.
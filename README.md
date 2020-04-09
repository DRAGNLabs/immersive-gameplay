# Immersive Gameplay Test Driver
This is the code that tests the methods described in the forthcoming paper Immersive Gameplay via Improved Natural Language Understanding. Before you can run it you will need word and sentence embedding models for GloVe, FastText, and InferSent. Instructions for downloading all three can be found at https://modelzoo.co/model/infersent

I am happy to answer any questions. You may contact me at bandrus5@byu.edu

## Contents

### run_test_cases.py
This is the main python script that runs the test cases. You can set the hyperparameters you want in the 'Hyperparameters' section
(lines 10-15) or you can provide them as command line arguments. Usage is `python3 run_test_cases.py [infersent_version]
[dataset]`. `infersent_version` should be 1 or 2, `dataset` should be any group of test cases that has
a file for test cases and guidance data. Command extraction methods and distance metrics can be set by commenting out the appropriate lines in the code.

The way I've written it, running run_test_cases.py will use all 4 command extraction methods (simple distance, translation, nearest neighbor, and
PC distance) and all 7 distance metrics (listed starting on line 53). This means it will output 4
groups of 7 pairs of numbers. Each group is an extraction method and each pair of numbers is the number of verbs and
objects the model guessed correctly using a specific distance metric.

### run.sh
This is a bash script that runs run_test_cases.py repeatedly and prints the results to `out.txt`.
This is really helpful if you have a lot of long tests you want to run overnight or something like that.


### data/
This folder has all the test cases and guidance data that `run_test_cases.py` uses. For each new test environment you make,
you should add a file called {test_environment_name}.csv to to `data/guidance_data/` and to `data/test_cases/`. The first
is the examples that your model will have access to when making predictions, and the second is what it is trying to make
predictions on. The .csv files should have one test case per line, where the test case format is {verb},{object},{utterance}.
Verbs and objects should be all lower case. It is possible to have verbs and objects that are multiple words (like 'Go to'),
but that brings up some additional complications that you may not want to bother with. Objects can be left blank if there
isn't an object for a specific utterance (for example, one test case could be "flee,,Get out of here"). Utterances should
not have any commas in them.


### resources/
This folder has the external libraries and scripts needed to make my algorithms work.

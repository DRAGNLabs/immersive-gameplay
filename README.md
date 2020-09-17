# Immersive Gameplay
This is the code that tests the methods described in the paper [Immersive Gameplay via Improved Natural Language Understanding](https://dl.acm.org/doi/10.1145/3402942.3403024). Before you can run it you will need word and sentence embedding models for GloVe, FastText, and InferSent. Instructions for downloading all three can be found at https://modelzoo.co/model/infersent

I am happy to answer any questions. You may contact me at bandrus5@byu.edu

## Contents

### run_test_cases.py
This is the main python script that runs the test cases. You can set the hyperparameters you want in the 'Hyperparameters' section of this file (lines 10-15) or you can provide them as command line arguments. Usage is `python3 run_test_cases.py [infersent_version]
[dataset]`. `infersent_version` should be 1 or 2, `dataset` should be any group of test cases that has a file in data/test_cases/ and data/guidance_data/. Command extraction methods and distance metrics can be set by commenting out the appropriate lines in the code.

The way I've written it, running run_test_cases.py will use all 4 command extraction methods (simple distance, translation, nearest neighbor, and PC distance) and all 7 distance metrics (listed starting on line 53). It outputs the number of correct verbs and the number of correct objects identified for each combination of extraction method and distance metric.

### run.sh
This is a bash script that runs run_test_cases.py repeatedly and prints the results to `out.txt`.

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

## Descriptions of Test Environments
data/ has 4 test environments, which are sets of test cases and guidance data.

### Warcraft
This test environment came from NPC dialog in the game Warcraft III, as found on wowwiki.fandom.com. We skimmed through lists of lines of NPC dialog to find common underlying themes and intents that could be used as verbs and objects. Once a domain of verbs and objects was defined, we went through dialog lists again and copied lines that fit with one of our defined commands. The valid verbs in the Warcraft test environment are {Give, Attack, Submit to, Flee} and the valid objects are {orders, information, enemies, me (referring to the player), NULL}. In this test environment not all combinations of verb and object are sensible. For example, there are no test or guidance utterances that are labelled as ‘Attack information’. However, the model was still allowed to predict non-sensible combinations when using any of the command extraction methods other than Nearest Neighbor. This test set has 17 cases in the guidance data and 113 test cases.

### Handwritten 1
This test environment was handwritten by the authors of this paper to reflect the kinds of utterances a player might make while playing a sci-fi first person shooter like Halo. The valid verbs in the Handwritten 1 test environment are {Attack, Evade, Retreat, Follow, Protect, Enter, Exit, Go} and the valid objects are {enemies, spaceship, turret, me (referring to the player), vehicle, up, down, building, tunnels, NULL}. This test set has 20 cases in the guidance data and 25 test cases.

### Handwritten 2
This test environment was also handwritten by the authors of the paper, but it was generated in a more structured manner than Handwritten 1. We created parts of sentences that were synonymous with each of our desired verbs and objects, then concatenated parts of sentences to create a much larger test set, albeit a more formulaic one. For example, we combined “Shoot at ” and “that UFO” to get an example utterance that was labelled as ‘Attack spaceship’. The valid verbs in the Handwritten 2 test environment are {Attack, Evade, Follow, Protect, Enter, Exit, Go} and the valid objects are {enemies, spaceship, turret, me (referring to the player), vehicle, building, tunnels}. This test set has 20 cases in the guidance data and 480 test cases.

### Call of Duty
This test environment was the only one generated from real user input. We created a digital survey that showed screenshots from the game Call of Duty and asked responders what they would say to get a teammate to accomplish a specific objective. For example, one survey question was “Given the image below, what is something you might say to get your teammate to shoot at the circled people?”. We distributed the test to university students, the friends and family of our lab members, and several online communities including on Reddit and SurveyCircle. We ended up with nearly 100 unique survey participants. Once responses were collected, we removed any responses that were either 1) nonsensical answers from trolls or 2) only gave positional information (e.g. one answer was simply “12 ’o’ clock”). The valid verbs in the Call of Duty test environment are {Flee, Protect, Follow, Attack, Enter, Exit} and the valid objects are {ally, enemies, building, aircraft, vehicle, NULL}. This test set has 32 cases in the guidance data and 400 test cases.


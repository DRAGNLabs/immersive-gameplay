

objects = [('tunnels', ['those caves', 'that tunnel', 'that hallway', 'that entrance']),
           ('building', ['that hospital', 'the castle', 'that guard post', 'the second tower', 'those houses']),
           ('turret', ['that missile turret']),
           ('vehicle', ['that car', 'the helicopter', 'that warthog', 'those jeeps']),
           ('spaceship', ['that plane', 'those ships', 'that UFO', 'those bombers']),
           ('enemies', ['those hostiles', 'that gunner', 'the zombie', 'the monster']),
           ('me', ['my position', 'me'])]

verbs = [('go', ['run over to', 'go to', 'walk to']),
         ('attack', ['shoot at', 'try to kill', 'strike', 'target', 'take down']),
         ('evade', ['get away from', 'look out for', 'dodge']),
         ('protect', ['defend', 'guard', 'shield']),
         ('follow', ['keep up with', 'go with', 'trail', 'track']),
         ('enter', ['get in']),
         ('exit', ['get out of'])]


with open('generated_test_cases.csv', 'w') as file:
    print('verb,object,sentence', file=file)
    for object, o_varients in objects:
        for verb, v_varients in verbs:
            for o_varient in o_varients:
                for v_varient in v_varients:
                    print(verb, object, v_varient + ' ' + o_varient, sep=',', file=file)

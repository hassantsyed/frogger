# README

## Setup:
* Python 2
* Ubuntu 18
* i7 CPU
* 16 gb RAM

##### Packages:
* argparse
* cPickle
* random

## How to run:
#### Loading Agent:
```
python2 Qagent.py -l <pickle_file>
```
You should run:
```
python2 Qagent.py -l finalState.pickle
```

For more information on how to run:
```
python puzzlesolver.py -h
```

#### Data Files:
The data files are stored in binary in the pickle format. I chose to use cPickle to load and save the files quickly.


## Performance:
#### Average Success:
On average, two frogs will routinely make it home, sometimes 3, and infrequently 4.
The average reward is approximately -12.
* Note: For every step the frog takes, I subtract .1 from the reward to disincentivize doing nothing or moving back and forth, and to incentivize going home faster. Because of this the average reward for my frog is lower.

The agent works in the full environment.

## Learning Framework

#### Parameters:
* Gamma: .9
    * This was chosen somewhat arbitrarily. I noticed that it worked reasonably well, so I let it be. I think this makes sense since future rewards should be valued less than immediate ones, but frogger requires multiple steps to attain the reward so future rewards should be valued.
* Alpha: 
    * Originally, I had set this to a static value. I noticed that this didn't produce good results. Convergence of states to their real value was slow and innaccurate. I changes this to be 1 / N(state, action). I found this rolling average to work much better in terms of convergence.
* Exploration: 
    * I artificially inflated the values in my qTable of states based on how frequently I had visited them using: CONST / N(state, action) and adding this to their current state value. I selected CONST to be equal to 1. I did some tuning here and found that higher values required too many visits to get a reasonable value for a state. In hindsight, I think I would make this even lower, maybe .75 or .5.
    * I also noticed that without a step cost of -.1, my agent would opt to hide in the corner of the game where it couldn't die.
* I also made the decision to ignore doing nothing as an acceptable move. The agent must make a directional move.


#### State Representation:

The state representation that I settled on was a 5x3 matrix with the frog centered.
* 0: road
* 1: car
* 2: river object
* 3: home
* 4: border

Each cell in the matrix represents a square of pixels 24x24. If that group of pixels contains any of the items above that cell would be labeled as such.  
Here is an example state representation.

|  4 |  4 |  3 | 4  | 4  |
|:-:|:-:|:-:|:-:|:-:|
|  2 |  2 |  F | 2  | 2  |
| 0  | 0  | 0  | 1  | 1  |

This makes the frog state two jumps to the right and left and one jump up or down.

I had one other state representation before arriving at this one. Originally, I had a 3x3 matrix with the frog centered. I also did not encode the border. I found this to be lacking as the frog was unable to learn very well in the river portion of the game. The frog would not navigate down the lengths of the logs or turtles. It also had no notion of the border coming up, so it would frequently die going out of bounds.

With my updated representation, the frog can navigate the cars and river with greater precision due to the added granularity afforded by the expanded matrix. It also has learned that borders mean death and will try to navigate away from them.

#### Training:
I trained the frog overnight to get my current performance. I think if the frog trained even longer it would be better. 

If I had more time to work on this project, I would make the action picked be random for actions with tied values. This comes up often in the beginning of the training and exploration phases since all new states are generated with the same initial value of 0. Instead, I try to find the max, returning the first instance of the max if there is a tie.

I also would have liked to tune my exploration and gamma parameter more. I chose .9 for gamma somewhat arbitrarily since it seemed to work well. In terms of exploration, I would like to make it explore more efficiently. I find that my model needs to visit states too often to get a reasonable value for them, so it will go to states that it dies in more than I would like it to. I could fix this by tuning my exploration values.

I would also encode the crocodiles and flies that sometimes appear in the home rows. I think this would improve performace since my frog doesn't seem to realize it can wait in front of the home with a crocodile before going there. However, this would require retraining.

I would also allow for the no move action. I think this could be useful in a more trained model, but in the training sets I did where I was trying to iterate quickly, the no action move made learning slow.

Eventually I would like to incorporate a TD-lambda framework.

## Discussed With:
Alessio Mazzone: General ideas about the project, state representation (what was tried)

## Additional References:
1. https://docs.python.org/2/library/pickle.html
    * pickle documentation
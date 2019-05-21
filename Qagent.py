from ple import PLE
import frogger_new
import numpy as np
from pygame.constants import K_w,K_a,K_F15,K_d,K_s
import pygame
import cPickle
from random import randint
import argparse

CONST = 1
actions = [119,100,97, 115, None]
leftOffset = 160
rightOffset = 608
count = 0

class State():
    def __init__(self, obs):
        self.x = obs['frog_x']
        self.y = obs['frog_y']
        self.matrix =  [(-48,24), (-24,24), (0, 24), (24,24), (48,24), (-48, 0), (-24,0), (0, 0), (24,0), (48, 0), (-48, -24), (-24,-24), (0,-24), (24,-24), (48, -24)]
        self.matrix = self.carCheck(obs)
        #print(self.matrix[0:5])
        #print(self.matrix[5:10])
        #print(self.matrix[10:15])
        #print("_________________")

    def carCheck(self, obs):
        matrix = self.matrix

        for i in range(len(matrix)):
            matrix[i] = self.checkGame(self.x + matrix[i][0], self.y+matrix[i][1], obs, i)

        return matrix

    def checkGame(self, top, left, obs, index):
        r = pygame.Rect(top, left, 24, 24)
            #print("river mode")
        for i in range(len(obs['homeR'])):
            if obs['homeR'][i].colliderect(r) and obs['homes'][i] == 0:
                return 3
        for car in obs['cars']:
            if car.colliderect(r):
                return 1
        if index % 5 == 0 or index == 4 or index == 9 or index == 14:
            if top < 0 or top > 416:
                return 4
        for rivs in obs['rivers']:
            if rivs.colliderect(r):
                return 2
        
        return 0

    def __hash__(self):
        #return hash((self.x, self.y, tuple(self.matrix)))
        return hash(tuple(self.matrix))

    def __eq__(self, other):
        if not self.x == other.x or not self.y == other.y:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

class RLAgent():
    def __init__(self, alpha, gamma, actions, qTable = None, N = None):
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        #state & action maps to current value,
        if not qTable:
            self.qTable = {}
        else:
            self.qTable = qTable
        #stat & action maps to amount of times seen
        if not qTable:
            self.N = {}
        else:
            self.N = N

    def genActions(self, state):
        actions = []
        for act in self.actions:
            if act is None:
                continue
            stateAction = (state, act)
            if not stateAction in self.qTable:
                self.qTable[stateAction] = 0
                self.N[stateAction] = 1
            actions.append([act, state])

        #print(actions)
        return actions

    def pickAction(self, state):
        global count
        count += 1
        acts = self.genActions(state)
        sPrime = None
        aPrime = None
        val = float("-inf")
        #if count % 1000 == 0:
        #    ran = True
        #else:
        ran = False
        if ran:
            i = randint(0, len(acts) -1)
            act = acts[i]
            val = self.qTable[(act[1], act[0])] + (CONST / float(self.N[(act[1], act[0])]))
            aPrime = act[0]
            return aPrime, val
        for act in acts:
            #need to add eploration here
            if self.qTable[(act[1], act[0])] > val:
                #print (self.qTable[(act[1], act[0])] + (CONST / float(self.N[(act[1], act[0])])))
                val = self.qTable[(act[1], act[0])] + (CONST / float(self.N[(act[1], act[0])]))
                sPrime = act[1]
                aPrime = act[0]
        return aPrime, val


    def updateQ(self, state, nextState, action, reward):
        oldQ = self.qTable[(state, action)]
        nextVal = self.pickAction(nextState)[1]
        modifier = (1/float(self.N[(state, action)])) * (reward + self.gamma * nextVal - oldQ)
        self.qTable[(state, action)] = oldQ + modifier
        self.N[(state, action)] += 1
        #print(len(self.qTable))
        #print(self.qTable)
        #print(self.N)

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--load", help = "file to load from")
parser.add_argument("-s", "--save", help = "file to save to")
args = parser.parse_args()
if args.load:
    print(args.load)
    qTable = open(args.load, "rb")
    pre, post = args.load.split(".")
    pre += "N"
    nFile = pre+"."+post
    N = open(nFile, "rb")
    agent = RLAgent(.3, .9, actions, cPickle.load(qTable), cPickle.load(N))
    print("loaded")
else:
    agent = RLAgent(.3, .9, actions)

game = frogger_new.Frogger()
fps = 30
p = PLE(game, fps=fps,force_fps=False)
reward = 0.0

p.init()
count = 0
tr = 0
try:
    while True:
        count += 1
        if p.game_over():
            #print("{} REWARD".format(tr))
            tr = 0
            p.reset_game()

        obs = game.getGameState()
        #print obs
        cur = State(obs)
        action = agent.pickAction(cur)[0]
        #action = None
        reward = p.act(action)
        newState = State(obs)

        #disincentivizing no move
        #if cur == newState:
        reward -= .1
        tr += reward
        agent.updateQ(cur, newState, action, reward)
        #break
except KeyboardInterrupt:
    if args.save:
        qTable = open(args.save, "wb")
        cPickle.dump(agent.qTable, qTable)
        qTable.close()
        pre, post = args.save.split(".")
        pre += "N"
        nFile = pre+"."+post
        N = open(nFile, "wb")
        cPickle.dump(agent.N, N)
        N.close()
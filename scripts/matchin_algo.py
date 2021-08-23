import pandas as pd
import numpy as np
from ast import literal_eval
import os, sys
import random
from tqdm import tqdm
import time


class MatchingWords():
    """A class for the pool from which we will subsample data
    Note: There will be an English and a French pool"""

    def __init__(self, w_df, nw_df, log_every=10):
        self.words = w_df

        self.pool_nw = nw_df.reset_index().rename(columns={'index': 'pool_index'})
        self.match_nw = pd.DataFrame(columns=self.pool_nw.columns)
        self.log_every  = log_every

        self.rand_init_nw()

        self.prec_loss = self.freq_loss()
        self.loss = None

    def rand_init_nw(self):
        "Randomly initialises  non words with the words df. - based on syllable structure"

        for index, row in self.words.iterrows():
            if len(self.pool_nw[self.pool_nw["structure"] == row.structure]) > 0:
                n = self.pool_nw[self.pool_nw["structure"] == row.structure].sample()
                self.match_nw.loc[index] = n.values[0]
                self.pool_nw.drop(n.index, inplace=True)
            else:
                self.match_nw.loc[index] = pd.Series(dtype='object')

        # remove rows which couldn't match a structure as not enough in pool
        na_mask = self.match_nw['pool_index'].notna()
        self.match_nw = self.match_nw[na_mask].reset_index(drop=True)
        self.words = self.words[na_mask].reset_index(drop=True)

    def make_move(self):
        #ensure you keep the match index as paired"

        no_structure = True
        while no_structure: #ensure that there is a posible structure in the pool
            row_frommatch = self.match_nw.dropna().sample(1) #only those who have one.
            structure = row_frommatch['structure'].values[0] #get the same structure
            if len(self.pool_nw[self.pool_nw["structure"] == structure]) > 0:
                no_structure = False

        row_frompool = self.pool_nw[self.pool_nw["structure"] == structure].sample(1)


        self.pool_nw = self.pool_nw.drop(row_frompool.index)
        self.match_nw = self.match_nw.drop(row_frommatch.index)
        self.match_nw.loc[row_frommatch.index[0]] = row_frompool.values[0]
        self.pool_nw = pd.concat([row_frommatch, self.pool_nw], ignore_index=True)
        made_move = [row_frommatch, row_frompool]
        return made_move

    def revert_move(self, made_move):
        row_frommatch = made_move[0]
        row_frompool = made_move[1]

        self.pool_nw = pd.concat([row_frompool, self.pool_nw], ignore_index=True)
        self.match_nw.loc[row_frommatch.index[0]] = row_frommatch.values[0]

        self.pool_nw.drop(self.pool_nw.loc[self.pool_nw['pool_index'] == row_frommatch['pool_index'].values[0]].index, inplace=True)
        self.match_nw.drop(self.match_nw.loc[self.match_nw['pool_index'] == row_frompool['pool_index'].values[0]].index, inplace=True)



    @staticmethod
    def euclidean_distance(p, q):
        size = len(p) if hasattr(p, '__len__') else 1
        return np.linalg.norm(p-q) / size # ok to just use euclidena distance as our sizes are set?

    @staticmethod
    def kl_divergence(p, q):
        return np.sum(np.where(p != 0, p * np.log(p / q), 0))


    def freq_loss(self):
        loss = self.euclidean_distance(self.match_nw["count"], self.words["count"])
        #return loss/self.nb_spkr_norm #what is this?
        return loss

    def run_sim_annealing(self, n_iter):
        nb_accepted_moves = 0
        # Should implement a threshold based stop rule
        for iter in tqdm(range(n_iter)):
            # Make a move
            made_move = self.make_move()

            # Compute loss and decide if move should be revert or not
            curr_loss, loss_details = self.loss()
            if curr_loss > self.prec_loss:
                # We revert move, prec_loss is not updated
                self.revert_move(made_move)
            else:
                # We keep move, prec_loss becomes curr_loss
                self.prec_loss = curr_loss
                nb_accepted_moves += 1

            if nb_accepted_moves % self.log_every == 0:
                #self.write_logs(loss_details, iter, nb_accepted_moves)
                #self.write_logs(loss, iter, nb_accepted_moves)
                print(iter, loss)


        return self.loss


import numpy as np
import pandas as pd
import time
import pickle
import matplotlib.pyplot as plt

class QLearningTable:
    def __init__(self, actions, Text, Text_Table, use_new_table, epsilon, learning_rate=0.1, reward_decay=0.99):
        self.Q_table_mean = []
        self.steps_count = []
        self.list = []
        self.count = 0
        self.steps = 0
        self.actions = actions  # a list
        self.lr = learning_rate
        self.gamma = reward_decay
        #use_new_table = False
        if use_new_table:
            print("Use New Table")
            self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)
            self.epsilon = epsilon
        else:
            self.Text = Text
            #self.Text = "Q_Table_QTSim_2115_DbD_day6_to_day7"
            print (self.Text)
            file2 = open('Q_Tables/Q_Table_' + str(Text_Table) + '.pkl', 'rb')
            print("Printing Q-Table: ")
            self.q_table = pickle.load(file2)
            file2.close()
            print (self.q_table)
            time.sleep(2)
            self.epsilon = epsilon

    def choose_action(self, observation, Text):
        self.check_state_exist(observation, Text)
        # action selection
        if np.random.uniform() < self.epsilon: # choose best action
            state_action = self.q_table.loc[observation, :]
            state_action = state_action.reindex(np.random.permutation(state_action.index))     # some actions have same value
            action = state_action.idxmax()
        else: # choose random action
            action = np.random.choice(self.actions)
            #print ("Random Action Selected")
        return action

    def learn(self, s, a, r, s_, Text, episode, epsi_steps):
        self.check_state_exist(s, Text)
        self.check_state_exist(s_, Text)
        q_predict = self.q_table.loc[s, a]
        if s_ != 'terminal':
            q_target = r + self.gamma * self.q_table.loc[s_, :].max()  # next state is not terminal
        else:
            q_target = r  # next state is terminal
        self.q_table.loc[s, a] += self.lr * (q_target - q_predict)  # update

        if episode not in self.list:
            self.epsilon += epsi_steps
            self.list.append(episode)
            #print (self.list)
            #time.sleep(2)
        if self.epsilon >= 1:
            self.epsilon = 1

        return self.epsilon

    def check_state_exist(self, state, Text):
        if state not in self.q_table.index:
            # append new state to q table
            print ("New State: " + str(state))
            self.q_table = self.q_table.append(
                pd.Series(
                    [0]*len(self.actions),
                    index=self.q_table.columns,
                    name=state,
                )
            )

    def save(self, episode, Text):
        #row, column = self.q_table.shape
        self.steps = 1
        self.count += 1
        self.Q_table_mean.append(np.mean(self.q_table))
        self.steps_count.append(episode)

        '''
        fig, ax = plt.subplots(1)
        plt.plot(self.steps_count, self.Q_table_mean, 'r', label = 'Q function')
        ax.tick_params(axis='both', which='major', labelsize=10)
        plt.title('Q function mean' + str(Text), fontsize=15)
        plt.ylabel('Q predict', fontsize=15)
        plt.xlabel('steps', fontsize=20)
        ax.grid(True)
        fig.savefig('Saved_Data/Convergence_' + str(Text) + '.png', bbox_inches='tight')
        #plt.show()
        plt.close(fig)
        #with open('Saved_Data/' + Text + '.pkl', 'w') as f:  # Python 3: open(..., 'wb')
        #    pickle.dump([self.steps_count, self.Q_table_tot, Text], f)

        afile = open('Saved_Data/Convergence_' + Text + '.pkl', 'wb')
        pickle.dump([self.steps_count, self.Q_table_mean], afile)
        '''
        afile = open('Q_Tables/Q_Table_' + Text + '.pkl', 'wb')
        pickle.dump(self.q_table, afile)
        '''
        with open("Table_Dim.txt", 'a') as myfile:
            myfile.write("Dimension of " + str(Text) + ": " + str(self.q_table.shape) + "\n")
        myfile.close()
        '''

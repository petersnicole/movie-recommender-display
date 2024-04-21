import pandas as pd
import numpy as np
from tqdm import tqdm
from scipy.special import softmax

# reading in needed csv files
gen_scores = pd.read_csv('genome-scores.csv')
ratings = pd.read_csv('ratings.csv')


def set_up_ratings(ratings, min_move=1000, min_use=50):
    ''' function for limiting the  movies that are being analyzed
    args:
        ratings: dataframe of all ratings
        min_move(int): the minimum number of reviews a movie must have to be considered
        min_use(int): the minimum number of reviews a user must have for their reviews to be considered
    returns:
        ratings: updated ratings dataframe
        movie_dict: mapping of movie ids from their original id to new ids
        '''

    # groupby dataframes to get number of reviews
    by_movie = ratings.groupby('movieId').count()
    by_user = ratings.groupby('userId').count()

    # limit to movies with enough reviews
    by_movie = by_movie.reset_index()[['movieId', 'rating']]
    by_movie = by_movie[by_movie['rating']>=min_move]

    # limit to users with enough reviews
    by_user = by_user.reset_index()[['userId', 'rating']]
    by_user = by_user[by_user['rating']>=min_use]

    # get list of movies to be considered and get id mapping
    all_movies = by_movie['movieId']
    movie_dict = dict(zip(all_movies, range(len(all_movies))))

    # limit ratings dataframe properly and set new movie ids based on mappin
    ratings = ratings[ratings['movieId'].isin(by_movie['movieId'])]
    ratings = ratings[ratings['userId'].isin(by_user['userId'])]
    ratings['movieId'] = ratings['movieId'].map(movie_dict)

    return ratings, movie_dict

# limiting data
ratings, movie_dict = set_up_ratings(ratings, min_move = 2000)

# print how many movies are being considers
print('toal movies being considered:', len(set(ratings['movieId'])))


def calculate_similarity(list1, list2):
    # function that creates similarity score 0-25 for 2 movies based on genome scores
    # list 1 and list 2 are lists of the relevance scores for 2 movies

    # make sure lists are even lengths
    if len(list1) != len(list2):
        raise ValueError("Lists must be of equal length")

    # determine max similarity score
    similarity_score = 25*len(list1)

    # Calculate similarity score
    similarity_score -= sum(abs(list1[i] - list2[i]) * 200 for i in range(len(list1)))

    return similarity_score / len(list1)    

def q_learning_v2(num_episodes, ratings, gen_scores):
    # q learning that uses estimated/current q values of possible actions to assign transition probabilities
    # uses similarity scores as well

    # get list of all movie ids and establish reward dict
    movies = list(set(ratings['movieId']))
    reward_dict= {0.5:-25, 1:-20, 1.5:-15, 2:-10, 2.5:-5, 3:0, 3.5:5, 4:10, 4.5:15, 5:25}

    # initialize Q table and fill it with rewards based on average ratings
    Q = np.zeros((len(movies), len(movies)))
    by_mov = ratings.groupby('movieId').mean()['rating']
    for i in tqdm(range(Q.shape[1])):
        Q[:, i] = (by_mov[i]-.5)*10-30  

    # initialize tables for number of updates and similarity scores
    num_updates = np.zeros((len(movies), len(movies)))
    sim_scores = np.zeros((len(movies), len(movies)))

    # initialize hyperparameters
    gamma = 0.0
    epsilon = 0.9
    decay_rate = 0.9998

    # set up optimal policy array and list of checkpoint values
    optimal_policy = np.random.choice(a = movies, size=(len(movies)))

    # lists for keeping track of average reward per timestep and number of timesteps per episode
    avg_rewards = []
    step_list = []

    for i in tqdm(range(num_episodes)):




        # reset environment and variables before each episode
        observation = ratings.sample(n=1)
        while observation['rating'].values[0] < 4.5:
            observation = ratings.sample(n=1)
        terminated = False
        reward = 0
        num_steps = 0
        cum_reward = 0

        # get id of start state movie and start list of all movies in episode
        mov = observation['movieId'].values[0]
        prev_actions = [mov]

        # create initial action space
        pos_actions = list(ratings[ratings['userId']==observation['userId'].values[0]]['movieId'])
        pos_actions = np.array([i for i in pos_actions if i not in prev_actions])

        # get relevance scores
        tags_mov = list(gen_scores[gen_scores['movieId']==mov]['relevance'])
        for j in pos_actions:

            # calculate similarity scores for every movie in action space without one
            if not sim_scores[mov, j]:
                num_updates[mov, j] = 1
                num_updates[j, mov] = 1
                tags_2 = list(gen_scores[gen_scores['movieId']==j]['relevance'])
                if tags_mov and tags_2:
                    sim_scores[mov,j] = calculate_similarity(tags_mov, tags_2)
                    sim_scores[j,mov] = sim_scores[mov,j]
                    Q[mov, j] += sim_scores[mov,j]
                    Q[j, mov] += sim_scores[j, mov]

        # print('Mean sim score:', np.mean(sim_scores[sim_scores!=0]))
        # print('std sim score:', np.std(sim_scores[sim_scores!=0]))
        # until episode is terminated keep exploring
        while not terminated:

            # update action space
            pos_actions = [j for j in pos_actions if j not in prev_actions]

            # update current movie state
            mov = observation['movieId'].values[0]

            # epsilon greedy
            if np.random.rand()< epsilon:

                # use softmax of similarity scores to determine action
                probs = softmax(sim_scores[mov, pos_actions])
                action = int(np.random.choice(a = pos_actions, p = probs)) 
            else:

                # choose best possible action
                # print(Q[mov, pos_actions])
                maxi = np.argmax(Q[mov, pos_actions])
                action = pos_actions[maxi]

            # add action to list of taken actions
            prev_actions += [action]

            # get the new state
            new_state = ratings[(ratings['userId'] == observation['userId'].values[0]) & (ratings['movieId'] == action)]
            if new_state.empty:
                continue
    
            # calculate the reward
            reward = reward_dict[new_state['rating'].values[0]] + sim_scores[mov,new_state['movieId'].values[0]]
            cum_reward += reward

            # calculate eta then update matrices correctly using Q-learning equation
            num_updates[mov, action] += 1
            eta = 1/(1+num_updates[mov, action])
            Q[mov, action] = (1-eta)*Q[mov, action]+eta*(reward+gamma*np.max(Q[action,:]))

            # update optimal policy from new information
            optimal_policy[mov] = int(np.argmax(Q[mov,:]))

            # make the new state the observation for the net time step
            observation = new_state
            num_steps += 1

            # end episode if end conditions are met
            if reward_dict[new_state['rating'].values[0]] < 10 or len(pos_actions) < 2:
                avg_rewards += [cum_reward/num_steps]
                step_list += [num_steps]
                terminated = True

        # update epsilon after each episode
        epsilon *= decay_rate

        # change optimal policy to ints
        optimal_policy = optimal_policy.astype(int)

    return Q, optimal_policy, avg_rewards, step_list

gen_scores['movieId'] = gen_scores['movieId'].apply(lambda i: movie_dict.get(i, -1))
q, opt, rewards, steps = q_learning_v2(5000, ratings, gen_scores)

pd.DataFrame(q).to_csv('newqtable4.csv')
pd.DataFrame(opt).to_csv('new_policy4.csv')
pd.DataFrame(np.array(rewards)).to_csv('rewards4.csv')
pd.DataFrame(np.array(steps)).to_csv('steps4.csv')
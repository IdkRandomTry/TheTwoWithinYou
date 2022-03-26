import pickle

with open('save_state.txt', 'wb') as open_file:
    pickle.dump([False, False, False, False, False, False], open_file)
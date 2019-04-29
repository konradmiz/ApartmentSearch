import numpy as np
import pandas as pd

def run_search(applicant_values):
    best_so_far = -1
    stopping_length = len(applicant_values) / np.math.e
    
    for idx, candidate in enumerate(applicant_values):
        if idx < stopping_length:
            if candidate > best_so_far:
                best_so_far = candidate
        else:
            if candidate > best_so_far:
                if candidate == max(applicant_values):
                    return "Best"
                elif candidate >= np.percentile(applicant_values, 90):
                    return "90th"
                else:
                    return 0
    return 0
    

num_trials = 100000
total_pop_size = [10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 200, 500, 1000, 2000, 5000] #, 10000, 20000]

success_df = pd.DataFrame({'pop_size' : total_pop_size,
              'success' : np.zeros(len(total_pop_size))})


for j, k in enumerate(total_pop_size): 
    results = []

    for _ in range(num_trials):
        applicant_values = np.random.uniform(size = k)
        results.append(run_search(applicant_values))
        success_df.iloc[j, 1] = (results.count("Best") + results.count("90th"))/len(results)

success_df

success_df.plot(x = 'pop_size', y = 'success', logx = True, style = '.-')



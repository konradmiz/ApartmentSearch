import numpy as np

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
                    return 1
                else:
                    return 0
    return 0
    

num_trials = 10000
total_pop_size = 200
success = 0

for _ in range(num_trials):
    applicant_values = np.random.uniform(size = total_pop_size)
    success += run_search(applicant_values)

success/num_trials


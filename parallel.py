def parallel_function(function_to_apply, list_of_inputs, num_threads=None):
    from multiprocessing import Pool
    pool = Pool(processes=num_threads)
    result = pool.map(function_to_apply, list_of_inputs)
    pool.close()
    pool.join()
    return result

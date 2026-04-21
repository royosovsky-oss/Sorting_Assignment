import random
import time
import copy
import statistics
import matplotlib.pyplot as plt
import argparse
import sys


def Selection_Sort(Array):
    """
    Sorts an array in-place using the Selection Sort algorithm.
    """
    n = len(Array)
    for i in range(n):
        # Assume the current element is the minimum
        min_idx = i

        # Find the actual minimum element in the remaining unsorted array
        for j in range(i + 1, n):
            if Array[j] < Array[min_idx]:
                min_idx = j

        # Swap the found minimum element with the first unsorted element
        Array[i], Array[min_idx] = Array[min_idx], Array[i]

    return Array


def Insertion_Sort(Array):
    """
    Sorts an array in-place using the Insertion Sort algorithm.
    """
    n = len(Array)

    # We start from 1 because we assume the first element (index 0)
    # is already a "sorted" sub-list of one item.
    for i in range(1, n):
        key = Array[i]  # The "new card" we want to place
        j = i - 1

        # Look at the sorted cards to the left.
        # If they are bigger than our 'key', shift them one spot to the right.
        while j >= 0 and Array[j] > key:
            Array[j + 1] = Array[j]
            j -= 1

        # We found the right spot! Insert the key.
        Array[j + 1] = key

    return Array


def Merge_Sort(Array):
    """
    Sorts an array using the Merge Sort algorithm.
    """
    # Base case: if the array has 1 or 0 elements, it is already sorted.
    if len(Array) > 1:
        mid = len(Array) // 2  # Find the middle index

        # Divide the array into two halves
        Left_Half = Array[:mid]
        Right_Half = Array[mid:]

        # Recursively call merge_sort on both halves
        Merge_Sort(Left_Half)
        Merge_Sort(Right_Half)

        # --- The "Merge" Phase ---
        # i = index for Left_Half, j = index for Right_Half, k = index for main arr
        i = j = k = 0

        # Compare elements from the left and right halves and place the
        # smaller one back into the main array.
        while i < len(Left_Half) and j < len(Right_Half):
            if Left_Half[i] < Right_Half[j]:
                Array[k] = Left_Half[i]
                i += 1
            else:
                Array[k] = Right_Half[j]
                j += 1
            k += 1

        # If there are any remaining elements in the left half, add them
        while i < len(Left_Half):
            Array[k] = Left_Half[i]
            i += 1
            k += 1

        # If there are any remaining elements in the right half, add them
        while j < len(Right_Half):
            Array[k] = Right_Half[j]
            j += 1
            k += 1

    return Array


def Measure_Runtime(Algorithm, Array):
    """
    Measures the runtime of a specific sorting algorithm on a given array.
    """
    # Create a deep copy so the original array remains untouched for the next algorithm
    Arr_copy = copy.deepcopy(Array)

    Start_Time = time.perf_counter()
    Algorithm(Arr_copy)
    End_Time = time.perf_counter()

    return End_Time - Start_Time

def Generate_Random_Array(Size):
    """
    Generates an array of the given size filled with random integers.
    """
    # We use a list comprehension to quickly generate 'size' amount of numbers.
    # We will limit the random integers between 1 and 10,000 to keep it manageable.
    return [random.randint(1, 10000) for _ in range(Size)]


def Generate_Nearly_Sorted_Array(Size, Noise_Level):
    """
    Generates a sorted array and then randomly swaps a percentage of elements.
    noise_level should be a decimal (e.g., 0.05 for 5%).
    """
    # Start with a perfectly sorted array [1, 2, 3, ..., size]
    Arr = list(range(1, Size + 1))

    # Calculate exactly how many swaps to make
    num_swaps = int(Size * Noise_Level)

    for _ in range(num_swaps):
        # Pick two random indices and swap them
        idx1 = random.randint(0, Size - 1)
        idx2 = random.randint(0, Size - 1)
        Arr[idx1], Arr[idx2] = Arr[idx2], Arr[idx1]

    return Arr


def run_random_experiment(Algorithms, Sizes, Repetitions):
    """
    Runs the sorting algorithms on random arrays of various sizes,
    multiple times, and calculates the average and standard deviation.
    """
    # Create a dictionary to neatly store all our results for plotting later
    Results = {alg.__name__: {'sizes': Sizes, 'averages': [], 'stdevs': []} for alg in Algorithms}

    for Size in Sizes:
        print(f"Running experiments for array Size: {Size}...")

        for Alg in Algorithms:
            times = []

            # Repeat the experiment 'repetitions' times to get statistically valid data
            for _ in range(Repetitions):
                # Generate a fresh random array for each repetition
                Arr = Generate_Random_Array(Size)

                # Measure how long the algorithm takes
                time_taken = Measure_Runtime(Alg, Arr)
                times.append(time_taken)

            # Calculate average and standard deviation
            avg_time = statistics.mean(times)

            # Standard deviation requires at least 2 repetitions to calculate
            std_dev = statistics.stdev(times) if Repetitions > 1 else 0.0

            # Save the calculated metrics into our results dictionary
            Results[Alg.__name__]['averages'].append(avg_time)
            Results[Alg.__name__]['stdevs'].append(std_dev)

    return Results


def run_nearly_sorted_experiment(algorithms, sizes, repetitions, noise_level):
    """
    Runs the algorithms on nearly sorted arrays and calculates metrics.
    """
    Results = {alg.__name__: {'sizes': sizes, 'averages': [], 'stdevs': []} for alg in algorithms}

    for size in sizes:
        print(f"Running nearly sorted (noise={int(noise_level * 100)}%) for array size: {size}...")

        for alg in algorithms:
            times = []
            for _ in range(repetitions):
                # Using the new nearly-sorted generator!
                arr = Generate_Nearly_Sorted_Array(size, noise_level)
                time_taken = Measure_Runtime(alg, arr)
                times.append(time_taken)

            avg_time = statistics.mean(times)
            std_dev = statistics.stdev(times) if repetitions > 1 else 0.0

            Results[alg.__name__]['averages'].append(avg_time)
            Results[alg.__name__]['stdevs'].append(std_dev)

    return Results


def Plot_Results(Results, title, filename):
    """
    Plots the average running times and saves the figure.
    Includes a shaded region for the standard deviation and exact time annotations.
    """
    # Adding a clean style 
    plt.style.use('seaborn-v0_8-darkgrid')

    plt.figure(figsize=(10, 6))

    for alg_name, data in Results.items():
        sizes = data['sizes']
        averages = data['averages']
        stdevs = data['stdevs']

        # Plot the main line with circular markers
        plt.plot(sizes, averages, marker='o', label=alg_name)

        # --- NEW CODE: Add the exact time text above each dot ---
        # --- NEW CODE: Only annotate the final data point ---
        last_idx = len(sizes) - 1
        time_text = f"{averages[last_idx]:.4f}s"

        plt.annotate(time_text,
                     (sizes[last_idx], averages[last_idx]),
                     textcoords="offset points",
                     xytext=(0, 10),  # Push it a bit higher
                     ha='center',
                     fontsize=9,
                     fontweight='bold')  # Make it bold so it pops
        # --------------------------------------------------------

        # Calculate the upper and lower bounds for the standard deviation shading
        lower_bound = [max(0, avg - std) for avg, std in zip(averages, stdevs)]
        upper_bound = [avg + std for avg, std in zip(averages, stdevs)]

        # Add the shaded region
        plt.fill_between(sizes, lower_bound, upper_bound, alpha=0.2)

    # Add labels, title, a legend, and a grid
    plt.title(title)
    plt.xlabel('Array size (n)')
    plt.ylabel('Runtime (seconds)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)

    # Save the plot to a file
    plt.savefig(filename)
    print(f"Plot successfully saved as {filename}")

    # Display the plot on your screen
    plt.show()


if __name__ == "__main__":
    # 1. Set up the argument parser
    parser = argparse.ArgumentParser(description="Run sorting algorithm experiments.")
    parser.add_argument('-a', nargs='+', type=int, required=True,
                        help="Algorithms to compare: 1-Bubble, 2-Selection, 3-Insertion, 4-Merge, 5-Quick")
    parser.add_argument('-s', nargs='+', type=int, required=True,
                        help="Array sizes, e.g., 100 500 1000")
    parser.add_argument('-e', type=int, required=True,
                        help="Experiment type: 0-Random, 1-Nearly sorted (5%), 2-Nearly sorted (20%)")
    parser.add_argument('-r', type=int, required=True,
                        help="Number of repetitions")

    # 2. Parse the arguments provided by the user
    args = parser.parse_args()

    # 3. Map the user's number choices to our actual functions
    # (Note: We only implemented 2, 3, and 4. If they choose 1 or 5, we gracefully exit).
    algorithm_map = {
        2: Selection_Sort,
        3: Insertion_Sort,
        4: Merge_Sort
    }

    algorithms_to_test = []
    for alg_id in args.a:
        if alg_id in algorithm_map:
            algorithms_to_test.append(algorithm_map[alg_id])
        else:
            print(f"Error: Algorithm ID {alg_id} is not implemented. Please choose 2, 3, or 4.")
            sys.exit(1)

    # 4. Route to the correct experiment based on the -e flag
    if args.e == 0:
        print(f"--- Running Random Experiment ---")
        results = run_random_experiment(algorithms_to_test, args.s, args.r)
        Plot_Results(results, "Runtime Comparison (Random)", "result1.png")

    elif args.e == 1:
        print(f"--- Running Nearly Sorted (5% Noise) ---")
        results = run_nearly_sorted_experiment(algorithms_to_test, args.s, args.r, noise_level=0.05)
        Plot_Results(results, "Runtime Comparison (Nearly Sorted, 5%)", "result2.png")

    elif args.e == 2:
        print(f"--- Running Nearly Sorted (20% Noise) ---")
        results = run_nearly_sorted_experiment(algorithms_to_test, args.s, args.r, noise_level=0.20)
        Plot_Results(results, "Runtime Comparison (Nearly Sorted, 20%)", "result_noise_20.png")

    else:
        print("Error: Invalid experiment type. Choose 0, 1, or 2.")
        sys.exit(1)

import pandas as pd
import numpy as np
import re

green_text = "\033[32m"
red_text = "\033[31m"

# ANSI escape code to reset text color to default
reset_text = "\033[0m"

# define a function to extract the x value from the format "x tests failed out of y"
def extract_x_value(string):
    if pd.isna(string): return None
    match = re.search(r'(\d+) tests failed out of \d+', string)
    return int(match.group(1)) if match else None

# define a function to extract the y value from the format "x tests failed out of y"
def extract_y_value(string):
    if pd.isna(string): return None
    match = re.search(r'\d+ tests failed out of (\d+)', string)
    return int(match.group(1)) if match else None

# read the dataset of open-source projects collected from GitHub
test_df = pd.read_csv('dataset-test.csv')
df = pd.read_csv('dataset.csv')
N = 60

print("=" * ((N - len("Total Number of Codebases"))//2), f"{red_text}Total Number of Codebases {reset_text}", "=" * ((N - len("Total Number of Codebases"))//2))
print(df.shape[0])

print("=" * ((N - len("This is the results for Table I"))//2), f"{red_text}This is the results for Table I {reset_text}", "=" * ((N - len("This is the results for Table I"))//2))

print("=" * ((N - len("Projects"))//2), "Projects", "=" * ((N - len("Projects"))//2))
category_counts = df['category'].value_counts()
category_counts_formatted = category_counts.apply(lambda x: f'{x:02}')
print(category_counts_formatted)
print("TOTAL = ", df.shape)
print(f"{green_text}{(N+2) * '*'}{reset_text}")
print(df[df['category'].isna()]['project'])

print("=" * ((N - len("KLOC"))//2), "KLOC", "=" * ((N - len("KLOC"))//2))
category_loc_sum = df.groupby('category')['LOC'].sum() / 1000
category_loc_sum_formatted = category_loc_sum.apply(lambda x: f'{int(x):02}')
print(category_loc_sum_formatted)
print("TOTAL = ", int(df['LOC'].sum() / 1000))
print(f"{green_text}{(N+2) * '*'}{reset_text}")
print(df[df['LOC'].isna()]['project'])

print("=" * ((N - len("Executable Tests"))//2), "Executable Tests", "=" * ((N - len("Executable Tests"))//2))
category_loc_sum = df.groupby('category')['#executable tests'].sum()
print(category_loc_sum)
print("TOTAL = ", df['#executable tests'].sum())
print(f"{green_text}{(N+2) * '*'}{reset_text}")
print(df[df['#executable tests'].isna()]['project'])

print("=" * ((N - len("Test Cases"))//2), "Test Cases", "=" * ((N - len("Test Cases"))//2))
category_loc_sum = df.groupby('category')['#test cases'].sum()
print(category_loc_sum)
print("TOTAL = ", df['#test cases'].sum())
print(f"{green_text}{(N+2) * '*'}{reset_text}")
print(df[df['#test cases'].isna()]['project'])
print(f"{green_text}{(N+2) * '@'}{reset_text}\n")


print("=" * ((N - len("This is the results for Table II"))//2), f"{red_text}This is the results for Table II{reset_text}", "=" * ((N - len("This is the results for Table II"))//2))

# filter out rows where "How many build challenges?" is 0
error_df = df[df['What is the build error'].notna() & (df['What is the build error'] != 'N/A')]

# split the "What is the build error" column and explode into separate rows
error_list = error_df['What is the build error'].str.split(',').explode()

# strip whitespace and count the frequency of each error
error_counts = error_list.str.strip().value_counts()
error_counts_formatted = error_counts.apply(lambda x: f'{x:02}')
assert len(error_list) == df[~df['What is the build error'].isna()]['How many build challenges?'].sum()

print(error_counts_formatted)
print("Total number of build errors", " " * 8, df[~df['What is the build error'].isna()]['How many build challenges?'].sum())
print(f"{green_text}{(N+2) * '@'}{reset_text}\n")


# filter out rows where "root cause" is N/A or empty
root_cause_df = df[df['root cause'].notna() & (df['root cause'] != 'N/A')]

# split the "root cause" column and explode into separate rows
root_cause_list = root_cause_df['root cause'].str.split(',').explode()
root_cause_list = root_cause_list.tolist()
root_cause_list = [elem.strip() for elem in root_cause_list]

my_dict = {}
for root_cause in root_cause_list:
    pattern = r'^(.*) \((\d+)\)$'
    match_str = re.match(pattern, root_cause)
    if match_str:
        X = match_str.group(1)
        n = int(match_str.group(2))
        if X in my_dict.keys(): my_dict[X] = my_dict[X] + n
        else: my_dict[X] = n
    else: print(f"{red_text}input string is not a valid root cause {root_cause}{reset_text}")

# filter out rows where "emcc build in wasm" is 'Yes'
successful_projects = df[df['emcc build in wasm'] == 'Yes']
projects_without_build_error = df[df['What is the build error'].isna()]
category_loc_sum = df.groupby('emcc build in wasm')['project'].count()
print(category_loc_sum)

print("projects which could be built in wasm successfully: ", successful_projects.shape)
print("projects for which error type column is N/A:        ", projects_without_build_error.shape)
print("projects for which number of build errors is 0:     ", df[df['How many build challenges?'] == 0].shape)

assert df[df['How many build challenges?'] == 0].shape == successful_projects.shape
assert df[df['How many build challenges?'] == 0].shape == projects_without_build_error.shape

for index, row in df.iterrows():
    t1 = extract_y_value(row['Result of cross-compilation with no change '])
    t2 = extract_y_value(row['Test results for Native binary'])
    t3 = extract_y_value(row['Manually analyzed test results for WebAssembly'])
    executable_tests = row['#executable tests']
    assert (pd.isna(t3) or (t2 == t3 and t2 == executable_tests and (t1 == t2 or pd.isna(t1))))

print(f"{green_text}{(N+2) * '@'}{reset_text}\n")
print("=" * ((N - len("This is the results for Table III"))//2), f"{red_text} This is the results for Table III{reset_text}", "=" * ((N - len("This is the results for Table III"))//2))

print("=" * ((N - len("Manual Compilation"))//2), f"{red_text}Manual Compilation{reset_text}", "=" * ((N - len("Manual Compilation"))//2))

initial_results_for_native = 0
initial_results_for_wasm = 0
failed_to_be_built_in_wasm = 0
projects_with_tests_discrepancies = 0
projects_without_tests_discrepancies = 0
total_discripancies = 0
for index, row in df.iterrows():
    if not pd.isna(row['Result of cross-compilation with no change ']):
        t1 = extract_x_value(row['Result of cross-compilation with no change '])
        t2 = extract_x_value(row['Test results for Native binary'])
        initial_results_for_wasm += t1
        initial_results_for_native += t2
        if t1 != t2:
            projects_with_tests_discrepancies += 1
            total_discripancies += (t1 - t2)
        else:
            projects_without_tests_discrepancies += 1
    else:
        failed_to_be_built_in_wasm += 1

total_executable_for_projects_could_be_built =  df[df['emcc build in wasm'] == "Yes"]['#executable tests'].sum()
print("Projects which could be built in wasm successfully: ", df.shape[0] - failed_to_be_built_in_wasm)
print("For WebAssembly", initial_results_for_wasm, "executabel tests failed out of", total_executable_for_projects_could_be_built, "and", total_executable_for_projects_could_be_built - initial_results_for_wasm, "passed")
print("For native binary", initial_results_for_native, "executable tests failed out of", total_executable_for_projects_could_be_built, "and", total_executable_for_projects_could_be_built - initial_results_for_native, "passed")
print(f"Manual compilation showed no  discrepancies for {projects_without_tests_discrepancies} projects")
print(f"Manual compilation showed {total_discripancies} discrepancies for {projects_with_tests_discrepancies} projects")

print("Projects which could not be built in wasm successfully: ", failed_to_be_built_in_wasm)
print("Total number of executable tests for failed projects:", df[df['emcc build in wasm'] == "Build error"]['#executable tests'].sum())

assert df[df['emcc build in wasm'] == "Build error"].shape == df[df['emcc build in wasm'] != "Yes"].shape

projects_without_tests_discrepancies = 0
projects_with_tests_discrepancies = 0
total_discripancies = 0
total_projects_wasmchecker_could_build = 0
wasmchecker_results = df['Can WasmChecker build the project? what is the result of differential testing?'].tolist()
for res in wasmchecker_results:
    build_ = res.split('-')[0].strip()
    if build_ == "Y": total_projects_wasmchecker_could_build += 1
    result = res.split('-')[1].strip()
    pattern = r'(\d+) failed in wasm'
    match_str = re.match(pattern, result)
    if match_str:
        X = match_str.group(1)
        total_discripancies = total_discripancies + int(X)
        projects_with_tests_discrepancies += 1
    elif result == "0 discrepancies":
        projects_without_tests_discrepancies += 1
    elif build_ != "N": 
        print(f"{red_text}input string is not a valid discripancy {result}{reset_text}")

total_tests_for_projects_wasmchecker_could_not_build = 0
for index, row in df.iterrows():
    if row['Can WasmChecker build the project? what is the result of differential testing?'].split('-')[0].strip() == "N":
        total_tests_for_projects_wasmchecker_could_not_build += int(row['#executable tests'])

print("=" * ((N - len("WasmChecker Effectiveness"))//2), f"{red_text}WasmChecker Effectiveness {reset_text}", "=" * ((N - len("WasmChecker Effectiveness"))//2))

print("Total number of projects that WasmChecker could build: ", total_projects_wasmchecker_could_build, "out of", 
      df.shape[0], "or", np.round(total_projects_wasmchecker_could_build*100/df.shape[0]),"%")

print("Total number of build errors that WasmChecker could resolve:", df['How many build errors are addressed by WasmChecker'].sum(), "out of", 
      df['How many build challenges?'].sum(), "or", np.round(df['How many build errors are addressed by WasmChecker'].sum()*100/df['How many build challenges?'].sum()), "%")

total_tests = 0
manual_analysis = df[~df['Manually analyzed test results for WebAssembly'].isna()]['Manually analyzed test results for WebAssembly'].tolist()
for analysis in manual_analysis:
    if analysis == None:
        continue
    pattern = r'(\d+) tests failed out of (\d+)'
    match_str = re.match(pattern, analysis)
    if match_str:
        X = match_str.group(2)
        total_tests = total_tests + int(X)
    else:
        print(f"{red_text}input string is not a valid manual analysis {analysis}{reset_text}")
print("Total number of discripancies reported by WasmChecker:", total_discripancies, "out of", total_tests, "executable tests")

print(f"WasmChecker reported {total_discripancies} discrepancies for {projects_with_tests_discrepancies} projects")
print(f"WasmChecker reported no  discrepancies for {projects_without_tests_discrepancies} projects")
print(f"WasmChecker could not build {df.shape[0] - total_projects_wasmchecker_could_build} projects containing {total_tests_for_projects_wasmchecker_could_not_build} executable tests")
print(f"WasmChecker reported {df['FP'].sum()} false positive alarms and {total_discripancies - df['FP'].sum()} true discrepancies")

print(f"{green_text}{(N+2) * '@'}{reset_text}\n")

########################################################

total_discripancies = 0
projects_without_tests_discrepancies = 0
projects_with_tests_discrepancies = 0
total_projects_wasmchecker_could_build = 0
wasmchecker_results = df[df['emcc build in wasm'] == "Yes"]['Can WasmChecker build the project? what is the result of differential testing?'].tolist()
print("Total number of projects compiled both manually and by WasmChecker:", len(wasmchecker_results))
for res in wasmchecker_results:
    build_ = res.split('-')[0].strip()
    if build_ == "Y": total_projects_wasmchecker_could_build += 1
    result = res.split('-')[1].strip()
    pattern = r'(\d+) failed in wasm'
    match_str = re.match(pattern, result)
    if match_str:
        X = match_str.group(1)
        total_discripancies = total_discripancies + int(X)
        projects_with_tests_discrepancies += 1
    elif result == "0 discrepancies":
        projects_without_tests_discrepancies += 1
    elif build_ != "N": 
        print(f"{red_text}input string is not a valid discripancy {result}{reset_text}")

print("Total number of discripancies reported by WasmChecker:", total_discripancies)
print(f"WasmChecker reported {total_discripancies} discrepancies across {projects_with_tests_discrepancies} projects")
print(f"WasmChecker reported no  discrepancies for {projects_without_tests_discrepancies} projects")
#print(f"WasmChecker reported {df['FP'].sum()} false positive alarms and {total_discripancies - df['FP'].sum()} true discrepancies")

print(f"{green_text}{(N+2) * '@'}{reset_text}\n")

total_discripancies = 0
projects_without_tests_discrepancies = 0
projects_with_tests_discrepancies = 0
total_projects_wasmchecker_could_build = 0
wasmchecker_results = df[(df['emcc build in wasm'] == "Build error") & (df['Can WasmChecker build the project? what is the result of differential testing?'].str.startswith('Y'))]['Can WasmChecker build the project? what is the result of differential testing?'].tolist()
print("Total number of projects compilable only by WasmChecker:", len(wasmchecker_results))
for res in wasmchecker_results:
    build_ = res.split('-')[0].strip()
    if build_ == "Y": total_projects_wasmchecker_could_build += 1
    result = res.split('-')[1].strip()
    pattern = r'(\d+) failed in wasm'
    match_str = re.match(pattern, result)
    if match_str:
        X = match_str.group(1)
        total_discripancies = total_discripancies + int(X)
        projects_with_tests_discrepancies += 1
    elif result == "0 discrepancies":
        projects_without_tests_discrepancies += 1
    elif build_ != "N": 
        print(f"{red_text}input string is not a valid discripancy {result}{reset_text}")

print("Total number of discripancies reported by WasmChecker:", total_discripancies)
print(f"WasmChecker reported {total_discripancies} discrepancies across {projects_with_tests_discrepancies} projects")
print(f"WasmChecker reported no  discrepancies for {projects_without_tests_discrepancies} projects")
#print(f"WasmChecker reported {df['FP'].sum()} false positive alarms and {total_discripancies - df['FP'].sum()} true discrepancies")

print(f"{green_text}{(N+2) * '@'}{reset_text}\n")

#########################################################


print("=" * ((N - len("Total Number of Test Codebases"))//2), f"{red_text}Total Number of Test Codebases{reset_text}", "=" * ((N - len("Total Number of Test Codebases"))//2))
print(test_df.shape[0])

print("=" * ((N - len("This is the results for Table IV"))//2), f"{red_text}This is the results for Table IV {reset_text}", "=" * ((N - len("This is the results for Table IV"))//2))

print("=" * ((N - len("Projects"))//2), "Projects", "=" * ((N - len("Projects"))//2))
category_counts = test_df['category'].value_counts()
print(category_counts)
print("TOTAL = ", test_df.shape)
print(f"{green_text}{(N+2) * '*'}{reset_text}")
print(test_df[test_df['category'].isna()]['project'])

print("=" * ((N - len("KLOC"))//2), "KLOC", "=" * ((N - len("KLOC"))//2))
category_loc_sum = test_df.groupby('category')['LOC'].sum() / 1000
category_loc_sum_formatted = category_loc_sum.apply(lambda x: f'{x:02.0f}')
print(category_loc_sum_formatted)
print("TOTAL = ", int(test_df['LOC'].sum() / 1000))
print(f"{green_text}{(N+2) * '*'}{reset_text}")
print(test_df[test_df['LOC'].isna()]['project'])

print("=" * ((N - len("Executable Tests"))//2), "Executable Tests", "=" * ((N - len("Executable Tests"))//2))
category_loc_sum = test_df.groupby('category')['#executable tests'].sum()
print(category_loc_sum)
print("TOTAL = ", test_df['#executable tests'].sum())
print(f"{green_text}{(N+2) * '*'}{reset_text}")
print(test_df[test_df['#executable tests'].isna()]['project'])

print("=" * ((N - len("Test Cases"))//2), "Test Cases", "=" * ((N - len("Test Cases"))//2))
category_loc_sum = test_df.groupby('category')['#test cases'].sum()
print(category_loc_sum)
print("TOTAL = ", test_df['#test cases'].sum())
print(f"{green_text}{(N+2) * '*'}{reset_text}")
print(test_df[test_df['#test cases'].isna()]['project'])
print(f"{green_text}{(N+2) * '@'}{reset_text}\n")


print("=" * ((N - len("This is the results for Table II"))//2), f"{red_text}This is the results for Table II{reset_text}", "=" * ((N - len("This is the results for Table II"))//2))

# filter out rows where "How many build challenges?" is 0
error_test_df = test_df[test_df['What is the build error'].notna() & (test_df['What is the build error'] != 'N/A')]

# split the "What is the build error" column and explode into separate rows
error_list = error_test_df['What is the build error'].str.split(',').explode()

# strip whitespace and count the frequency of each error
error_counts = error_list.str.strip().value_counts()
error_counts_formatted = error_counts.apply(lambda x: f'{x:02}')
assert len(error_list) == test_df[~test_df['What is the build error'].isna()]['How many build challenges?'].sum()

print(error_counts_formatted)
print("Total number of build errors", " " * 6, f"{test_df[~test_df['What is the build error'].isna()]['How many build challenges?'].sum():02}")
print(f"{green_text}{(N+2) * '@'}{reset_text}\n")


# filter out rows where "root cause" is N/A or empty
root_cause_test_df = test_df[test_df['root cause'].notna() & (test_df['root cause'] != 'N/A')]

# split the "root cause" column and explode into separate rows
root_cause_list = root_cause_test_df['root cause'].str.split(',').explode()
root_cause_list = root_cause_list.tolist()
root_cause_list = [elem.strip() for elem in root_cause_list]

my_dict_test = {}
for root_cause in root_cause_list:
    pattern = r'^(.*) \((\d+)\)$'
    match_str = re.match(pattern, root_cause)
    if match_str:
        X = match_str.group(1)
        n = int(match_str.group(2))
        if X in my_dict_test.keys(): my_dict_test[X] = my_dict_test[X] + n
        else: my_dict_test[X] = n
    else: print(f"{red_text}input string is not a valid root cause {root_cause}{reset_text}")

# filter out rows where "emcc build in wasm" is 'Yes'
successful_projects = test_df[test_df['emcc build in wasm'] == 'Yes']
projects_without_build_error = test_df[test_df['What is the build error'].isna()]
category_loc_sum = test_df.groupby('emcc build in wasm')['project'].count()
print(category_loc_sum)

print("projects which could be built in wasm successfully: ", successful_projects.shape)
print("projects for which error type column is N/A:        ", projects_without_build_error.shape)
print("projects for which number of build errors is 0:     ", test_df[test_df['How many build challenges?'] == 0].shape)

print(f"{green_text}{(N+2) * '@'}{reset_text}\n")

print("=" * ((N - len("This is the results for Table V"))//2), f"{red_text}This is the results for Table V{reset_text}", "=" * ((N - len("This is the results for Table V"))//2))
print("=" * ((N - len("Manual Compilation"))//2), f"{red_text}Manual Compilation{reset_text}", "=" * ((N - len("Manual Compilation"))//2))

initial_results_for_native = 0
initial_results_for_wasm = 0
failed_to_be_built_in_wasm = 0
projects_with_tests_discrepancies = 0
projects_without_tests_discrepancies = 0
total_discripancies = 0
for index, row in test_df.iterrows():
    if not pd.isna(row['Result of cross-compilation with no change ']):
        t1 = extract_x_value(row['Result of cross-compilation with no change '])
        t2 = extract_x_value(row['Test results for Native binary'])
        initial_results_for_wasm += t1
        initial_results_for_native += t2
        if t1 != t2:
            projects_with_tests_discrepancies += 1
            total_discripancies += (t1 - t2)
        else:
            projects_without_tests_discrepancies += 1
    else:
        failed_to_be_built_in_wasm += 1

total_executable_for_projects_could_be_built =  test_df[test_df['emcc build in wasm'] == "Yes"]['#executable tests'].sum()
print("Projects which could be built in wasm successfully: ", test_df.shape[0] - failed_to_be_built_in_wasm)
print("For WebAssembly", initial_results_for_wasm, "executabel tests failed out of", total_executable_for_projects_could_be_built, "and", total_executable_for_projects_could_be_built - initial_results_for_wasm, "passed")
print("For native binary", initial_results_for_native, "executable tests failed out of", total_executable_for_projects_could_be_built, "and", total_executable_for_projects_could_be_built - initial_results_for_native, "passed")
print(f"Manual compilation showed no  discrepancies for {projects_without_tests_discrepancies} projects")
print(f"Manual compilation showed {total_discripancies} discrepancies for {projects_with_tests_discrepancies} projects")

print("Projects which could not be built in wasm successfully: ", failed_to_be_built_in_wasm)
print("Total number of executable tests for failed projects:", test_df[test_df['emcc build in wasm'] == "Build error"]['#executable tests'].sum())



assert test_df[test_df['emcc build in wasm'] == "Build error"].shape == test_df[test_df['emcc build in wasm'] != "Yes"].shape

projects_without_tests_discrepancies = 0
projects_with_tests_discrepancies = 0
total_discripancies = 0
total_projects_wasmchecker_could_build = 0
wasmchecker_results = test_df['Can WasmChecker build the project? what is the result of differential testing?'].tolist()
for res in wasmchecker_results:
    build_ = res.split('-')[0].strip()
    if build_ == "Y": total_projects_wasmchecker_could_build += 1
    result = res.split('-')[1].strip()
    pattern = r'(\d+) failed in wasm'
    match_str = re.match(pattern, result)
    if match_str:
        X = match_str.group(1)
        total_discripancies = total_discripancies + int(X)
        projects_with_tests_discrepancies += 1
    elif result == "0 discrepancies":
        projects_without_tests_discrepancies += 1
    elif build_ != "N": 
        print(f"{red_text}input string is not a valid discripancy {result}{reset_text}")

total_tests_for_projects_wasmchecker_could_not_build = 0
for index, row in test_df.iterrows():
    if row['Can WasmChecker build the project? what is the result of differential testing?'].split('-')[0].strip() == "N":
        total_tests_for_projects_wasmchecker_could_not_build += int(row['#executable tests'])

print("=" * ((N - len("WasmChecker Effectiveness"))//2), f"{red_text}WasmChecker Effectiveness {reset_text}", "=" * ((N - len("WasmChecker Effectiveness"))//2))

print("Total number of projects that WasmChecker could build: ", total_projects_wasmchecker_could_build, "out of", 
      test_df.shape[0], "or", np.round(total_projects_wasmchecker_could_build*100/test_df.shape[0]),"%")

print("Total number of build errors that WasmChecker could resolve:", test_df['How many build errors are addressed by WasmChecker'].sum(), "out of", 
      test_df['How many build challenges?'].sum(), "or", np.round(test_df['How many build errors are addressed by WasmChecker'].sum()*100/test_df['How many build challenges?'].sum()), "%")

total_tests = 0
manual_analysis = test_df[~test_df['Manually analyzed test results for WebAssembly'].isna()]['Manually analyzed test results for WebAssembly'].tolist()
for analysis in manual_analysis:
    if analysis == None:
        continue
    pattern = r'(\d+) tests failed out of (\d+)'
    match_str = re.match(pattern, analysis)
    if match_str:
        X = match_str.group(2)
        total_tests = total_tests + int(X)
    else:
        print(f"{red_text}input string is not a valid manual analysis {analysis}{reset_text}")
print("Total number of discripancies reported by WasmChecker:", total_discripancies, "out of", total_tests, "executable tests")

print(f"WasmChecker reported {total_discripancies} discrepancies for {projects_with_tests_discrepancies} projects")
print(f"WasmChecker reported no  discrepancies for {projects_without_tests_discrepancies} projects")
print(f"WasmChecker could not build {test_df.shape[0] - total_projects_wasmchecker_could_build} projects containing {total_tests_for_projects_wasmchecker_could_not_build} executable tests")
print(f"WasmChecker reported {test_df['FP'].sum()} false positive alarms and {total_discripancies - test_df['FP'].sum()} true discrepancies")

print(f"{green_text}{(N+2) * '@'}{reset_text}\n")

total_discripancies = 0
projects_without_tests_discrepancies = 0
projects_with_tests_discrepancies = 0
total_projects_wasmchecker_could_build = 0
wasmchecker_results = test_df[test_df['emcc build in wasm'] == "Yes"]['Can WasmChecker build the project? what is the result of differential testing?'].tolist()
print("Total number of projects in test dataset, compiled both manually and by WasmChecker:", len(wasmchecker_results))
for res in wasmchecker_results:
    build_ = res.split('-')[0].strip()
    if build_ == "Y": total_projects_wasmchecker_could_build += 1
    result = res.split('-')[1].strip()
    pattern = r'(\d+) failed in wasm'
    match_str = re.match(pattern, result)
    if match_str:
        X = match_str.group(1)
        total_discripancies = total_discripancies + int(X)
        projects_with_tests_discrepancies += 1
    elif result == "0 discrepancies":
        projects_without_tests_discrepancies += 1
    elif build_ != "N": 
        print(f"{red_text}input string is not a valid discripancy {result}{reset_text}")

print("Total number of discripancies reported by WasmChecker:", total_discripancies)
print(f"WasmChecker reported {total_discripancies} discrepancies across {projects_with_tests_discrepancies} projects")
print(f"WasmChecker reported no  discrepancies for {projects_without_tests_discrepancies} projects")
#print(f"WasmChecker reported {test_df['FP'].sum()} false positive alarms and {total_discripancies - test_df['FP'].sum()} true discrepancies")

print(f"{green_text}{(N+2) * '@'}{reset_text}\n")

total_discripancies = 0
projects_without_tests_discrepancies = 0
projects_with_tests_discrepancies = 0
total_projects_wasmchecker_could_build = 0
wasmchecker_results = test_df[(test_df['emcc build in wasm'] == "Build error") & (test_df['Can WasmChecker build the project? what is the result of differential testing?'].str.startswith('Y'))]['Can WasmChecker build the project? what is the result of differential testing?'].tolist()
print("Total number of projects in test dataset, compilable only by WasmChecker:", len(wasmchecker_results))
for res in wasmchecker_results:
    build_ = res.split('-')[0].strip()
    if build_ == "Y": total_projects_wasmchecker_could_build += 1
    result = res.split('-')[1].strip()
    pattern = r'(\d+) failed in wasm'
    match_str = re.match(pattern, result)
    if match_str:
        X = match_str.group(1)
        total_discripancies = total_discripancies + int(X)
        projects_with_tests_discrepancies += 1
    elif result == "0 discrepancies":
        projects_without_tests_discrepancies += 1
    elif build_ != "N": 
        print(f"{red_text}input string is not a valid discripancy {result}{reset_text}")

print("Total number of discripancies reported by WasmChecker:", total_discripancies)
print(f"WasmChecker reported {total_discripancies} discrepancies across {projects_with_tests_discrepancies} projects")
print(f"WasmChecker reported no  discrepancies for {projects_without_tests_discrepancies} projects")
#print(f"WasmChecker reported {test_df['FP'].sum()} false positive alarms and {total_discripancies - test_df['FP'].sum()} true discrepancies")

print(f"{green_text}{(N+2) * '@'}{reset_text}\n")

print("=" * ((N - len("RQ2"))//2), f"{red_text}RQ2{reset_text}", "=" * ((N - len("RQ2"))//2))
print(my_dict)
print(f"{green_text}{(N+2) * '@'}{reset_text}\n")

print("=" * ((N - len("RQ2"))//2), f"{red_text}RQ2{reset_text}", "=" * ((N - len("RQ2"))//2))
print(my_dict_test)
print(f"{green_text}{(N+2) * '@'}{reset_text}\n")
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

print(f"Overall, we evaluated WasmChecker on {len(df) + len(test_df)} projects with {df['#test cases'].sum() + test_df['#test cases'].sum()} test cases and {df['#executable tests'].sum() + test_df['#executable tests'].sum()} executable tests")

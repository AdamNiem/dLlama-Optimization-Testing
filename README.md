# dLlama-Optimization-Testing
For SBCC26 competition, detailing how we plan to benchmark dLlama for task3:

## What we tried, what worked and what failed
We initially had larger plans for the more optimization heavvy task 3, however, our approaches to improving the model and our limited time did not prove fruitful. For example initially thought of including GPUs in our cluster for their excellent matrix multiply performance over CPUs (crucial for llms like Llama). However we deemed that we did not have enough time nor were we sure the time and effort would be worth the inclusion of gpus which may have hurt performance potentially by the synchronous vulkan backend the library uses.

We also tried exploring ai agent in the loop optimizations such as with the tool Codex by OpenAI. However we found it to overcomplicate the codebase and make it difficult to verify improvements without a fast and iterable benchmark system written besides the library. We considered going down this route further but figured that we did not have enough time.

# Potential Optimization
Although most of our explorations in improving DLlama were not fruitful, we did notice a github issue mentioning the removal of the words 'batchSize == 1u || ' from the nn-cpu-ops.cpp file brought roughly 50% performance gain so we consider exploring this for task 3 although this is such a minor change that we did not include the code with this modification here.

# Run Scripts
As for running we plan to either manually adjust the parameters in the dllama inference command as well as the dllama workers command. We also may refer to our parameter sweep python script included in this repo if time is permitting.

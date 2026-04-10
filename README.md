# dLlama-Optimization-Testing
For SBCC26 competition, detailing how we plan to benchmark dLlama for task3:

## What we tried, what worked and what failed
We initially had larger plans for the more optimization heavvy task 3, however, our approaches to improving the model and our limited time did not prove fruitful. For example initially thought of including GPUs in our cluster for their excellent matrix multiply performance over CPUs (crucial for llms like Llama). However we deemed that we did not have enough time nor were we sure the time and effort would be worth the inclusion of gpus which may have hurt performance potentially by the synchronous vulkan backend the library uses.

We also tried exploring ai agent in the loop optimizations such as with the tool Codex by OpenAI. However we found it to overcomplicate the codebase and make it difficult to verify improvements without a fast and iterable benchmark system written besides the library. We considered going down this route further but figured that we did not have enough time.

# Import the torch module
import sys
import torch

# Define a function to get the name and compute capability of a GPU
def get_gpu_info(gpu_id):
    # Get the device object from the GPU id
    # device = torch.device(f"cuda:{gpu_id}")
    
    # Get the name of the GPU
    gpu_name = torch.cuda.get_device_name(gpu_id)
    
    # Get the compute capability of the GPU
    gpu_compute_capability_tuple = torch.cuda.get_device_capability(gpu_id)

    # Convert the tuple into a float by adding the major version and the minor version divided by 10
    gpu_compute_capability_float = gpu_compute_capability_tuple[0] + gpu_compute_capability_tuple[1] / 10
    
    # Return the name and compute capability of the GPU
    return gpu_name, gpu_compute_capability_float

def get_accelerated_hardware_capability():
    print("Accelerated hardware capabilities:")
    # Get the number of available GPUs
    num_gpus = torch.cuda.device_count()
    # Loop over the GPU ids
    for gpu_id in range(num_gpus):
        # Call the function and print the result
        gpu_name, gpu_compute_capability = get_gpu_info(gpu_id)
        print(f"{gpu_name}: {gpu_compute_capability}")

def main():
    print(f"{torch.__version__=}")
    print(f"{torch.cuda.is_available()=}")
    print(f"{torch.cuda.device_count()=}")
    print(f"{torch.cuda.get_device_name()=}")
    get_accelerated_hardware_capability()
    return 0

if __name__ == "__main__":
    sys.exit(main())
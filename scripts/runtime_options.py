"""Shared hardware options for training and IG; no model changes."""
import argparse


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def nonnegative_int(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return number


def add_runtime_arguments(parser):
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--precision", choices=["auto", "fp32", "bf16"], default="auto",
                        help="auto uses BF16 on supported CUDA GPUs, otherwise FP32. IG attribution itself uses FP32.")
    parser.add_argument("--torch-threads", type=positive_int, default=None,
                        help="CPU computation threads; omitted leaves PyTorch's default.")


def resolve_runtime(args):
    import torch
    device_name = args.device
    if device_name == "auto":
        device_name = "cuda" if torch.cuda.is_available() else "cpu"
    if device_name == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA is unavailable; use --device cpu or install a compatible CUDA environment.")
    bf16_supported = device_name == "cuda" and torch.cuda.is_bf16_supported()
    if args.precision == "bf16" and not bf16_supported:
        raise ValueError("BF16 requires a supported CUDA GPU; use --precision fp32 or auto.")
    use_amp = bf16_supported and args.precision != "fp32"
    if args.torch_threads is not None:
        torch.set_num_threads(args.torch_threads)
    print(f"Device: {device_name}; forward precision: {'bf16' if use_amp else 'fp32'}")
    return torch.device(device_name), use_amp

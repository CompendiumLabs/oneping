# llm servers

from itertools import chain
import subprocess

def start(model, n_gpu_layers=-1, **kwargs):
    args = chain(*[(f'--{k}', str(v)) for k, v in kwargs.items()])
    opts = ['--model', model, '--n_gpu_layers', n_gpu_layers, *args]
    cmds = ['python', '-m', 'llama_cpp.server', *opts]
    subprocess.run([str(x) for x in cmds])

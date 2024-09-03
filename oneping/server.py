# llm servers

import subprocess

def run_llama_server(model, n_gpu_layers=-1, *args):
    opts = ['--model', model, '--n_gpu_layers', n_gpu_layers, *args]
    cmds = ['python', '-m', 'llama_cpp.server', *opts]
    subprocess.run([str(x) for x in cmds])

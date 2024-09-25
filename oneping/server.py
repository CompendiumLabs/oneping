# llm servers

import subprocess

def run_llama_server(model, n_gpu_layers=-1, **kwargs):
    args = [(k, str(v)) for k, v in kwargs.items()]
    opts = ['--model', model, '--n_gpu_layers', n_gpu_layers, *args]
    cmds = ['python', '-m', 'llama_cpp.server', *opts]
    subprocess.run([str(x) for x in cmds])

if __name__ == '__main__':
    import fire
    fire.Fire(run_llama_server)

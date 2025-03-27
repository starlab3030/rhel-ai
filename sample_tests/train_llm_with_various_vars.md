# LLM 훈련 및 테스트

## 1. LLM 훈련을 위한 설정 값 변경

### 1.1 Epoch 변경

#### 1.1.1 모델 훈련 설정 확인

실행 명령어
```bash
yq '.train' ~/.config/instructlab/config.yaml
```

실행 결과
```json
{
  "additional_args": {
    "learning_rate": 0.000006,
    "lora_alpha": 32,
    "lora_dropout": 0.1,
    "warmup_steps": 25,
    "use_dolomite": true
  },
  "checkpoint_at_epoch": true,
  "ckpt_output_dir": "/root/.local/share/instructlab/checkpoints",
  "data_output_dir": "/root/.local/share/instructlab/internal",
  "data_path": "/root/.local/share/instructlab/datasets",
  "deepspeed_cpu_offload_optimizer": false,
  "device": "cuda",
  "disable_flash_attn": false,
  "distributed_backend": "fsdp",
  "effective_batch_size": 128,
  "fsdp_cpu_offload_optimizer": false,
  "is_padding_free": false,
  "lora_quantize_dtype": null,
  "lora_rank": 0,
  "max_batch_len": 60000,
  "max_seq_len": 10000,
  "model_path": "/root/.cache/instructlab/models/granite-3.1-8b-starter-v1",
  "nproc_per_node": 8,
  "num_epochs": 8,
  "phased_base_dir": "/root/.local/share/instructlab/phased",
  "phased_mt_bench_judge": "/root/.cache/instructlab/models/prometheus-8x7b-v2-0",
  "phased_phase1_effective_batch_size": 128,
  "phased_phase1_learning_rate": 0.00002,
  "phased_phase1_num_epochs": 7,
  "phased_phase1_samples_per_save": 0,
  "phased_phase2_effective_batch_size": 3840,
  "phased_phase2_learning_rate": 0.000006,
  "phased_phase2_num_epochs": 1,
  "phased_phase2_samples_per_save": 0,
  "pipeline": "accelerated",
  "save_samples": 0,
  "training_journal": null
}
```
* *train.num_epochs*: 8
* *train.phased_phase1_num_epochs*: 7
* *train.phased_phase2_num_epochs*: 1

#### 1.1.2 Phased 디렉터리 확인

실행 명령어
```bash
cd ~/phased
tree -F -sh -L 4
```

실행 결과
```log
[root@rhel_ai phased]# tree -F -sh -L 4
.
├── [ 1.4K]  journalfile.yaml
├── [   55]  phase1/
│   ├── [  139]  checkpoints/
│   │   ├── [ 128K]  full_logs_global0.log
│   │   ├── [  143]  full_state/
│   │   │   ├── [ 4.0K]  epoch_0/
│   │   │   ├── [ 4.0K]  epoch_1/
│   │   │   ├── [ 4.0K]  epoch_2/
│   │   │   ├── [ 4.0K]  epoch_3/
│   │   │   ├── [ 4.0K]  epoch_4/
│   │   │   ├── [ 4.0K]  epoch_5/
│   │   │   └── [ 4.0K]  epoch_6/
│   │   ├── [  177]  hf_format/
│   │   │   ├── [ 4.0K]  samples_1261/
│   │   │   ├── [ 4.0K]  samples_1892/
│   │   │   ├── [ 4.0K]  samples_2524/
│   │   │   ├── [ 4.0K]  samples_3156/
│   │   │   ├── [ 4.0K]  samples_3789/
│   │   │   ├── [ 4.0K]  samples_4421/
│   │   │   └── [ 4.0K]  samples_630/
│   │   └── [  14K]  training_params_and_metrics_global0.jsonl
│   └── [   10]  eval_cache/
└── [   55]  phase2/
    ├── [  139]  checkpoints/
    │   ├── [ 1.9M]  full_logs_global0.log
    │   ├── [   29]  full_state/
    │   │   └── [ 4.0K]  epoch_0/
    │   ├── [   36]  hf_format/
    │   │   └── [ 4.0K]  samples_356641/
    │   └── [ 342K]  training_params_and_metrics_global0.jsonl
    └── [   30]  eval_cache/
        └── [   60]  mt_bench/
            ├── [   42]  model_answer/
            └── [   55]  model_judgment/

29 directories, 5 files

[root@rhel_ai phased]# 
```

#### 1.1.3 Phase1의 epoch 디렉터리 확인

실행 명령어
```bash
ls -lh phase1/checkpoints/full_state/
```

실행 결과
```
[root@rhel_ai phased]# ls -lh phase1/checkpoints/full_state/
total 28K
drwxr-xr-x. 2 root root 4.0K Mar 27 14:12 epoch_0
drwxr-xr-x. 2 root root 4.0K Mar 27 14:14 epoch_1
drwxr-xr-x. 2 root root 4.0K Mar 27 14:16 epoch_2
drwxr-xr-x. 2 root root 4.0K Mar 27 14:18 epoch_3
drwxr-xr-x. 2 root root 4.0K Mar 27 14:19 epoch_4
drwxr-xr-x. 2 root root 4.0K Mar 27 14:21 epoch_5
drwxr-xr-x. 2 root root 4.0K Mar 27 14:23 epoch_6

[root@rhel_ai phased]# 
```
* 총 7개의 epoch 실행

#### 1.1.4 Phase2의 epoch 디렉터리 확인

실행 명령어
```bash
ls -lh phase2/checkpoints/full_state/
```

실행 결과
```
[root@rhel_ai phased]# ls -lh phase2/checkpoints/full_state/
total 4.0K
drwxr-xr-x. 2 root root 4.0K Mar 27 17:48 epoch_0

[root@rhel_ai phased]#
```
* 총 1개의 epoch 실행

#### 1.1.5 모델 훈련 결과 확인

실행 명령어
```bash
yq '.' journalfile.yaml 
```

실행 결과
```json
{
  "current_phase": "done",
  "ended_at_utc": "2025-03-27 17:53:37.017614+00:00",
  "eval_1": null,
  "eval_2": {
    "best_checkpoint": {
      "checkpoint": "/root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_356641",
      "ended_at_utc": "2025-03-27 17:53:37.011598+00:00",
      "score": 7.103225806451613
    },
    "checkpoints": [
      "/root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_356641"
    ],
    "ended_at_utc": "2025-03-27 17:53:37.017591+00:00",
    "finished_checkpoints": [
      "/root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_356641"
    ],
    "results": [
      {
        "checkpoint": "/root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_356641",
        "ended_at_utc": "2025-03-27 17:53:37.011598+00:00",
        "score": 7.103225806451613
      }
    ],
    "started_at_utc": "2025-03-27 17:48:40.834251+00:00"
  },
  "final_output": {
    "checkpoint": "/root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_356641",
    "ended_at_utc": "2025-03-27 17:53:37.011598+00:00",
    "score": 7.103225806451613
  },
  "run_id": "3b64a8e3-dbec-4a2f-aad9-201678c95ece",
  "started_at_utc": "2025-03-27 14:09:09.028101+00:00",
  "train_1": {
    "checkpoints": "/root/.local/share/instructlab/phased/phase1/checkpoints",
    "ended_at_utc": "2025-03-27 14:23:39.837102+00:00",
    "started_at_utc": "2025-03-27 14:09:09.033005+00:00"
  },
  "train_2": {
    "checkpoints": "/root/.local/share/instructlab/phased/phase2/checkpoints",
    "ended_at_utc": "2025-03-27 17:48:40.786801+00:00",
    "started_at_utc": "2025-03-27 14:23:39.911178+00:00"
  }
}
```
* Phase1은 14분 30초
* Phase2는 3시간 25분 01초
<br>

### 1.2 훈련 결과 확인

#### 1.2.1 모델 서비스

실행 명령어
```
ilab model serve --model-path ~/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_356641
```

실행 결과
```
[root@rhel_ai ~]# ilab model serve --model-path ~/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_356641
INFO 2025-03-27 19:54:30,547 instructlab.model.serve_backend:54: Setting backend_type in the serve config to vllm
INFO 2025-03-27 19:54:30,560 instructlab.model.serve_backend:60: Using model '/root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_356641' with -1 gpu-layers and 4096 max context size.
INFO 2025-03-27 19:54:30,560 instructlab.model.serve_backend:92: '--gpus' flag used alongside '--tensor-parallel-size' in the vllm_args section of the config file. Using value of the --gpus flag.
INFO 2025-03-27 19:54:30,656 instructlab.model.backends.vllm:332: vLLM starting up on pid 75 at http://127.0.0.1:8000/v1
INFO 03-27 19:54:39 api_server.py:585] vLLM API server version 0.6.4.post1

...<snip>...

^C^CINFO 2025-03-27 20:01:31,931 instructlab.model.backends.vllm:85: vLLM server terminated by keyboard
INFO 03-27 20:01:31 launcher.py:57] Shutting down FastAPI HTTP server.
INFO 03-27 20:01:31 multiproc_worker_utils.py:133] Terminating local vLLM worker processes
(VllmWorkerProcess pid=218) INFO 03-27 20:01:31 multiproc_worker_utils.py:240] Worker exiting
(VllmWorkerProcess pid=217) INFO 03-27 20:01:31 multiproc_worker_utils.py:240] Worker exiting
(VllmWorkerProcess pid=222) INFO 03-27 20:01:31 multiproc_worker_utils.py:240] Worker exiting
(VllmWorkerProcess pid=220) INFO 03-27 20:01:31 multiproc_worker_utils.py:240] Worker exiting
(VllmWorkerProcess pid=219) INFO 03-27 20:01:31 multiproc_worker_utils.py:240] Worker exiting
(VllmWorkerProcess pid=223) INFO 03-27 20:01:31 multiproc_worker_utils.py:240] Worker exiting
(VllmWorkerProcess pid=221) INFO 03-27 20:01:31 multiproc_worker_utils.py:240] Worker exiting
^CINFO 2025-03-27 20:01:32,405 instructlab.model.serve_backend:121: Server terminated by keyboard
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
/usr/lib64/python3.11/multiprocessing/resource_tracker.py:254: UserWarning: resource_tracker: There appear to be 1 leaked shared_memory objects to clean up at shutdown
  warnings.warn('resource_tracker: There appear to be %d '
INFO 2025-03-27 20:01:43,242 instructlab.model.backends.vllm:494: Waiting for GPU VRAM reclamation...

[root@rhel_ai ~]#
```

#### 1.2.2 모델과 채팅

실행 명령어
```
ilab model chat
```

실행 결과
```
[root@rhel_ai ~]# ilab model chat
INFO 2025-03-27 19:55:55,448 instructlab.model.chat:775: Requested model /root/.cache/instructlab/models/granite-3.1-8b-lab-v1 is not served by the server. Proceeding to chat with served model: /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_356641
╭──────────────────────────────────────────────────────────────── system ────────────────────────────────────────────────────────────────╮
│ Welcome to InstructLab Chat w/ SAMPLES_356641 (type /h for help)                                                                       │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
>>> 휴가 포상은?                                                                                                              [S][default]
╭──────────────────────────────────────────────────────────── samples_356641 ────────────────────────────────────────────────────────────╮
│ 휴가 포상은 직원의 노력과 성과를 인정하고 정규직 또는 계약직 직원에게 제공됩니다.                                                      │
│                                                                                                                                        │
│                                                                                                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────── elapsed 0.179 seconds ─╯
>>> 가족 행사 비용은 있나요?                                                                                                  [S][default]
╭──────────────────────────────────────────────────────────── samples_356641 ────────────────────────────────────────────────────────────╮
│ 최대 20만원(비과세)이 지급됩니다. 이는 직원의 가족 구성원들이 참석하는 가족 행사에 대한 지원금입니다.                                  │
│                                                                                                                                        │
│                                                                                                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────── elapsed 0.245 seconds ─╯
>>> 몸이 아파요?                                                                                                              [S][default]
╭──────────────────────────────────────────────────────────── samples_356641 ────────────────────────────────────────────────────────────╮
│ 3일~ consumption가 상한정도로 휴가 요약을 통해 의료 휴가를 유급합니다.                                                                 │
│                                                                                                                                        │
│                                                                                                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────── elapsed 0.149 seconds ─╯
>>> 레드햇의 직원은 몇 명인가요?                                                                                              [S][default]
╭──────────────────────────────────────────────────────────── samples_356641 ────────────────────────────────────────────────────────────╮
│ 레드햇은 16만여명의 직원들을 충분히 관리하는 첫 직원과 새로운 직원들에게 동등한 기회를 제공하려고 노력합니다.                          │
│                                                                                                                                        │
│                                                                                                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────── elapsed 0.251 seconds ─╯
>>> 사내 교육 제도가 있나요?                                                                                                  [S][default]
╭──────────────────────────────────────────────────────────── samples_356641 ────────────────────────────────────────────────────────────╮
│ 예, 레드햇은 직원의 성과 및 개발 계획을 지원하는 다양한 교육 기회를 제공합니다. 직원은 직원 디자인 플랜을 통해 성과계획을 기술하는     │
│ 다른 직원에게 구애없이 교육을 요구할 수 있습니다.                                                                                      │
│                                                                                                                                        │
│                                                                                                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────── elapsed 0.432 seconds ─╯
>>> exit                                                                                                                      [S][default]

[root@rhel_ai ~]#
```
<br>

### 1.3 GPU 수 변경

#### 1.3.1 모델 훈련

실행 명령어
```bash
ilab model train --strategy lab-multiphase --phased-phase1-data /root/.local/share/instructlab/datasets/2025-03-27_133844/knowledge_train_msgs_2025-03-27T13_40_10.jsonl --phased-phase2-data /root/.local/share/instructlab/datasets/2025-03-27_133844/skills_train_msgs_2025-03-27T13_40_10.jsonl --model-path /root/.local/share/instructlab/phased.second/phase2/checkpoints/hf_format/samples_356641 --gpus 4
```

실행 결과
```
[root@rhel_ai ~]# ilab model train --strategy lab-multiphase --phased-phase1-data /root/.local/share/instructlab/datasets/2025-03-27_133844/knowledge_train_msgs_2025-03-27T13_40_10.jsonl --phased-phase2-data /root/.local/share/instructlab/datasets/2025-03-27_133844/skills_train_msgs_2025-03-27T13_40_10.jsonl --model-path /root/.local/share/instructlab/phased.second/phase2/checkpoints/hf_format/samples_356641 --gpus 4
LoRA is disabled (rank=0), ignoring all additional LoRA args

~~~~~~~~~~~~~STARTING MULTI-PHASE TRAINING~~~~~~~~~~~~~
No training journal found. Will initialize at: '/root/.local/share/instructlab/phased/journalfile.yaml'
Metadata (checkpoints, the training journal) may have been saved from a previous training run.
By default, training will resume from this metadata if it exists.
Alternatively, the metadata can be cleared, and training can start from scratch.

Would you like to START TRAINING FROM THE BEGINNING?
'y' clears metadata to start new training, 'N' tries to resume:  [y/N]: y


[root@rhel_ai ~]#
```

#### 1.3.2 GPU 사용량 확인

실행 명령어
```bash
nvidia-smi 
```

실행 결과
```
[root@rhel_ai ~]# nvidia-smi 
Thu Mar 27 20:16:42 2025       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.144.03             Driver Version: 550.144.03     CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA H100 80GB HBM3          On  |   00000000:0D:00.0 Off |                    0 |
| N/A   41C    P0            565W /  700W |   21650MiB /  81559MiB |     90%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
|   1  NVIDIA H100 80GB HBM3          On  |   00000000:0E:00.0 Off |                    0 |
| N/A   46C    P0            544W /  700W |   22080MiB /  81559MiB |     55%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
|   2  NVIDIA H100 80GB HBM3          On  |   00000000:0F:00.0 Off |                    0 |
| N/A   50C    P0            543W /  700W |   22736MiB /  81559MiB |     46%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
|   3  NVIDIA H100 80GB HBM3          On  |   00000000:10:00.0 Off |                    0 |
| N/A   49C    P0            528W /  700W |   22778MiB /  81559MiB |     60%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
|   4  NVIDIA H100 80GB HBM3          On  |   00000000:11:00.0 Off |                    0 |
| N/A   27C    P0             70W /  700W |       4MiB /  81559MiB |      0%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
|   5  NVIDIA H100 80GB HBM3          On  |   00000000:12:00.0 Off |                    0 |
| N/A   26C    P0             70W /  700W |       4MiB /  81559MiB |      0%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
|   6  NVIDIA H100 80GB HBM3          On  |   00000000:13:00.0 Off |                    0 |
| N/A   29C    P0             68W /  700W |       4MiB /  81559MiB |      0%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
|   7  NVIDIA H100 80GB HBM3          On  |   00000000:14:00.0 Off |                    0 |
| N/A   30C    P0             71W /  700W |       4MiB /  81559MiB |      0%      Default |
|                                         |                        |             Disabled |
+-----------------------------------------+------------------------+----------------------+
                                                                                         
+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    0   N/A  N/A   3318163      C   /opt/app-root/bin/python3.11                24688MiB |
|    1   N/A  N/A   3318164      C   /opt/app-root/bin/python3.11                24738MiB |
|    2   N/A  N/A   3318165      C   /opt/app-root/bin/python3.11                25774MiB |
|    3   N/A  N/A   3318166      C   /opt/app-root/bin/python3.11                25422MiB |
+-----------------------------------------------------------------------------------------+

[root@rhel_ai ~]#
```
<br>




<br>
<br>

실행 명령어
```bash

```

실행 결과
```

```

<br>
<br>

------
[차례](../README.md)


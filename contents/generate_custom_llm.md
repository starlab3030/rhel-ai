# RHEL AI를 사용하여 커스텀 LLM 생성

1. [SDG로 새 데이터 세트 생성](generate_custom_llm.md#1-sdg로-새-데이터-세트-생성)<br>
2. [모델 학습](generate_custom_llm.md#2-모델-학습)<br>
3. [모델 평가](generate_custom_llm.md#3-모델-평가)<br>
4. [새 모델 제공 및 채팅](generate_custom_llm.md#4-새-모델-제공-및-채팅)<br>
<br>
<br>

## 1. SDG로 새 데이터 세트 생성

택소노미 트리를 사용자 지정한 후 RHEL AI에서 SDG(Synthetic Data Generation) 프로세스를 사용하여 합성 데이터 세트를 생성할 수 있습니다.
* SDG는 제공된 예를 기반으로 실제 데이터를 모방하는 인공적으로 생성된 데이터 세트를 만드는 프로세스
* SDG는 질문과 답변 쌍을 포함하는 YAML 파일을 입력 데이터로 사용
* SDG는 *mixtral-8x7b-instruct-v0-1* LLM을 교사 모델로 사용하여 유사한 질문과 답변 쌍을 생성
* SDG 파이프라인에서 많은 질문이 품질에 따라 생성되고 점수가 매겨지며, *mixtral-8x7b-instruct-v0-1* 교사 모델은 질문의 관련성과 일관성을 평가
* 그런 다음 파이프라인은 필터링 메커니즘을 적용하여 가장 높은 점수를 받은 질문을 선택
  + 해당 답변을 생성한 다음 원래 예제 질문을 기반으로 정확도를 추가로 평가
  + 그런 다음 최종 고품질 질문과 답변 쌍 세트가 훈련에 사용되는 합성 데이터 세트에 포함

### 1.1 사전 준비 사항

* RHEL AI 노드 준비
* 지식 데이터를 가진 커스텀 *qna.yaml* 파일 생성
* 이미지 준비
  + SDG를 위한 교사 모델로 *mixtral-8x7b-instruct-v0-1* 다운로드
  + LoRA 계층화된 기술 및 지식 어댑터 용 이미지 다운로드
    - *skills-adapter-v3:1.4*
    - *knowledge-adapter-v3:1.4*
<br>

**InstructLab의 합성 데이터 모델 구성**
```bash
yq '.generate' .config/instructlab/config.yaml
```

실행 결과
```json
{
  "chunk_word_count": 1000,
  "max_num_tokens": 4096,
  "model": "/var/home/instruct/.cache/instructlab/models/mixtral-8x7b-instruct-v0-1",
  "num_cpus": 10,
  "num_instructions": -1,
  "output_dir": "/var/home/instruct/.local/share/instructlab/datasets",
  "pipeline": "/usr/share/instructlab/sdg/pipelines/agentic",
  "sdg_scale_factor": 30,
  "seed_file": "/var/home/instruct/.local/share/instructlab/internal/seed_tasks.json",
  "taxonomy_base": "empty",
  "taxonomy_path": "/var/home/instruct/.local/share/instructlab/taxonomy",
  "teacher": {
    "backend": "vllm",
    "chat_template": "tokenizer",
    "llama_cpp": {
      "gpu_layers": -1,
      "llm_family": "",
      "max_ctx_size": 4096
    },
    "model_path": "/var/home/instruct/.cache/instructlab/models/mixtral-8x7b-instruct-v0-1",
    "server": {
      "backend_type": "",
      "current_max_ctx_size": 4096,
      "host": "127.0.0.1",
      "port": 8000
    },
    "vllm": {
      "gpus": 4,
      "llm_family": "mixtral",
      "max_startup_attempts": 120,
      "vllm_args": [
        "--enable-lora",
        "--max-lora-rank",
        "64",
        "--dtype",
        "bfloat16",
        "--lora-dtype",
        "bfloat16",
        "--fully-sharded-loras",
        "--lora-modules",
        "skill-classifier-v3-clm=/var/home/instruct/.cache/instructlab/models/skills-adapter-v3",
        "text-classifier-knowledge-v3-clm=/var/home/instruct/.cache/instructlab/models/knowledge-adapter-v3"
      ]
    }
  }
}
```

### 1.2 예제를 사용하여 합성 데이터 세트를 생성

#### 1.2.1 합성 데이터 세트 생성

지식을 기반으로 사용자 정의 분류법을 기반으로 새로운 합성 데이터 세트를 생성
```bash
ilab data generate
```
* *--enable-serving-output*: vLLM 시작 로그를 표시

#### 1.2.2 vLLM 서버 시작

SDG 프로세스가 시작될 때 vLLM은 *mixtral-8x7B-instruct* 교사 모델을 호스팅하는 서버를 시작하려고 시도

예) vLLM이 서버를 시작 로그
```log
Starting a temporary vLLM server at http://127.0.0.1:47825/v1
INFO 2024-08-22 17:01:09,461 instructlab.model.backends.backends:480: Waiting for the vLLM server to start at http://127.0.0.1:47825/v1, this might take a moment... Attempt: 1/120
INFO 2024-08-22 17:01:14,213 instructlab.model.backends.backends:480: Waiting for the vLLM server to start at http://127.0.0.1:47825/v1, this might take a moment... Attempt: 2/120
```

#### 1.2.3 vLLM 서버 연결 및 SDG 생성

vLLM이 연결되면 SDG 프로세스는 *qna.yaml* 파일에 있는 시드 예제를 기반으로 합성 데이터를 생성하기 시작

예) vLLM 연결 및 SDG 생성 로그
```log
INFO 2024-08-22 15:16:43,497 instructlab.model.backends.backends:480: Waiting for the vLLM server to start at http://127.0.0.1:49311/v1, this might take a moment... Attempt: 74/120
INFO 2024-08-22 15:16:45,949 instructlab.model.backends.backends:487: vLLM engine successfully started at http://127.0.0.1:49311/v1
Generating synthetic data using '/usr/share/instructlab/sdg/pipelines/agentic' pipeline, '/var/home/cloud-user/.cache/instructlab/models/mixtral-8x7b-instruct-v0-1' model, '/var/home/cloud-user/.local/share/instructlab/taxonomy' taxonomy, against http://127.0.0.1:49311/v1 server
INFO 2024-08-22 15:16:46,594 instructlab.sdg:375: Synthesizing new instructions. If you aren't satisfied with the generated instructions, interrupt training (Ctrl-C) and try adjusting your YAML files. Adding more examples may help.
```

#### 1.2.4 CLI에 새 데이터 세트의 위치가 표시되면 SDG 프로세스가 완료

예) 성공적인 SDG 실행
```log
INFO 2024-08-16 17:12:46,548 instructlab.sdg.datamixing:200: Mixed Dataset saved to /home/example-user/.local/share/instructlab/datasets/skills_train_msgs_2024-08-16T16_50_11.jsonl
INFO 2024-08-16 17:12:46,549 instructlab.sdg:438: Generation took 1355.74s
```
 
> [!NOTE] 
> 하드웨어 사양에 따라 시간이 많이 걸릴 수 있습니다.
<br>

### 1.3 생성된 SDG 파일 검증

#### 1.3.1 생성된 파일 확인

*~/.local/share/instructlab/datasets/* 디렉토리로 이동하여 데이터가 생성된 날짜에 해당하는 파일을 나열

실행 명령어
```bash
ls 2024-03-24_194933
```

실행 결과
```
knowledge_recipe_2024-03-24T20_54_21.yaml                   skills_recipe_2024-03-24T20_54_21.yaml
knowledge_train_msgs_2024-03-24T20_54_21.jsonl              skills_train_msgs_2024-03-24T20_54_21.jsonl
messages_granite-7b-lab-Q4_K_M_2024-03-24T20_54_21.jsonl    node_datasets_2024-03-24T15_12_12/
```

> [!IMPORTANT]
> 가장 최근의 *knowledge_train_msgs.jsonl* 및 *skills_train_msgs.jsonl* 파일을 기록해 두세요. 다중 단계 훈련 중에 이 파일을 지정해야 합니다. 각 JSONL에는 파일에 타임스탬프가 있습니다. (예: knowledge_train_msgs_2024-08-08T20_04_28.jsonl). 훈련 시 가장 최근 파일을 사용하세요.

#### 1.3.2 (옵션) JSONL 파일을 열어 SDG 출력을 확인

*~/.local/share/datasets/\<generation-date\>* 디렉토리로 이동하고 JSONL 파일을 열어 SDG 출력을 확인

실행 명령어
```bash
cat ~/.local/share/datasets/<generation-date>/<jsonl-dataset>
```

실행 결과
```
{"messages":[{"content":"I am, Red Hat\u00ae Instruct Model based on Granite 7B, an AI language model developed by Red Hat and IBM Research, based on the Granite-7b-base language model. My primary function is to be a chat assistant.","role":"system"},{"content":"<|user|>\n### Deep-sky objects\n\nThe constellation does not lie on the [galactic\nplane](galactic_plane \"wikilink\") of the Milky Way, and there are no\nprominent star clusters. [NGC 625](NGC_625 \"wikilink\") is a dwarf\n[irregular galaxy](irregular_galaxy \"wikilink\") of apparent magnitude\n11.0 and lying some 12.7 million light years distant.
Only 24000 light\nyears in diameter, it is an outlying member of the [Sculptor\nGroup](Sculptor_Group \"wikilink\"). NGC 625 is thought to have been\ninvolved in a collision and is experiencing a burst of [active star\nformation](Active_galactic_nucleus \"wikilink\"). [NGC\n37](NGC_37 \"wikilink\") is a [lenticular\ngalaxy](lenticular_galaxy \"wikilink\") of apparent magnitude 14.66. It is\napproximately 42 [kiloparsecs](kiloparsecs \"wikilink\") (137,000\n[light-years](light-years \"wikilink\")) in diameter and about 12.9\nbillion years old. [Robert's Quartet](Robert's_Quartet \"wikilink\")\n(composed of the
irregular galaxy [NGC 87](NGC_87 \"wikilink\"), and three\nspiral galaxies [NGC 88](NGC_88 \"wikilink\"), [NGC 89](NGC_89 \"wikilink\")\nand [NGC 92](NGC_92 \"wikilink\")) is a group of four galaxies located\naround 160 million light-years away which are in the process of\ncolliding and merging. They are within a circle of radius of 1.6 arcmin,\ncorresponding to about 75,000 light-years. Located in the galaxy ESO\n243-49 is [HLX-1](HLX-1 \"wikilink\"), an [intermediate-mass black\nhole](intermediate-mass_black_hole \"wikilink\")\u2014the first one of its kind\nidentified. It is thought to be a remnant of a dwarf
galaxy that was\nabsorbed in a [collision](Interacting_galaxy \"wikilink\") with ESO\n243-49. Before its discovery, this class of black hole was only\nhypothesized.\n\nLying within the bounds of the constellation is the gigantic [Phoenix\ncluster](Phoenix_cluster \"wikilink\"), which is around 7.3 million light\nyears wide and 5.7 billion light years away, making it one of the most\nmassive [galaxy clusters](galaxy_cluster \"wikilink\"). It was first\ndiscovered in 2010, and the central galaxy is producing an estimated 740\nnew stars a year. Larger still is [El\nGordo](El_Gordo_(galaxy_cluster) \"wikilink\"),
or officially ACT-CL\nJ0102-4915, whose discovery was announced in 2012.
```
<br>

### 1.4 백그라운드에서 SDG(Synthetic Data Generation) 실행

#### 1.4.1 백그라운드에서 SDG 프로세스를 시작

실행 명령어
```bash
ilab data generate -dt
```

실행 결과
```log
INFO 2025-01-15 11:36:47,557 instructlab.process.process:236: Started subprocess with PID 68289. Logs are being written to /Users/<user-name>/.local/share/instructlab/logs/generation/generation-e85623ac-d35e-11ef-bc70-2a1c6126d703.log.
```

#### 1.4.2 분리된 SDG 프로세스를 관리, 보고, 상호 작용

실행 명령어 - 실행 중인 모든 프로세스 및 상태 확인
```bash
ilab process list
```

실행 결과
```
+------------+-------+--------------------------------------+----------------------------------------------------------------------------------------------------------------+----------+---------+
| Type       | PID   | UUID                                 | Log File                                                                                                       | Runtime  | Status  |
+------------+-------+--------------------------------------+----------------------------------------------------------------------------------------------------------------+----------+---------+
| Generation | 30334 | f2623406-de55-11ef-b684-2a1c6126d703 | /Users/<user-name>/.local/share/instructlab/logs/generation/generation-f2623406-de55-11ef-b684-2a1c6126d703.log| 00:08:30 | Running |
+------------+-------+--------------------------------------+----------------------------------------------------------------------------------------------------------------+----------+---------+
```

실행 명령어 - 가장 최신의 프로세스에 참여
```bash
ilab process attach --latest
```
* 한 번 *attach*하면 *dettach*할 수 없음
<br>
<br>

## 2. 모델 훈련

### 2.1 새로 학습된 모델

RHEL AI는 택소노미 트리와 합성 데이터를 사용하여 다중 단계 학습 및 평가를 통해 도메인별 지식 또는 기술로 새로 학습된 모델을 만들 수 있습니다.

* 생성한 합성 데이터 세트를 사용하여 전체 학습 및 평가 프로세스를 실행 가능
* 다중 단계 학습의 LAB 최적화 기술은 여러 단계의 학습 및 평가를 거치는 LLM 학습 유형
  + 다양한 단계에서 RHEL AI는 학습 프로세스를 실행하고 모델 체크포인트를 생성
  + 다음 단계에 가장 적합한 체크포인트를 선택
  + 이 프로세스는 여러 체크포인트를 생성하고 가장 높은 점수를 받은 체크포인트를 선택
  + 이 가장 높은 점수를 받은 체크포인트가 새로 학습된 LLM

전체 프로세스는 택소노미 트리의 합성 데이터를 사용하여 학습 및 평가되는 새로 생성된 모델을 생성합니다.

**InstructLab의 훈련 모델 구성**
```bash
yq '.train' .config/instructlab/config.yaml
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
  "ckpt_output_dir": "/var/home/instruct/.local/share/instructlab/checkpoints",
  "data_output_dir": "/var/home/instruct/.local/share/instructlab/internal",
  "data_path": "/var/home/instruct/.local/share/instructlab/datasets",
  "deepspeed_cpu_offload_optimizer": false,
  "device": "cuda",
  "disable_flash_attn": false,
  "distributed_backend": "fsdp",
  "effective_batch_size": 128,
  "fsdp_cpu_offload_optimizer": false,
  "is_padding_free": false,
  "lora_quantize_dtype": null,
  "lora_rank": 0,
  "max_batch_len": 10000,
  "max_seq_len": 10000,
  "model_path": "/var/home/instruct/.cache/instructlab/models/granite-3.1-8b-starter-v1",
  "nproc_per_node": 4,
  "num_epochs": 4,
  "phased_base_dir": "/var/home/instruct/.local/share/instructlab/phased",
  "phased_mt_bench_judge": "/var/home/instruct/.cache/instructlab/models/prometheus-8x7b-v2-0",
  "phased_phase1_effective_batch_size": 128,
  "phased_phase1_learning_rate": 0.00002,
  "phased_phase1_num_epochs": 7,
  "phased_phase1_samples_per_save": 0,
  "phased_phase2_effective_batch_size": 3840,
  "phased_phase2_learning_rate": 0.000006,
  "phased_phase2_num_epochs": 10,
  "phased_phase2_samples_per_save": 0,
  "pipeline": "accelerated",
  "save_samples": 0,
  "training_journal": null
}
```
<br>

### 2.2 데이터로 모델 훈련하기

RHEL AI를 사용하여 합성적으로 생성된 데이터로 모델을 훈련할 수 있습니다. 

> [!IMPORTANT] 
> RHEL AI 일반 가용성은 동시에 학습과 추론 제공을 지원하지 않습니다. 추론 서버를 실행 중인 경우 학습 프로세스를 시작하기 전에 닫아야 합니다.


#### 2.2.1 사전 준비

* RHEL AI 노드
* *스타터* 모델인 *granite-3.1-8b-starter-v1* 이미지 다운로드
* 지식 데이터로 사용자 지정 *qna.yaml* 파일을 생성
* 합성 데이터 생성(SDG) 프로세스를 실행
* 판단 모델인 *prometheus-8x7b-v2-0* 이미지를 다운로드

#### 2.2.2 수행 절차

SDG에서 생성된 데이터 파일로 다음 명령을 실행하면 다단계 학습 및 평가를 실행할 수 있습니다.

실행 명령어
```bash
ilab model train --strategy lab-multiphase \
  --phased-phase1-data ~/.local/share/instructlab/datasets/<generation-date>/<knowledge-train-messages-jsonl-file> \
  --phased-phase2-data ~/.local/share/instructlab/datasets/<generation-date>/<skills-train-messages-jsonl-file>
```
* *ilab model train --enable-serving-output* 명령으로 학습 로그를 표시
* \<generation-date\>
  + 합성 데이터 생성(SDG)을 실행한 날짜
* \<knowledge-train-messages-file\>
  + Phase1은 지식 관련 훈련
  + SDG 중에 생성된 knowledge_messages.jsonl 파일의 위치
  + RHEL AI는 *.jsonl 파일의 데이터를 사용하여 학생 모델 *granite-3.1-8b-starter-v1*를 훈련
  + 경로 예
    ```
    ~/.local/share/instructlab/datasets/2024-09-07_194933/knowledge_train_msgs_2024-09-07T20_54_21.jsonl.
    ```
* \<skills-train-messages-file\>
  + Phase2는 기술 관련 훈련
  + SDG 중에 생성된 skills_messages.jsonl 파일의 위치
  + RHEL AI는 *.jsonl 파일의 데이터를 사용하여 학생 모델 *granite-3.1-8b-starter-v1*를 훈련
  + 경로 예
    ```
    ~/.local/share/instructlab/datasets/2024-09-07_194933/skills_train_msgs_2024-09-07T20_54_21.jsonl.
    ```

#### 2.2.3 기술에 대해서만 모델을 훈련하는 명령어

*--strategy lab-skills-only* 옵션으로 실행
```bash
ilab model train --strategy lab-skills-only --phased-phase2-data ~/.local/share/instructlab/datasets/<skills-train-messages-jsonl-file>
```

#### 2.2.4 모델 훈련 예

실행 명령어
```bash
ilab model train --strategy lab-multiphase --phased-phase1-data /root/.local/share/instructlab/datasets/2025-03-27_133844/knowledge_train_msgs_2025-03-27T13_40_10.jsonl --phased-phase2-data /root/.local/share/instructlab/datasets/2025-03-27_133844/skills_train_msgs_2025-03-27T13_40_10.jsonl --model-path /root/.local/share/instructlab/phased.first/phase2/checkpoints/hf_format/samples_1173515
```

실행 결과
```
[root@rhel_ai ~]# ps -ef | grep -v grep | grep ilab
root     3244897 2831062  0 14:08 pts/0    00:00:09 podman run --rm -it --device nvidia.com/gpu=all --security-opt label=disable --net host --shm-size 10G --pids-limit -1 -v /root:/root --env HF_TOKEN --env HOME --env NCCL_DEBUG --env VLLM_LOGGING_LEVEL --entrypoint ilab registry.redhat.io/rhelai1/instructlab-nvidia-rhel9:1.4.1-1739870750 model train --strategy lab-multiphase --phased-phase1-data /root/.local/share/instructlab/datasets/2025-03-27_133844/knowledge_train_msgs_2025-03-27T13_40_10.jsonl --phased-phase2-data /root/.local/share/instructlab/datasets/2025-03-27_133844/skills_train_msgs_2025-03-27T13_40_10.jsonl --model-path /root/.local/share/instructlab/phased.first/phase2/checkpoints/hf_format/samples_1173515

root     3244924 3244922  1 14:08 pts/0    00:02:23 /opt/app-root/bin/python3.11 /opt/app-root/bin/ilab model train --strategy lab-multiphase --phased-phase1-data /root/.local/share/instructlab/datasets/2025-03-27_133844/knowledge_train_msgs_2025-03-27T13_40_10.jsonl --phased-phase2-data /root/.local/share/instructlab/datasets/2025-03-27_133844/skills_train_msgs_2025-03-27T13_40_10.jsonl --model-path /root/.local/share/instructlab/phased.first/phase2/checkpoints/hf_format/samples_1173515

[root@rhel_ai ~]# pstree -ps -a 3244924
systemd,1 --switched-root --system --deserialize 31
  └─conmon,3244922 --api-version 1 -c 4ea65c26511aa04ff93ad564e540d1f5a21a13cf083dd1e62254806970bcc150 -u...
      └─ilab,3244924 /opt/app-root/bin/ilab model train --strategy lab-multiphase --phased-phase1-data/root/.local/share/instruct
          ├─pt_elastic,3281294 /opt/app-root/bin/torchrun --nnodes=1 --node_rank=0 --nproc_per_node=8 --rdzv_id=123...
          │   ├─python3.11,3281298 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   ├─pt_data_worker,3285117 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285813
          │   │   ├─pt_data_worker,3285264 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285815
          │   │   ├─pt_data_worker,3285363 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285814
          │   │   ├─pt_data_worker,3285364 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285816
          │   │   ├─pt_data_worker,3285490 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285819
          │   │   ├─pt_data_worker,3285492 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285817
          │   │   ├─pt_data_worker,3285620 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285818
          │   │   ├─pt_data_worker,3285684 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285820
          │   │   ├─{python3.11},3281328
          │   │   ├─{python3.11},3281516
          │   │   ├─{python3.11},3281528
          │   │   ├─{python3.11},3281529
          │   │   ├─{python3.11},3281530
          │   │   ├─{python3.11},3281531
          │   │   ├─{python3.11},3281536
          │   │   ├─{python3.11},3281577
          │   │   ├─{python3.11},3281579
          │   │   ├─{python3.11},3281592
          │   │   ├─{python3.11},3281612
          │   │   ├─{python3.11},3282160
          │   │   ├─{python3.11},3283220
          │   │   ├─{python3.11},3285805
          │   │   ├─{python3.11},3285806
          │   │   ├─{python3.11},3285807
          │   │   ├─{python3.11},3285808
          │   │   ├─{python3.11},3285809
          │   │   ├─{python3.11},3285810
          │   │   ├─{python3.11},3285811
          │   │   ├─{python3.11},3285812
          │   │   ├─{python3.11},3286348
          │   │   ├─{python3.11},3286350
          │   │   ├─{python3.11},3286351
          │   │   ├─{python3.11},3286353
          │   │   ├─{python3.11},3286354
          │   │   ├─{python3.11},3286365
          │   │   ├─{python3.11},3286367
          │   │   └─{python3.11},3286387
          │   ├─python3.11,3281299 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   ├─pt_data_worker,3283348 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285780
          │   │   ├─pt_data_worker,3283351 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285778
          │   │   ├─pt_data_worker,3283353 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285783
          │   │   ├─pt_data_worker,3283793 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285784
          │   │   ├─pt_data_worker,3283905 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285787
          │   │   ├─pt_data_worker,3284134 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285789
          │   │   ├─pt_data_worker,3284232 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285793
          │   │   ├─pt_data_worker,3284656 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285794
          │   │   ├─{python3.11},3281325
          │   │   ├─{python3.11},3281519
          │   │   ├─{python3.11},3281524
          │   │   ├─{python3.11},3281537
          │   │   ├─{python3.11},3281548
          │   │   ├─{python3.11},3281550
          │   │   ├─{python3.11},3281574
          │   │   ├─{python3.11},3281576
          │   │   ├─{python3.11},3281599
          │   │   ├─{python3.11},3281613
          │   │   ├─{python3.11},3282159
          │   │   ├─{python3.11},3285756
          │   │   ├─{python3.11},3285758
          │   │   ├─{python3.11},3285760
          │   │   ├─{python3.11},3285761
          │   │   ├─{python3.11},3285762
          │   │   ├─{python3.11},3285763
          │   │   ├─{python3.11},3285764
          │   │   ├─{python3.11},3285766
          │   │   ├─{python3.11},3286355
          │   │   ├─{python3.11},3286368
          │   │   ├─{python3.11},3286375
          │   │   ├─{python3.11},3286376
          │   │   ├─{python3.11},3286377
          │   │   ├─{python3.11},3286378
          │   │   ├─{python3.11},3286380
          │   │   └─{python3.11},3286381
          │   ├─python3.11,3281300 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   ├─pt_data_worker,3283221 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285772
          │   │   ├─pt_data_worker,3283347 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285773
          │   │   ├─pt_data_worker,3283350 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285775
          │   │   ├─pt_data_worker,3283354 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285776
          │   │   ├─pt_data_worker,3283872 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285774
          │   │   ├─pt_data_worker,3284104 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285785
          │   │   ├─pt_data_worker,3284231 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285777
          │   │   ├─pt_data_worker,3284531 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285796
          │   │   ├─{python3.11},3281324
          │   │   ├─{python3.11},3281514
          │   │   ├─{python3.11},3281522
          │   │   ├─{python3.11},3281535
          │   │   ├─{python3.11},3281543
          │   │   ├─{python3.11},3281545
          │   │   ├─{python3.11},3281581
          │   │   ├─{python3.11},3281583
          │   │   ├─{python3.11},3281596
          │   │   ├─{python3.11},3281611
          │   │   ├─{python3.11},3282161
          │   │   ├─{python3.11},3285694
          │   │   ├─{python3.11},3285703
          │   │   ├─{python3.11},3285707
          │   │   ├─{python3.11},3285720
          │   │   ├─{python3.11},3285734
          │   │   ├─{python3.11},3285755
          │   │   ├─{python3.11},3285757
          │   │   ├─{python3.11},3285759
          │   │   ├─{python3.11},3286357
          │   │   ├─{python3.11},3286358
          │   │   ├─{python3.11},3286360
          │   │   ├─{python3.11},3286374
          │   │   ├─{python3.11},3286382
          │   │   ├─{python3.11},3286386
          │   │   ├─{python3.11},3286389
          │   │   └─{python3.11},3286393
          │   ├─python3.11,3281301 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   ├─pt_data_worker,3284733 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285797
          │   │   ├─pt_data_worker,3284796 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285798
          │   │   ├─pt_data_worker,3284797 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285799
          │   │   ├─pt_data_worker,3284875 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285800
          │   │   ├─pt_data_worker,3284985 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285801
          │   │   ├─pt_data_worker,3285048 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285803
          │   │   ├─pt_data_worker,3285049 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285802
          │   │   ├─pt_data_worker,3285112 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285804
          │   │   ├─{python3.11},3281331
          │   │   ├─{python3.11},3281520
          │   │   ├─{python3.11},3281525
          │   │   ├─{python3.11},3281538
          │   │   ├─{python3.11},3281541
          │   │   ├─{python3.11},3281542
          │   │   ├─{python3.11},3281578
          │   │   ├─{python3.11},3281588
          │   │   ├─{python3.11},3281598
          │   │   ├─{python3.11},3281615
          │   │   ├─{python3.11},3282158
          │   │   ├─{python3.11},3285781
          │   │   ├─{python3.11},3285782
          │   │   ├─{python3.11},3285786
          │   │   ├─{python3.11},3285788
          │   │   ├─{python3.11},3285790
          │   │   ├─{python3.11},3285791
          │   │   ├─{python3.11},3285792
          │   │   ├─{python3.11},3285795
          │   │   ├─{python3.11},3286364
          │   │   ├─{python3.11},3286379
          │   │   ├─{python3.11},3286385
          │   │   ├─{python3.11},3286388
          │   │   ├─{python3.11},3286390
          │   │   ├─{python3.11},3286394
          │   │   ├─{python3.11},3286399
          │   │   └─{python3.11},3286403
          │   ├─python3.11,3281302 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   ├─pt_data_worker,3283237 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285711
          │   │   ├─pt_data_worker,3283349 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285767
          │   │   ├─pt_data_worker,3283352 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285765
          │   │   ├─pt_data_worker,3283658 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285769
          │   │   ├─pt_data_worker,3284057 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285768
          │   │   ├─pt_data_worker,3284201 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285779
          │   │   ├─pt_data_worker,3284302 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285771
          │   │   ├─pt_data_worker,3284530 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3285770
          │   │   ├─{python3.11},3281327
          │   │   ├─{python3.11},3281517
          │   │   ├─{python3.11},3281526
          │   │   ├─{python3.11},3281539
          │   │   ├─{python3.11},3281544
          │   │   ├─{python3.11},3281546
          │   │   ├─{python3.11},3281585
          │   │   ├─{python3.11},3281586
          │   │   ├─{python3.11},3281593
          │   │   ├─{python3.11},3281603
          │   │   ├─{python3.11},3281617
          │   │   ├─{python3.11},3282055
          │   │   ├─{python3.11},3285432
          │   │   ├─{python3.11},3285491
          │   │   ├─{python3.11},3285493
          │   │   ├─{python3.11},3285554
          │   │   ├─{python3.11},3285619
          │   │   ├─{python3.11},3285621
          │   │   ├─{python3.11},3285685
          │   │   ├─{python3.11},3285686
          │   │   ├─{python3.11},3286369
          │   │   ├─{python3.11},3286371
          │   │   ├─{python3.11},3286373
          │   │   ├─{python3.11},3286383
          │   │   ├─{python3.11},3286398
          │   │   ├─{python3.11},3286400
          │   │   ├─{python3.11},3286401
          │   │   └─{python3.11},3286402
          │   ├─python3.11,3281303 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   ├─pt_data_worker,3285822 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3286335
          │   │   ├─pt_data_worker,3285885 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3286334
          │   │   ├─pt_data_worker,3285886 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3286336
          │   │   ├─pt_data_worker,3285921 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3286337
          │   │   ├─pt_data_worker,3286074 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3286338
          │   │   ├─pt_data_worker,3286075 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3286339
          │   │   ├─pt_data_worker,3286123 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3286340
          │   │   ├─pt_data_worker,3286263 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3286341
          │   │   ├─{python3.11},3281326
          │   │   ├─{python3.11},3281515
          │   │   ├─{python3.11},3281523
          │   │   ├─{python3.11},3281533
          │   │   ├─{python3.11},3281558
          │   │   ├─{python3.11},3281559
          │   │   ├─{python3.11},3281575
          │   │   ├─{python3.11},3281582
          │   │   ├─{python3.11},3281594
          │   │   ├─{python3.11},3281605
          │   │   ├─{python3.11},3282163
          │   │   ├─{python3.11},3286326
          │   │   ├─{python3.11},3286327
          │   │   ├─{python3.11},3286328
          │   │   ├─{python3.11},3286329
          │   │   ├─{python3.11},3286330
          │   │   ├─{python3.11},3286331
          │   │   ├─{python3.11},3286332
          │   │   ├─{python3.11},3286333
          │   │   ├─{python3.11},3286356
          │   │   ├─{python3.11},3286370
          │   │   ├─{python3.11},3286391
          │   │   ├─{python3.11},3286395
          │   │   ├─{python3.11},3286396
          │   │   ├─{python3.11},3286397
          │   │   ├─{python3.11},3286408
          │   │   └─{python3.11},3286409
          │   ├─python3.11,3281304 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   ├─pt_data_worker,3282698 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3283217
          │   │   ├─pt_data_worker,3282761 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3283211
          │   │   ├─pt_data_worker,3282762 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3283213
          │   │   ├─pt_data_worker,3282887 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3283218
          │   │   ├─pt_data_worker,3282950 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3283215
          │   │   ├─pt_data_worker,3283013 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3283214
          │   │   ├─pt_data_worker,3283015 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3283212
          │   │   ├─pt_data_worker,3283093 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3283216
          │   │   ├─{python3.11},3281330
          │   │   ├─{python3.11},3281513
          │   │   ├─{python3.11},3281521
          │   │   ├─{python3.11},3281534
          │   │   ├─{python3.11},3281561
          │   │   ├─{python3.11},3281562
          │   │   ├─{python3.11},3281580
          │   │   ├─{python3.11},3281589
          │   │   ├─{python3.11},3281597
          │   │   ├─{python3.11},3281619
          │   │   ├─{python3.11},3282157
          │   │   ├─{python3.11},3283203
          │   │   ├─{python3.11},3283204
          │   │   ├─{python3.11},3283205
          │   │   ├─{python3.11},3283206
          │   │   ├─{python3.11},3283207
          │   │   ├─{python3.11},3283208
          │   │   ├─{python3.11},3283209
          │   │   ├─{python3.11},3283210
          │   │   ├─{python3.11},3286352
          │   │   ├─{python3.11},3286372
          │   │   ├─{python3.11},3286384
          │   │   ├─{python3.11},3286392
          │   │   ├─{python3.11},3286404
          │   │   ├─{python3.11},3286405
          │   │   ├─{python3.11},3286406
          │   │   └─{python3.11},3286407
          │   ├─python3.11,3281305 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   ├─pt_data_worker,3282178 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3282695
          │   │   ├─pt_data_worker,3282241 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3282690
          │   │   ├─pt_data_worker,3282242 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3282691
          │   │   ├─pt_data_worker,3282354 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3282694
          │   │   ├─pt_data_worker,3282430 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3282692
          │   │   ├─pt_data_worker,3282431 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3282696
          │   │   ├─pt_data_worker,3282556 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3282693
          │   │   ├─pt_data_worker,3282557 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py...
          │   │   │   └─{pt_data_worker},3282697
          │   │   ├─{python3.11},3281329
          │   │   ├─{python3.11},3281518
          │   │   ├─{python3.11},3281527
          │   │   ├─{python3.11},3281532
          │   │   ├─{python3.11},3281552
          │   │   ├─{python3.11},3281555
          │   │   ├─{python3.11},3281584
          │   │   ├─{python3.11},3281587
          │   │   ├─{python3.11},3281595
          │   │   ├─{python3.11},3281608
          │   │   ├─{python3.11},3282162
          │   │   ├─{python3.11},3282682
          │   │   ├─{python3.11},3282683
          │   │   ├─{python3.11},3282684
          │   │   ├─{python3.11},3282685
          │   │   ├─{python3.11},3282686
          │   │   ├─{python3.11},3282687
          │   │   ├─{python3.11},3282688
          │   │   ├─{python3.11},3282689
          │   │   ├─{python3.11},3286346
          │   │   ├─{python3.11},3286347
          │   │   ├─{python3.11},3286349
          │   │   ├─{python3.11},3286359
          │   │   ├─{python3.11},3286361
          │   │   ├─{python3.11},3286362
          │   │   ├─{python3.11},3286363
          │   │   └─{python3.11},3286366
          │   └─{pt_elastic},3281296
          ├─python3.11,3245170 -c from multiprocessing.resource_tracker import main;main(72)
          ├─{ilab},3245023
          ├─{ilab},3245085
          ├─{ilab},3245086
          ├─{ilab},3245087
          ├─{ilab},3245088
          ├─{ilab},3245089
          ├─{ilab},3245090
          ├─{ilab},3245091
          ├─{ilab},3245092
          ├─{ilab},3245093
          ├─{ilab},3245094
          ├─{ilab},3245095
          ├─{ilab},3245096
          ├─{ilab},3245097
          ├─{ilab},3245098
          ├─{ilab},3245099
          ├─{ilab},3245100
          ├─{ilab},3245104
          ├─{ilab},3245105
          ├─{ilab},3245106
          ├─{ilab},3245107
          ├─{ilab},3245108
          ├─{ilab},3245109
          ├─{ilab},3245110
          ├─{ilab},3245111
          ├─{ilab},3245112
          ├─{ilab},3245113
          ├─{ilab},3245114
          ├─{ilab},3245115
          ├─{ilab},3245116
          ├─{ilab},3245117
          ├─{ilab},3245118
          ├─{ilab},3245119
          ├─{ilab},3245120
          ├─{ilab},3245121
          ├─{ilab},3245122
          ├─{ilab},3245123
          ├─{ilab},3245124
          ├─{ilab},3245125
          ├─{ilab},3245126
          ├─{ilab},3245127
          ├─{ilab},3245128
          ├─{ilab},3245129
          ├─{ilab},3245130
          ├─{ilab},3245131
          ├─{ilab},3245132
          ├─{ilab},3245133
          ├─{ilab},3245134
          ├─{ilab},3245135
          ├─{ilab},3245136
          ├─{ilab},3245137
          ├─{ilab},3245138
          ├─{ilab},3245139
          ├─{ilab},3245140
          ├─{ilab},3245141
          ├─{ilab},3245142
          ├─{ilab},3245143
          ├─{ilab},3245144
          ├─{ilab},3245145
          ├─{ilab},3245146
          ├─{ilab},3245147
          ├─{ilab},3245148
          ├─{ilab},3245149
          ├─{ilab},3245150
          ├─{ilab},3245151
          ├─{ilab},3245152
          ├─{ilab},3245153
          ├─{ilab},3245154
          ├─{ilab},3245155
          ├─{ilab},3245156
          ├─{ilab},3245157
          ├─{ilab},3245158
          ├─{ilab},3245159
          ├─{ilab},3245160
          ├─{ilab},3245161
          ├─{ilab},3245162
          ├─{ilab},3245163
          ├─{ilab},3245164
          ├─{ilab},3245165
          ├─{ilab},3245166
          ├─{ilab},3245167
          ├─{ilab},3245172
          ├─{ilab},3245174
          ├─{ilab},3245175
          ├─{ilab},3245176
          ├─{ilab},3245177
          ├─{ilab},3245178
          ├─{ilab},3245179
          ├─{ilab},3245180
          ├─{ilab},3245181
          ├─{ilab},3245182
          ├─{ilab},3245183
          ├─{ilab},3245184
          ├─{ilab},3245185
          ├─{ilab},3245186
          ├─{ilab},3245187
          ├─{ilab},3245188
          ├─{ilab},3245189
          ├─{ilab},3245190
          ├─{ilab},3245191
          ├─{ilab},3245192
          ├─{ilab},3245193
          ├─{ilab},3245194
          ├─{ilab},3276663
          ├─{ilab},3276664
          ├─{ilab},3276665
          ├─{ilab},3276666
          ├─{ilab},3276667
          ├─{ilab},3276668
          ├─{ilab},3276669
          ├─{ilab},3276670
          ├─{ilab},3276671
          ├─{ilab},3276672
          ├─{ilab},3276673
          ├─{ilab},3276674
          ├─{ilab},3276675
          ├─{ilab},3276676
          ├─{ilab},3276677
          ├─{ilab},3276678
          ├─{ilab},3276679
          ├─{ilab},3276680
          ├─{ilab},3276681
          ├─{ilab},3276682
          ├─{ilab},3276683
          ├─{ilab},3276684
          ├─{ilab},3276729
          ├─{ilab},3276730
          ├─{ilab},3276731
          ├─{ilab},3276732
          ├─{ilab},3276733
          └─{ilab},3276866

[root@rhel_ai ~]# ps -ef|grep -v grep|grep 3281294
root     3281294 3244924  0 15:08 pts/0    00:00:06 /opt/app-root/bin/python3.11 /opt/app-root/bin/torchrun --nnodes=1 --node_rank=0 --nproc_per_node=8 --rdzv_id=123 --rdzv_endpoint=127.0.0.1:12222 /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py --model_name_or_path=/root/.local/share/instructlab/phased/phase1/checkpoints/hf_format/samples_4421 --data_path=/root/.local/share/instructlab/internal/data.jsonl --output_dir=/root/.local/share/instructlab/phased/phase2/checkpoints --num_epochs=1 --effective_batch_size=3840 --learning_rate=6e-06 --num_warmup_steps=25 --save_samples=0 --log_level=INFO --max_batch_len=60000 --seed=42 --chat-tmpl-path=/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_legacy_tmpl.py --checkpoint_at_epoch --accelerate_full_state_at_epoch --use_dolomite --lora_r=0 --lora_alpha=32 --lora_dropout=0.1 --lora_target_modules q_proj k_proj v_proj o_proj --distributed_training_framework=fsdp --fsdp_sharding_strategy=SHARD_GRAD_OP
root     3281298 3281294 98 15:08 ?        02:20:53 /opt/app-root/bin/python3.11 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py --model_name_or_path=/root/.local/share/instructlab/phased/phase1/checkpoints/hf_format/samples_4421 --data_path=/root/.local/share/instructlab/internal/data.jsonl --output_dir=/root/.local/share/instructlab/phased/phase2/checkpoints --num_epochs=1 --effective_batch_size=3840 --learning_rate=6e-06 --num_warmup_steps=25 --save_samples=0 --log_level=INFO --max_batch_len=60000 --seed=42 --chat-tmpl-path=/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_legacy_tmpl.py --checkpoint_at_epoch --accelerate_full_state_at_epoch --use_dolomite --lora_r=0 --lora_alpha=32 --lora_dropout=0.1 --lora_target_modules q_proj k_proj v_proj o_proj --distributed_training_framework=fsdp --fsdp_sharding_strategy=SHARD_GRAD_OP
root     3281299 3281294 99 15:08 ?        02:20:54 /opt/app-root/bin/python3.11 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py --model_name_or_path=/root/.local/share/instructlab/phased/phase1/checkpoints/hf_format/samples_4421 --data_path=/root/.local/share/instructlab/internal/data.jsonl --output_dir=/root/.local/share/instructlab/phased/phase2/checkpoints --num_epochs=1 --effective_batch_size=3840 --learning_rate=6e-06 --num_warmup_steps=25 --save_samples=0 --log_level=INFO --max_batch_len=60000 --seed=42 --chat-tmpl-path=/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_legacy_tmpl.py --checkpoint_at_epoch --accelerate_full_state_at_epoch --use_dolomite --lora_r=0 --lora_alpha=32 --lora_dropout=0.1 --lora_target_modules q_proj k_proj v_proj o_proj --distributed_training_framework=fsdp --fsdp_sharding_strategy=SHARD_GRAD_OP
root     3281300 3281294 99 15:08 ?        02:20:55 /opt/app-root/bin/python3.11 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py --model_name_or_path=/root/.local/share/instructlab/phased/phase1/checkpoints/hf_format/samples_4421 --data_path=/root/.local/share/instructlab/internal/data.jsonl --output_dir=/root/.local/share/instructlab/phased/phase2/checkpoints --num_epochs=1 --effective_batch_size=3840 --learning_rate=6e-06 --num_warmup_steps=25 --save_samples=0 --log_level=INFO --max_batch_len=60000 --seed=42 --chat-tmpl-path=/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_legacy_tmpl.py --checkpoint_at_epoch --accelerate_full_state_at_epoch --use_dolomite --lora_r=0 --lora_alpha=32 --lora_dropout=0.1 --lora_target_modules q_proj k_proj v_proj o_proj --distributed_training_framework=fsdp --fsdp_sharding_strategy=SHARD_GRAD_OP
root     3281301 3281294 99 15:08 ?        02:20:56 /opt/app-root/bin/python3.11 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py --model_name_or_path=/root/.local/share/instructlab/phased/phase1/checkpoints/hf_format/samples_4421 --data_path=/root/.local/share/instructlab/internal/data.jsonl --output_dir=/root/.local/share/instructlab/phased/phase2/checkpoints --num_epochs=1 --effective_batch_size=3840 --learning_rate=6e-06 --num_warmup_steps=25 --save_samples=0 --log_level=INFO --max_batch_len=60000 --seed=42 --chat-tmpl-path=/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_legacy_tmpl.py --checkpoint_at_epoch --accelerate_full_state_at_epoch --use_dolomite --lora_r=0 --lora_alpha=32 --lora_dropout=0.1 --lora_target_modules q_proj k_proj v_proj o_proj --distributed_training_framework=fsdp --fsdp_sharding_strategy=SHARD_GRAD_OP
root     3281302 3281294 99 15:08 ?        02:21:43 /opt/app-root/bin/python3.11 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py --model_name_or_path=/root/.local/share/instructlab/phased/phase1/checkpoints/hf_format/samples_4421 --data_path=/root/.local/share/instructlab/internal/data.jsonl --output_dir=/root/.local/share/instructlab/phased/phase2/checkpoints --num_epochs=1 --effective_batch_size=3840 --learning_rate=6e-06 --num_warmup_steps=25 --save_samples=0 --log_level=INFO --max_batch_len=60000 --seed=42 --chat-tmpl-path=/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_legacy_tmpl.py --checkpoint_at_epoch --accelerate_full_state_at_epoch --use_dolomite --lora_r=0 --lora_alpha=32 --lora_dropout=0.1 --lora_target_modules q_proj k_proj v_proj o_proj --distributed_training_framework=fsdp --fsdp_sharding_strategy=SHARD_GRAD_OP
root     3281303 3281294 99 15:08 ?        02:20:55 /opt/app-root/bin/python3.11 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py --model_name_or_path=/root/.local/share/instructlab/phased/phase1/checkpoints/hf_format/samples_4421 --data_path=/root/.local/share/instructlab/internal/data.jsonl --output_dir=/root/.local/share/instructlab/phased/phase2/checkpoints --num_epochs=1 --effective_batch_size=3840 --learning_rate=6e-06 --num_warmup_steps=25 --save_samples=0 --log_level=INFO --max_batch_len=60000 --seed=42 --chat-tmpl-path=/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_legacy_tmpl.py --checkpoint_at_epoch --accelerate_full_state_at_epoch --use_dolomite --lora_r=0 --lora_alpha=32 --lora_dropout=0.1 --lora_target_modules q_proj k_proj v_proj o_proj --distributed_training_framework=fsdp --fsdp_sharding_strategy=SHARD_GRAD_OP
root     3281304 3281294 99 15:08 ?        02:20:54 /opt/app-root/bin/python3.11 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py --model_name_or_path=/root/.local/share/instructlab/phased/phase1/checkpoints/hf_format/samples_4421 --data_path=/root/.local/share/instructlab/internal/data.jsonl --output_dir=/root/.local/share/instructlab/phased/phase2/checkpoints --num_epochs=1 --effective_batch_size=3840 --learning_rate=6e-06 --num_warmup_steps=25 --save_samples=0 --log_level=INFO --max_batch_len=60000 --seed=42 --chat-tmpl-path=/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_legacy_tmpl.py --checkpoint_at_epoch --accelerate_full_state_at_epoch --use_dolomite --lora_r=0 --lora_alpha=32 --lora_dropout=0.1 --lora_target_modules q_proj k_proj v_proj o_proj --distributed_training_framework=fsdp --fsdp_sharding_strategy=SHARD_GRAD_OP
root     3281305 3281294 99 15:08 ?        02:20:54 /opt/app-root/bin/python3.11 -u /opt/app-root/lib64/python3.11/site-packages/instructlab/training/main_ds.py --model_name_or_path=/root/.local/share/instructlab/phased/phase1/checkpoints/hf_format/samples_4421 --data_path=/root/.local/share/instructlab/internal/data.jsonl --output_dir=/root/.local/share/instructlab/phased/phase2/checkpoints --num_epochs=1 --effective_batch_size=3840 --learning_rate=6e-06 --num_warmup_steps=25 --save_samples=0 --log_level=INFO --max_batch_len=60000 --seed=42 --chat-tmpl-path=/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_legacy_tmpl.py --checkpoint_at_epoch --accelerate_full_state_at_epoch --use_dolomite --lora_r=0 --lora_alpha=32 --lora_dropout=0.1 --lora_target_modules q_proj k_proj v_proj o_proj --distributed_training_framework=fsdp --fsdp_sharding_strategy=SHARD_GRAD_OP

[root@rhel_ai ~]# 
```

<br>

### 2.3 모델 훈련 예

#### 2.3.1 지식 기여를 통해 얻은 합성 데이터를 사용하여 모델을 훈련

지식 훈련의 출력 예
```log
Training Phase 1/2...
TrainingArgs for current phase: TrainingArgs(model_path='/opt/app-root/src/.cache/instructlab/models/granite-7b-starter', chat_tmpl_path='/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_generic_tmpl.py', data_path='/tmp/jul19-knowledge-26k.jsonl', ckpt_output_dir='/tmp/e2e/phase1/checkpoints', data_output_dir='/opt/app-root/src/.local/share/instructlab/internal', max_seq_len=4096, max_batch_len=55000, num_epochs=2, effective_batch_size=128, save_samples=0, learning_rate=2e-05, warmup_steps=25, is_padding_free=True, random_seed=42, checkpoint_at_epoch=True, mock_data=False, mock_data_len=0, deepspeed_options=DeepSpeedOptions(cpu_offload_optimizer=False, cpu_offload_optimizer_ratio=1.0, cpu_offload_optimizer_pin_memory=False, save_samples=None), disable_flash_attn=False, lora=LoraOptions(rank=0, alpha=32, dropout=0.1, target_modules=('q_proj', 'k_proj', 'v_proj', 'o_proj'), quantize_data_type=<QuantizeDataType.NONE: None>))
```

#### 2.3.2 RHEL AI는 다음 단계에 사용할 가장 적합한 체크포인트를 선택

#### 2.3.3 다음 단계에서는 기술 데이터의 합성 데이터를 사용하여 모델을 훈련

기술 훈련의 예
```log
Training Phase 2/2...
TrainingArgs for current phase: TrainingArgs(model_path='/tmp/e2e/phase1/checkpoints/hf_format/samples_52096', chat_tmpl_path='/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_generic_tmpl.py', data_path='/usr/share/instructlab/sdg/datasets/skills.jsonl', ckpt_output_dir='/tmp/e2e/phase2/checkpoints', data_output_dir='/opt/app-root/src/.local/share/instructlab/internal', max_seq_len=4096, max_batch_len=55000, num_epochs=2, effective_batch_size=3840, save_samples=0, learning_rate=2e-05, warmup_steps=25, is_padding_free=True, random_seed=42, checkpoint_at_epoch=True, mock_data=False, mock_data_len=0, deepspeed_options=DeepSpeedOptions(cpu_offload_optimizer=False, cpu_offload_optimizer_ratio=1.0, cpu_offload_optimizer_pin_memory=False, save_samples=None), disable_flash_attn=False, lora=LoraOptions(rank=0, alpha=32, dropout=0.1, target_modules=('q_proj', 'k_proj', 'v_proj', 'o_proj'), quantize_data_type=<QuantizeDataType.NONE: None>))
```

#### 2.3.4 2단계 모델 훈련의 체크포인트 평가 및 반환

RHEL AI는 Multi-turn Benchmark(MT-Bench)를 사용하여 2단계 모델 학습의 모든 체크포인트를 평가하고 완전히 학습된 출력 모델로 가장 성능이 좋은 체크포인트를 반환

기술 평가 출력의 예
```log
MT-Bench evaluation for Phase 2...
Using gpus from --gpus or evaluate config and ignoring --tensor-parallel-size configured in serve vllm_args
INFO 2024-08-15 10:04:51,065 instructlab.model.backends.backends:437: Trying to connect to model server at http://127.0.0.1:8000/v1
INFO 2024-08-15 10:04:53,580 instructlab.model.backends.vllm:208: vLLM starting up on pid 79388 at http://127.0.0.1:54265/v1
INFO 2024-08-15 10:04:53,580 instructlab.model.backends.backends:450: Starting a temporary vLLM server at http://127.0.0.1:54265/v1
INFO 2024-08-15 10:04:53,580 instructlab.model.backends.backends:465: Waiting for the vLLM server to start at http://127.0.0.1:54265/v1, this might take a moment... Attempt: 1/300
INFO 2024-08-15 10:04:58,003 instructlab.model.backends.backends:465: Waiting for the vLLM server to start at http://127.0.0.1:54265/v1, this might take a moment... Attempt: 2/300
INFO 2024-08-15 10:05:02,314 instructlab.model.backends.backends:465: Waiting for the vLLM server to start at http://127.0.0.1:54265/v1, this might take a moment... Attempt: 3/300
moment... Attempt: 3/300
INFO 2024-08-15 10:06:07,611 instructlab.model.backends.backends:472: vLLM engine successfully started at http://127.0.0.1:54265/v1
```

#### 2.3.5 훈련이 완료되면 확인 메시지가 나타나고 가장 잘 수행된 체크포인트가 표시

완전한 다단계 훈련 실행의 출력 예
```log
Training finished! Best final checkpoint: samples_1945 with score: 6.813759384
```
* 평가 및 제공에 이 경로가 필요하므로 이 체크포인트를 기록 필요
<br>

### 2.4 검증

#### 2.4.1 훈련된 데이터 포인트

* *ilab model train*으로 모델을 훈련할 때, 여러 개의 체크포인트는 훈련된 데이터 포인트 수에 따라 samples_ 접두사로 저장
* *~/.local/share/instructlab/phase/* 디렉토리에 저장 됨

#### 2.4.2 실행 예

실행 명령어
```bash
ls ~/.local/share/instructlab/phase/<phase1-or-phase2>/checkpoints/
```

실행 결과 - 새로운 모델의 출력 예
```log
samples_1711 samples_1945 samples_1456 samples_1462 samples_1903
```
<br>

### 2.5 훈련 재시작 혹은 이어하기

RHEL AI를 사용하면 다중 단계 훈련 중에 실패했을 수 있는 훈련 실행을 계속할 수 있습니다.

**훈련 실행이 실패하는 경우**
* vLLM 서버가 올바르게 시작되지 않음
* 가속기 또는 GPU가 정지되어 훈련이 중단
* ***InstructLab***의 *config.yaml* 파일에 오류

처음으로 다중 단계 훈련을 실행하면 초기 훈련 데이터가 *journalfile.yaml* 파일에 저장됩니다.
* 필요한 경우 파일의 이 메타데이터를 사용하여 실패한 훈련을 다시 시작 가능
* 다중 단계 훈련을 실행할 때 CLI 프롬프트에 따라 훈련 데이터를 지우는 훈련 실행을 다시 시작 가능

#### 2.5.1 다단계 훈련 명령을 다시 실행

```bash
ilab model train --strategy lab-multiphase \
    --phased-phase1-data ~/.local/share/instructlab/datasets/<generation-date>/<knowledge-train-messages-jsonl-file> \
    --phased-phase2-data ~/.local/share/instructlab/datasets/<generation-date>/<skills-train-messages-jsonl-file>
```
* RHEL AI CLI는 *journalfile.yaml* 파일이 있는지 읽고 해당 지점에서 학습 실행을 계속

#### 2.5.2 훈련 실행을 계속할지 아니면 처음부터 시작할지 선택

* ***n***을 입력하여, 미리보기 학습 실행을 계속
  ```
  Metadata (checkpoints, the training journal) may have been saved from a previous training run.
  By default, training will resume from this metadata if it exists
  Alternatively, the metadata can be cleared, and training can start from scratch
  Would you like to START TRAINING FROM THE BEGINNING? n
  ```

* ***y***를 입력하여, 훈련 실행을 다시 시작
  ```
  Metadata (checkpoints, the training journal) may have been saved from a previous training run.
  By default, training will resume from this metadata if it exists
  Alternatively, the metadata can be cleared, and training can start from scratch
  Would you like to START TRAINING FROM THE BEGINNING? y
  ```
* 재시작하면 이전 검사점, 저널 파일 및 기타 교육 데이터의 시스템 캐시도 지워짐
<br>
<br>

## 3. 모델 평가

새 모델의 개선 사항을 측정하려면 평가 프로세스를 통해 기본 모델과 성능을 비교할 수 있습니다.
* 모델과 직접 채팅하여 새 모델이 새로 만든 지식을 학습했는지 정성적으로 확인 가능
* 모델 개선 사항에 대한 정량적 결과를 더 원하면 RHEL AI CLI에서 평가 프로세스를 실행 가능

**InstructLab의 모델 평가 구성**
```bash
yq '.evaluate' .config/instructlab/config.yaml
```

실행 결과
```json
{
  "base_branch": null,
  "base_model": "/var/home/instruct/.cache/instructlab/models/granite-3.1-8b-starter-v1",
  "branch": null,
  "dk_bench": {
    "input_questions": null,
    "judge_model": "gpt-4o",
    "output_dir": "/var/home/instruct/.local/share/instructlab/internal/eval_data/dk_bench",
    "output_file_formats": "jsonl"
  },
  "gpus": 4,
  "mmlu": {
    "batch_size": "auto",
    "few_shots": 5
  },
  "mmlu_branch": {
    "tasks_dir": "/var/home/instruct/.local/share/instructlab/datasets"
  },
  "model": null,
  "mt_bench": {
    "judge_model": "/var/home/instruct/.cache/instructlab/models/prometheus-8x7b-v2-0",
    "max_workers": "auto",
    "output_dir": "/var/home/instruct/.local/share/instructlab/internal/eval_data/mt_bench"
  },
  "mt_bench_branch": {
    "judge_model": "/var/home/instruct/.cache/instructlab/models/prometheus-8x7b-v2-0",
    "output_dir": "/var/home/instruct/.local/share/instructlab/internal/eval_data/mt_bench_branch",
    "taxonomy_path": "/var/home/instruct/.local/share/instructlab/taxonomy"
  },
  "system_prompt": null,
  "temperature": 0.0
}
```

### 3.1 새 모델 평가

#### 3.1.1 *qna.yaml* 파일을 생성한 작업 git 브랜치로 이동

#### 3.1.2 벤치마크에서 평가 프로세스를 실행

각 명령에는 평가할 훈련된 `samples` 모델에 대한 경로가 필요하며, `~/.local/share/instructlab/checkpoints` 폴더에서 이러한 체크포인트에 액세스할 수 있습니다.

**MMLU_BRANCH** 벤치마크
* 귀하의 지식 기여가 모델에 어떤 영향을 미쳤는지 측정하려면 다음 명령을 실행하여 mmlu_branch 벤치마크를 실행
  ```bash
  ilab model evaluate --benchmark mmlu_branch
      --model ~/.local/share/instructlab/phased/phase2/checkpoints/hf_format/<checkpoint> \
      --tasks-dir ~/.local/share/instructlab/datasets/<generation-date>/<node-dataset> \
      --base-model ~/.cache/instructlab/models/granite-7b-starter
  ```
  + \<checkpoint\>: 다중 단계 훈련 중 생성된 최고 점수의 체크포인트 파일을 지정
  + \<node-dataset\>
     - ~/.local/share/instructlab/datasets/\<generation-date\> 디렉토리에 SDG 동안 생성된 node_datasets 디렉토리를 지정
     - 모드 학습에 사용된 *.jsonl 파일과 동일한 타임스탬프를 지정

* 실행 결과 예
  ```
  # KNOWLEDGE EVALUATION REPORT
  
  ## BASE MODEL (SCORE)
  /home/user/.cache/instructlab/models/instructlab/granite-7b-lab/ (0.74/1.0)
  
  ## MODEL (SCORE)
  /home/user/local/share/instructlab/phased/phases2/checkpoints/hf_format/samples_665(0.78/1.0)
  
  ### IMPROVEMENTS (0.0 to 1.0):
  1. tonsils: 0.74 -> 0.78 (+0.04)
  ```

**MT_BENCH_BRANCH** 벤치마크
* 기술 기여가 모델에 어떤 영향을 미쳤는지 측정하려면 다음 명령을 실행
  ```bash
  ilab model evaluate \
      --benchmark mt_bench_branch \
      --model ~/.local/share/instructlab/phased/phase2/checkpoints/hf_format/<checkpoint> \
      --judge-model ~/.cache/instructlab/models/prometheus-8x7b-v2-0 \
      --branch <worker-branch> \
      --base-branch <worker-branch>
  ```
  + \<checkpoint\>: 여러 단계로 구성된 훈련 중 생성된 가장 높은 점수를 받은 체크포인트 파일을 지정
  + \<worker-branch\>: 택소노미 트리에 데이터를 추가할 때 사용한 분기를 지정
  + \<num-gpus\>: 평가에 사용할 GPU 수를 지정
* 실행 결과 예
  ```
  # SKILL EVALUATION REPORT
  
  ## BASE MODEL (SCORE)
  /home/user/.cache/instructlab/models/instructlab/granite-7b-lab (5.78/10.0)
  
  ## MODEL (SCORE)
  /home/user/local/share/instructlab/phased/phases2/checkpoints/hf_format/samples_665(6.00/10.0)
  
  ### IMPROVEMENTS (0.0 to 10.0):
  1. foundational_skills/reasoning/linguistics_reasoning/object_identification/qna.yaml: 4.0 -> 6.67 (+2.67)
  2. foundational_skills/reasoning/theory_of_mind/qna.yaml: 3.12 -> 4.0 (+0.88)
  3. foundational_skills/reasoning/linguistics_reasoning/logical_sequence_of_words/qna.yaml: 9.33 -> 10.0 (+0.67)
  4. foundational_skills/reasoning/logical_reasoning/tabular/qna.yaml: 5.67 -> 6.33 (+0.67)
  5. foundational_skills/reasoning/common_sense_reasoning/qna.yaml: 1.67 -> 2.33 (+0.67)
  6. foundational_skills/reasoning/logical_reasoning/causal/qna.yaml: 5.67 -> 6.0 (+0.33)
  7. foundational_skills/reasoning/logical_reasoning/general/qna.yaml: 6.6 -> 6.8 (+0.2)
  8. compositional_skills/writing/grounded/editing/content/qna.yaml: 6.8 -> 7.0 (+0.2)
  9. compositional_skills/general/synonyms/qna.yaml: 4.5 -> 4.67 (+0.17)
  
  ### REGRESSIONS (0.0 to 10.0):
  1. foundational_skills/reasoning/unconventional_reasoning/lower_score_wins/qna.yaml: 5.67 -> 4.0 (-1.67)
  2. foundational_skills/reasoning/mathematical_reasoning/qna.yaml: 7.33 -> 6.0 (-1.33)
  3. foundational_skills/reasoning/temporal_reasoning/qna.yaml: 5.67 -> 4.67 (-1.0)
  
  ### NO CHANGE (0.0 to 10.0):
  1. foundational_skills/reasoning/linguistics_reasoning/odd_one_out/qna.yaml (9.33)
  2. compositional_skills/grounded/linguistics/inclusion/qna.yaml (6.5)
  ```


#### 3.1.3 (옵션) 수동 평가

MMLU 및 MT_BENCH 벤치마크를 사용하여 각 체크포인트를 수동으로 평가할 수 있습니다.
* 표준화된 지식 또는 기술 집합에 대해 모든 모델을 평가하여 다른 LLM과 자신의 모델의 점수를 비교

**MMLU**
* 표준화된 지식 데이터 집합에 대한 새 모델의 평가 점수를 확인하려면 다음 명령을 실행하여 mmlu 벤치마크를 설정
  ```bash
  ilab model evaluate --benchmark mmlu --model ~/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_665
  ```
  + \<checkpoint\>: 다단계 학습 중 생성된 체크포인트 파일 중 하나를 지정
* 실행 결과 예
  ```
  # KNOWLEDGE EVALUATION REPORT
  
  ## MODEL (SCORE)
  /home/user/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_665
  
  ### SCORES (0.0 to 1.0):
  mmlu_abstract_algebra - 0.31
  mmlu_anatomy - 0.46
  mmlu_astronomy - 0.52
  mmlu_business_ethics - 0.55
  mmlu_clinical_knowledge - 0.57
  mmlu_college_biology - 0.56
  mmlu_college_chemistry - 0.38
  mmlu_college_computer_science - 0.46
  ...
  ```

> [!NOTE]
> **MMLU (Massive Multitask Language Understanding)**<br>
> <br>
> 인공지능 모델이 획득한 지식을 측정하는 벤치하크로, 약 57개의 주제에 대해 다지선다 문제를 푸는 테스트 입니다. 특히 zero-shot 환경이나 few-shot 환경에 맞게 되어 있습니다.

**MT_BENCH**
* 표준화된 기술 세트와 비교하여 새 모델의 평가 점수를 확인하려면 다음 명령을 실행하여 mt_bench 벤치마크를 설정
  ```bash
  ilab model evaluate --benchmark mt_bench --model ~/.local/share/instructlab/phased/phases2/checkpoints/hf_format/samples_665
  ```
  + \<checkpoint\>: 다단계 학습 중 생성된 체크포인트 파일 중 하나를 지정
* 실행 결과 예
  ```
  # SKILL EVALUATION REPORT
  
  ## MODEL (SCORE)
  /home/user/local/share/instructlab/phased/phases2/checkpoints/hf_format/samples_665(7.27/10.0)
  
  ### TURN ONE (0.0 to 10.0):
  7.48
  
  ### TURN TWO (0.0 to 10.0):
  7.05
  ```

> [!NOTE]
> **MT-Bench (Multi-turn Benchmark)**<br>
> <br>
> 언어 모델이 얼마나 잘 대화할 수 있는지 평가하기 위한 프레임워크입니다. 다양한 모델의 성능을 비교하고 강점과 약점을 파악하는 데 사용됩니다.
<br>

### 3.2 도메인 지식 벤치마크 평가

RHEL AI, MMLU 및 MMLU_branch의 현재 지식 평가 벤치마크는 다중 선택형 질문에 답하는 능력에 따라 모델을 평가합니다.
* 도메인 지식 벤치마크(Domain Knowledge Benchmark: DK-bench) 평가는 사용자 지정 평가 질문을 제공하고 모델 답변을 척도에 따라 평가할 수 있는 기능을 제공
* 제공된 각 답변은 참조 답변과 비교되고 심사 모델이 다음 척도에 따라 등급을 매김

**도메인 지식 벤치마크 루브릭**
|$\color{lime}{\texttt{점수}}$|$\color{lime}{\texttt{기준}}$|
|:--:|:---|
|1|응답은 전혀 틀렸거나, 관련성이 없거나, 어떤 의미 있는 방식으로든 참조 내용과 일치하지 않음|
|2|응답은 참조 내용과 부분적으로 일치하지만, 중대한 오류, 중요한 누락 또는 관련 없는 정보가 포함되어 있음|
|3|응답은 전반적인 참고 자료와 일치하지만 충분한 세부 정보나 명확성이 부족하거나 사소한 부정확성을 포함하고 있음|
|4|응답은 대체로 정확하고, 참고 자료와 긴밀하게 일치하며, 사소한 문제점이나 누락만 포함되어 있음|
|5|답변은 완벽히 정확하고, 참고문헌과 완벽히 일치하며, 명확하고, 철저하고, 상세함|
<br>

### 3.3 수행 절차

#### 3.3.1 평가 질문 파일 생성

사용자 정의 평가를 활용하려면 모델에 답하고 평가할 모든 질문을 포함하는 jsonl 파일을 만들어야 합니다.

예) DK-bench를 위한 `jsonl` 파일
```
{"user_input":"What is the capital of Canada?","reference":"The capital of Canada is Ottawa."}
```
* user_input: 모델에 대한 질문이 포함
* reference: 질문에 대한 답변이 포함

#### 3.3.2 평가를 위한 벤치마크 실행

사용자 정의 평가 질문으로 DK-bench 벤치마크를 실행
```bash
ilab model evaluate --benchmark dk_bench --input-questions /home/use/path/to/questions.jsonl --model ~/.cache/instructlab/models/instructlab/granite-7b-lab
```
* \<path-to-jsonl-file\>: 질문과 답변이 포함된 jsonl 파일의 경로를 지정
* \<path-to-model\>: 평가하려는 모델의 경로를 지정

실행 명령어
```bash
ilab model evaluate --benchmark dk_bench --input-questions /home/use/path/to/questions.jsonl --model ~/.cache/instructlab/models/instructlab/granite-7b-lab
```

실행 결과
```
# DK-BENCH REPORT

## MODEL: granite-7b-lab

Question #1:     5/5
Question #2:     5/5
Question #3:     5/5
Question #4:     5/5
Question #5:     2/5
Question #6:     3/5
Question #7:     2/5
Question #8:     3/5
Question #9:     5/5
Question #10:     5/5
----------------------------
Average Score:   4.00/5
Total Score:     40/50
```
<br>

### 3.4 한국어 평가 사례

다양한 인공지능 모델이 계속해서 나오고 있지만, 대부분이 영어를 기반으로 하고 있으며, 모델에 대한 평가도 영어(데이터 세트)로 수행되어 결과가 발표되고 있습니다.

한국어를 기반으로 모델을 훈련하고 이를 평가하는 방안에 대한 얘기가 국내에서 이루어지고 있으며, 다음은 이를 위해 모델을 평가하는 방안 및 결과에 대한 사례 입니다.

|$\color{lime}{\texttt{벤치마크}}$|$\color{lime}{\texttt{참조}}$|
|:---|:---|
|CLIcK (Cultural and Linguistic Intelligence in Korean)|[깃허브](https://github.com/rladmstn1714/CLIcK)<br>[논문](https://arxiv.org/abs/2403.06412)<br>[허깅페이스](https://huggingface.co/datasets/EunsuKim/CLIcK)|
|HAE_RAE_BENCH 1.0|[깃허브](https://github.com/HAE-RAE/HAE-RAE-BENCH)<br>[논문](https://arxiv.org/abs/2309.02706)<br>[허깅페이스](https://huggingface.co/datasets/HAERAE-HUB/HAE_RAE_BENCH_1.0)|
|KMMLU|<br>[논문](https://arxiv.org/abs/2402.11548)<br>[허깅페이스](https://huggingface.co/datasets/HAERAE-HUB/KMMLU)|
|KMMLU-HARD|<br>[논문](https://arxiv.org/abs/2402.11548)<br>[허깅페이스](https://huggingface.co/datasets/HAERAE-HUB/KMMLU-HARD)|

#### 3.4.1 CLIcK (Cultural and Linguistic Intelligence in Korean)

* 다음 과목 영역에서 한국어 능력을 평가
  + 한국 문화
    - 역사
    - 지리
    - 법률
    - 정치
    - 사회
    - 전통
    - 경제
    - 대중 문화
  + 한국어
    - 텍스트
    - 기능
    - 문법
* 11개 범주에 총 1,995개의 샘플 데이터
* 4개 또는 5개의 객관식 문제를 제시
* 질문에 따라 추가 맥락이 제공

#### 3.4.2 HAE_RAE_BENCH 1.0

* 다음 6가지 범주에서 한국어 능력을 평가
  + 일반 지식
  + 역사
  + 외래어
  + 희귀어
  + 독해 이해
  + 표준 명명법
* CLiCK과 유사하게, 이 과제는 객관식 문제를 푸는 것이지만, 추가 맥락은 없음
* 6가지 범주에 총 1,538개의 샘플 데이터

#### 3.4.3 KMMLU

* 한국어로 된 대규모 멀티태스크 언어 이해 평가 데이터 세트
* MMLU 데이터셋을 단순히 번역한 것이 아니라 한국어 텍스트에서 생성된 데이터로, 한국어에서 LLM/SLM이 얼마나 잘 작동하는지 평가
* STEM, 응용 과학, HUMSS, 기타 등 총 45개 카테고리와 4개 슈퍼 카테고리로 구성

#### 3.4.4 KMMLU-HARD

* KMMLU 데이터 세트의 확장 버전으로 더 어려운 질문이 포함
* 한국어 NLP 모델의 한계를 더욱 평가하도록 설계
* 특히 높은 수준의 이해 및 추론 기술이 필요한 질문이 포함

<br>
<br>

## 4. 새 모델 제공 및 채팅

모델을 제공함으로써 모델을 머신에 배포해야 합니다.
* 모델이 배포되고 모델을 상호 작용하고 채팅 가능

### 4.1 새로운 모델을 제공

새 모델과 상호 작용하려면 서빙을 통해 머신에서 모델을 활성화해야 합니다.

#### 4.1.1 모델과 채팅할 수 있는 vLLM 서버를 시작

```bash
ilab model serve --model-path <path-to-best-performed-checkpoint>
```
* \<path-to-best-performed-checkpoint\>
  + 훈련 후 빌드한 체크포인트의 전체 경로를 지정
  + 새 모델은 훈련 후 파일 경로가 표시된 가장 잘 수행된 체크포인트

#### 4.1.2 실행 예

실행 명령 예
```bash
ilab model serve --model-path ~/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1945/
```

실행 결과 예
```log
$ ilab model serve --model-path ~/.local/share/instructlab/phased/phase2/checkpoints/hf_format/<checkpoint>
INFO 2024-03-02 02:21:11,352 lab.py:201 Using model /home/example-user/.local/share/instructlab/checkpoints/hf_format/checkpoint_1945 with -1 gpu-layers and 4096 max context size.
Starting server process
After application startup complete see http://127.0.0.1:8000/docs for API.
Press CTRL+C to shut down the server.
```
<br>

### 4.2 새로운 모델과의 채팅

#### 4.2.1 새로운 터미널 실행

하나의 터미널 창에서 모델을 제공하고 있으므로 모델과 채팅하려면 새 터미널 창을 열어야 합니다.

#### 4.2.2 새 모델과 채팅하려면 다음 명령을 실행

명령어 형식
```bash
ilab model chat --model <path-to-best-performed-checkpoint-file>
```
* \<path-to-best-performed-checkpoint-file\>
  + 훈련 후 빌드한 새 모델 체크포인트 파일을 지정
  + 새 모델은 훈련 후 파일 경로가 표시된 가장 잘 수행된 체크포인트

실행 예
```bash
$ ilab model chat --model ~/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1945
```

#### 4.2.3 InstructLab 챗봇의 출력 예

```
$ ilab model chat
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────── system ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Welcome to InstructLab Chat w/ CHECKPOINT_1945 (type /h for help)                                                                                                                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
>>>                                                                                                                                                                                                                        [S][default]
```
<br>

### 4.3 훈련된 모델 업로드 

실행 명령어
```bash
ilab model upload --model <name-of-model> --destination <registry-location> --dest-type <registry-type>
```
* \<name-of-model\>
  + 업로드 할 체크포인트 이름
  + 체크포인트 경로 지정 가능
* \<registry-location\>
  + 모델 업로드 위치
* \<registry-type\>
  + 모델 형식 지정
  + 현재 `s3` 지원

예 - s3 버킷에 업로드
```
ilab model upload --model samples_0801 --destination example-s3-bucket --dest-type s3
```
<br>
<br>

------
[차례](../README.md)
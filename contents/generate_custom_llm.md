# RHEL AI를 사용하여 커스텀 LLM 생성

1. [SDG로 새 데이터 세트 생성](./generate_custom_llm.md#1-sdg로-새-데이터-세트-생성)<br>
2. [모델 학습](./generate_custom_llm.md#2-모델-학습)<br>
3. [모델 평가](./generate_custom_llm.md#3-모델-평가)<br>
4. [새 모델 제공 및 채팅](./generate_custom_llm.md#4-새-모델-제공-및-채팅)<br>
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
  + SDG 중에 생성된 knowledge_messages.jsonl 파일의 위치
  + RHEL AI는 *.jsonl 파일의 데이터를 사용하여 학생 모델 *granite-3.1-8b-starter-v1*를 훈련
  + 경로 예
    ```
    ~/.local/share/instructlab/datasets/2024-09-07_194933/knowledge_train_msgs_2024-09-07T20_54_21.jsonl.
    ```
* \<skills-train-messages-file\>
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

#### 2.5.2 교육 실행을 계속할지 아니면 처음부터 시작할지 선택

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
> 인공지능 모델이 획득한 지식을 측정하는 벤치하크로, 약 57개의 주제에 대해 다지선다 문제를 푸는 테스트 입니다. 특히 zero-shot 환경이나 few-shot 환경에 맞게 되어 있습니ㅏㄷ.

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
<br>

------
[차례](../README.md)
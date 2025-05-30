# 모델 최적화

**차례**
1. Neural Magic을 통한 모델 압축<br>
&nbsp;1.1 [Neural Magic](quantization_model.md#11-neural-magic)<br>
&nbsp;1.2 [압축된 모델 평가](quantization_model.md#12-압축된-모델-평가)<br>
&nbsp;1.3 [압축된 granite 작동 방식](quantization_model.md#13-압축된-granite-작동-방식)<br>
&nbsp;1.4 [에이전트 파이프라인 명령어 수행 평가](quantization_model.md#14-에이전트-파이프라인-명령어-수행-평가)<br>
2. GGUF vs GGML<br>
&nbsp;2.1 [PT-Generated Unified Format(GGUF)란](quantization_model.md#21-pt-generated-unified-formatgguf란)<br>
&nbsp;2.2 [GGUF와 GGML의 차이](quantization_model.md#22-gguf와-ggml의-차이)<br>
&nbsp;2.3 [GGUF로 전환](quantization_model.md#23-gguf로-전환)<br>
3. []()<br>

<br>

## 1. Neural Magic을 통한 모델 압축

### 1.1 Neural Magic

* 개방적이고 효율적인 AI를 제공한다는 사명을 가속화
* 새로운 압축 Granite 3.1 모델은 엔터프라이즈 배포용으로 설계
  + 기존 모델보다 3.3배 더 작은 크기
  + 최대 2.8배 향상된 성능
  + 99%의 정확도 복구를 달성
* 모델과 레시피는 Hugging Face에서 오픈 소스로 제공
* vLLM을 통해 배포 가능하고 LLM Compressor를 사용하여 확장 가능
<br>

### 1.2 압축된 모델 평가

#### 1.2.1 압축된 Granite 3.1 8B 및 2B 모델 출시

* Neural Magic의 첫 번째 기여
* 접근성과 효율성을 향상시키기 위해 Granite 3.1 모델의 양자화 버전을 개발
  + 이러한 압축 변형은 99%의 정확도 복구를 유지
  + 리소스 요구 사항을 줄여 비용 효율적이고 확장 가능한 AI 배포에 이상적
* 사용 가능한 옵션
  |$\color{lime}{\texttt{옵션}}$|$\color{lime}{\texttt{옵션 이름}}$|$\color{lime}{\texttt{설명}}$|
  |:--------|:----------------------------|:---|
  |FP8 W8A8 |FP8 weights and activiations |NVIDIA Ada Lovelace 및 Hopper GPU에서 서버 및 처리량 기반 시나리오에 최적화|
  |INT W8A8 |INT8 weights and activiations|NVIDIA Ampere 및 이전 GPU를 사용하는 서버에 이상적|
  |FP8 W4A16|INT4 weight-only models      |지연 시간에 민감한 애플리케이션이나 GPU 리소스가 제한된 경우에 적합|

#### 1.2.2 성능 평가

**광범위한 평가를 통한 결과**
* 최대 3.3배 더 작음
* 평균 99%의 정확도 복구
* 최대 2.8배 더 뛰어난 추론 성능

<img src="./images/compressed_granite_3.1_performance.webp" title="100px" alt="압축된 granite 3.1 모델 성능"/>

> [!NOTE]
> OpenLLM Leaderboard V1과 OpenLLM Leaderboard V2의 평균에 따른 정확도 평가를 위해 Granite 3.1 모델(8B, 2B)의 기준선과 양자화 버전을 비교했습니다.

<br>

<img src="./images/compressed_granite_3.1_inference_benchmarks.webp" title="100px" alt="압축된 granite 3.1 모델 성능"/>

> [!NOTE]
> 1xA6000 및 1xL40 GPU에서 RAG 및 코드 완성 시나리오에 대한 추론 벤치마크를 위한 Granite 3.1 8B의 기준 버전과 양자화 버전을 비교하여 최상의 지연 시간(단일 스트림) 및 처리량(멀티 스트림) 성능을 비교했습니다.

<br>

### 1.3 압축된 Granite 작동 방식

**작동 방식**
* 압축된 Granite 3.1 모델은 vLLM 생태계와 완벽하게 통합
* 개발자는 이러한 모델을 신속하게 배포 가능
* LLM Compressor를 통해 특정 요구 사항에 맞게 압축 레시피를 추가로 맞춤 설정 가능

**예 - vLLM을 시작**
```py
from vllm import LLM

llm = LLM(model="neuralmagic/granite-3.1-8b-instruct-quantized.w4a16")
prompts = ["The Future of AI is"]

for output in llm.generate(prompts)
    print(f"Prompt {output.prompt}, Generated: {output.outputs[0].text}")
```

### 1.4 에이전트 파이프라인 명령어 수행 평가

#### 1.4.1 작은 요청

**수행 평가**
* 에이전트 파이프라인의 명령어 수행 작업(프롬프트 토큰 256개, 출력 토큰 128개)과 같이 더 작은 요청 크기의 경우, 압축된 Granite 모델은 다양한 GPU에서 지연 시간, 서버 및 처리량 사용 사례 전반에 걸쳐 일관된 성능 향상을 제공

<img src="./images/compressed_granite_3.1_requests_per_second.webp" title="100px" alt="압축된 granite 3.1 모델 작은 용량 요청 처리 성능"/>

* Single Stream, Latency
  + W4A16은 A5000 대비 2.7배, L40 대비 1.5배 낮은 지연 시간으로 가장 높은 효율성을 달성
* Multi-Stream
  + W8A8 모델은 A5000에서 6 RPS 이후 가장 우수한 성능을 발휘하여 동일한 성능에서 초당 1.6배 더 많은 요청을 처리
  + W4A16은 L40에서 최대 8배 더 많은 요청을 처리
  
> [!NOTE]
> 1xA5000 및 1xL40 GPU에서 명령 추종 서버 기반 추론 성능을 위한 Granite 3.1 8B의 기준 버전과 양자화 버전을 비교하여 요청 속도(RPS)와 요청 지연 시간을 비교합니다.

#### 1.4.2 대용량 요청

**수행 평가**
* 압축 모델은 검색 증강 생성(RAG)이나 요약 워크플로(프롬프트 토큰 4,096개, 출력 토큰 512개)와 같은 대용량 요청에 대해, 비슷한 성능 이점을 제공

<img src="./images/compressed_granite_3.1_requests_per_second_for_large.webp" title="100px" alt="압축된 granite 3.1 모델 대용량 요청 처리 성능"/>

* Single Stream, Latency
  + W4A16은 A5000 대비 2.4배, A100 대비 1.7배 낮은 지연 시간으로 최고의 효율성을 달성
* Multi-Stream
  + W8A8 모델은 최고의 성능을 제공하여 동일한 성능에서 A5000 대비 최대 4배, A100 대비 최대 3배 더 많은 요청을 처리

> [!NOTE]
> 1xA5000 및 1xA100 GPU에서 RAG/Summarization 서버 기반 추론 성능을 위한 Granite 3.1 8B의 기준선 및 양자화 버전을 비교하여 요청 속도(RPS)와 요청 지연 시간을 비교합니다.
<br>
<br>

## 2. GGUF vs GGML

### 2.1 PT-Generated Unified Format(GGUF)란

GPT-Generated Unified Format(GGUF)은 대규모 언어 모델(LLM)의 사용 및 배포를 간소화하는 파일 형식입니다. GGUF는 추론 모델을 저장하고 소비자 등급 컴퓨터 하드웨어에서 우수한 성능을 발휘하도록 특별히 설계되었습니다.

**GGUF 특징**
* 효율적인 실행을 위해 모델 매개변수(가중치 및 편향)를 추가 메타데이터와 결합하여 이를 달성
* GGUF는 명확하고 확장 가능하며 다재다능하며 이전 모델과의 호환성을 깨지 않고도 새로운 정보를 통합
* GGUF는 이전 파일 형식인 GGML에서 구축한 기반을 바탕으로 한 최근 개발된 형식
  + 모델의 빠른 로딩 및 저장을 위해 명확하게 설계된 바이너리 형식
  + Python 및 R과 같은 다양한 프로그래밍 언어와 호환 (-> 이 때문에 GGUF는 형식의 인기를 더함)
  + 미세 조정을 지원하므로 사용자는 LLM을 특수 애플리케이션에 맞게 조정
  + 애플리케이션 간 모델 배포를 위한 프롬프트 템플릿을 저장
* GGML은 여전히 ​​사용되고 있지만 지원은 GGUF로 대체됨
<br>

### 2.2 GGUF와 GGML의 차이

#### 2.2.1 GGML의 배경 및 목적

**GGML의 배경**
* 개발자 Georgi Gerganov가 개발한 GGUF 바로 이전의 파일 형식
* GGML은 Gerganov의 이니셜(GG)과 머신러닝을 뜻하는 ML을 합친 것

**GGML의 목적**
* GGML은 다양한 하드웨어 플랫폼에서 고성능을 제공하도록 설계된 텐서 라이브러리
* OpenAI의 GPT 인공지능 모델에 대한 파일 형식을 개발하여 모델의 손쉬운 공유 및 실행을 용이하게 하려는 초기 시도
* GGML은 명확하고 모델을 로드하는 데 필요한 모든 정보를 포함하도록 설계
* 그러나 유연성과 확장성 측면에서 한계가 있었음
  + 즉, GGML은 수동 조정이 필요
  + 사용자가 GGML의 한계를 해결하기 위해 새로운 기능을 추가하면서 호환성 문제에 직면

#### 2.2.2 GGML을 개선한 GGUF

* GGML의 한계를 해결하고 기존 모델과의 호환성을 유지하면서 새로운 기능을 추가
* 기존 버전의 호환성 문제를 해결하여 최신 버전으로의 전환을 용이하게 하고 다양한 모델을 지원하여 포괄적인 솔루션을 제공

> [!NOTE]
> 기존 모델을 GGUF로 변환하는 데는 시간이 많이 걸릴 수 있습니다.
<br>

### 2.3 GGUF로 전환

**Huggingface**
* 자연어 처리(NLP) 도구와 모델을 제공하는 기업 및 커뮤니티 기반 플랫폼
* GGUF 파일 형식으로 변환 가능한 사전 학습된 여러 모델을 포함하는 트랜스포머 라이브러리를 제공
* 미세 조정 및 배포 기능도 지원

**트랜스포머**
* 현대 NLP의 중추가 된 모델 아키텍처의 한 유형
* GGUF는 이러한 고급 아키텍처를 사용하는 애플리케이션을 위해 트랜스포머 기반 모델의 저장 및 배포를 지원
<br>

### 2.4 GGUF 아키텍처

#### 2.4.1 GGUF의 특징

* 언어 모델을 위한 강력하고 유연하며 효율적인 형식을 제공
* 기존 형식의 한계를 해결하고 진화하는 기술 및 기법과의 호환성을 보장
* 향상된 유연성, 향상된 성능, 그리고 고급 양자화 및 배포 프레임워크 지원

#### 2.4.2 GGUF의 모델 가중치

* 모델 가중치는 머신러닝 모델이 학습하는 매개변수
* GGUF는 이러한 가중치를 효율적으로 저장하여 빠른 로딩 및 추론이 가능
* 모델 가중치에 적용되는 양자화 방식은 성능을 더욱 향상시키고 리소스 소비를 줄임

#### 2.4.3 모델 양자화

* 연속 신호를 가능한 값이 더 적은 디지털 형식으로 변환하는 프로세스
* 특히 리소스가 제한된 하드웨어의 효율성과 성능을 향상
* 모델 크기를 줄이고 추론 속도를 향상시킴
  + 양자화된 모델은 필요한 연산 능력을 줄여 에너지 소비를 줄임
* 따라서 GGUF는 전력 리소스가 제한된 에지 장치 및 모바일 플랫폼에 배포하는 데 매우 적합
* 예) GPTQ(생성적 사전 학습된 변환기를 위한 정확한 학습 후 양자화)
  + GPTQ는 복잡한 데이터를 더 간단한 형식으로 변환하여 LLM의 크기와 연산 요구량을 줄임
  + 이를 통해 메모리와 처리 능력이 낮은 장치에도 LLM을 배포

#### 2.4.4 GGUF 바이너리 특징

* 바이너리 설계 형식
  + 모델 로딩 및 저장 속도를 크게 향상시킴
  + 빠른 배포 및 추론이 필요한 애플리케이션에 효과적
  + 시간에 민감한 애플리케이션에서 사용자 경험이 향상
    - 예: 실시간 언어 변환 서비스와 대화형 AI 시스템
* 호환성
  + 저랭크 적응(LoRA), 양자화 저랭크 적응(QLoRA), 적응형 가중치 양자화(AWQ)와 같은 고급 튜닝 기술과 호환
  + 이를 기반으로 모델 성능과 리소스 활용을 더욱 최적화

#### 2.4.5 GGUF가 지원하는 양자화 수준

다양한 양자 수준을 지원하여 모델 정확도와 효율성의 균형을 유연하게 맞출 수 있습니다.

|$\color{lime}{\texttt{양자화 모델}}$|$\color{lime}{\texttt{설명}}$|
|:---:|:---|
|2비트 양자화|가장 높은 압축률을 제공하여 모델 크기와 추론 속도를 크게 줄임, 정확도에 영향을 미침|
|4비트 양자화|압축과 정확도의 균형을 맞춰 다양한 실용적인 응용 분야에 적합|
|8비트 양자화|적당한 압축률로 우수한 정확도를 제공하며, 다양한 응용 분야에서 널리 사용|
* 퀀트(Quants)는 모델 가중치에 적용되는 다양한 양자화 수준(예: 2비트, 4비트 또는 8비트 양자화)을 나타냄

#### 2.4.6 GPU 지원

* CUDA(Compute Unified Device Architecture) 지원
  + 병렬 컴퓨팅 플랫폼이자 애플리케이션 프로그래밍 인터페이스인 CUDA를 지원
* 모델이 가속 컴퓨팅 작업에 GPU를 사용하여 언어 모델의 계산 효율성과 속도를 향상

#### 2.4.7 Langchai과 통합

 * 언어 모델 개발 및 배포 프레임워크인 Langchain과 통합
 * GGUF 모델의 배포를 용이하게 하여 개발 환경 및 애플리케이션에서 효과적으로 사용
<br>

### 2.5 GGUF 모델 및 사용 사례

#### 2.5.1 대규모 언어 모델 Meta AI (LLaMA)

**Llama-2 / Llama-3**
* 텍스트 생성, 요약, 질문 답변을 포함한 자연어 처리(NLP) 작업을 위해 설계된 LLaMA 모델로 GGUF 사용
* LLaMA의 GGUF를 사용하면 고성능 GPU에서 보다 일반적인 소비자 등급 CPU에 이르기까지 다양한 하드웨어 구성에 배포 가능

#### 2.5.2 택스트 생성 webUI

* LLM을 사용하여 텍스트를 생성하고 모델 저장 및 추론에 GGUF를 사용
* GGUF의 유연성을 통해 사용자는 대규모 모델을 빠르게 로드하여 최소한의 대기 시간으로 텍스트 생성 작업을 수행

#### 2.5.3 KoboldCpp

* LLM을 로컬에서 실행하는 데 널리 사용되는 클라이언트
* 성능을 개선하려고 GGUF를 채택
<br>

### 2.6 커뮤니티 및 에코시스템

|$\color{lime}{\texttt{이름}}$|$\color{lime}{\texttt{설명}}$|
|:---:|:---|
|llama.cpp|<ul><li>변환 유틸리티 및 실행 중인 모델에 대한 지원을 포함</li><li>GGUF로 작업하기 위한 도구를 제공하는 핵심 라이브러리</li></ul>|
|ctransformer|<ul><li>GGUF 모델을 통합할 수 있도록 다양한 프로그래밍 환경 지원</li><li>개발자가 애플리케이션에서 이러한 모델을 더 쉽게 사용</li></ul>|
|LoLLMS Web UI|<ul><li>GGUF를 지원하는 웹 기반 인터페이스</li><li>사용자 친화적인 인터페이스를 통해 모델과 상호 작용할</li></ul>|
<br>
<br>

<hr>

[차례](../README.md)
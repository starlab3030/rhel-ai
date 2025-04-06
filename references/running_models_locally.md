# Podman Desktop을 통해 모델을 로컬에서 실행

**차례**
1. []()<br>
2. []()<br>
3. []()<br>
4. []()<br>
<br>
<br>


## 1. Podman AI 랩

### 1.1 모델 테스트를 위한 Podman AI Lab

* 모델 선택 후에는, 워크스테이션에서 실행하고 테스트 필요
* 이를 위한 방법으로 Podman AI 랩 사용
* Podman Desktop 확장 프로그램으로, 메모리가 제한된 환경에서 컨테이너화된 AI 애플리케이션과 모델을 실행
* Podman AI Lab은 특히 노트북과 같은 로컬 워크스테이션에서 대규모 모델을 실행하려는 개발자에게 유용
<br>

### 1.2 지원하는 LLM

#### 1.2.1 Podman AI Lab과 llama.cpp

* 큰 크기와 관련된 사용 제한을 극복하기 위해 대규모 언어 모델(LLM)에 중점을 둠
* Podman AI Lab은 비가속 소비자 하드웨어에서 LLM을 실행할 수 있도록 llama.cpp를 사용

#### 1.2.2 llama.cpp

* 다양한 하드웨어에서 양자화된 모델을 실행하도록 최적화된 LLM용 추론 런타임
  + 주요 목표는 값비싼 컴퓨팅 가속기를 사용할 수 없는 사용자가 LLM에 더 쉽게 액세스할 수 있도록 하는 것
  + 이 런타임 라이브러리를 사용하면 개발자 워크스테이션이나 엣지 장치를 포함한 광범위한 장치에서 LLM을 사용 가능
* GPT-Generated Unified Format(GGUF)에 저장된 양자화된 모델을 실행

#### 1.2.3 GPT-Generated Unified Format (GGUF) 

* llama.cpp를 위해 특별히 설계되었으며 모델을 단일 파일에 캡슐화
* GGUF 모델 파일은 다음과 같이 모델 특성을 설명하는 명명 패턴을 사용
  ```
  BaseName-Size-FineTune-Version-Encoding-Type.gguf
  ```
  |$\color{lime}{\texttt{필드}}$|$\color{lime}{\texttt{설명}}$|
  |:---:|:---:|
  |BaseName|`granite`과 같이 모델 기본 유형이나 아키텍처를 설명하는 이름|
  |Size|매개변수 번호에 대한 반올림된 소수점 뒤에 지수를 나타내는 문자<br>  예1) 120M은 1억 2천만 개의 매개변수<br>  예2) 7B는 70억 개의 매개변수<br>  예3) 전문가 혼합(MoE) 모델은 매개변수 번호 앞에 전문가 수를 추가한 다음 x를 붙임|
  |FineTune|모델이 훈련받은 작업이나 접근 방식을 나타내는 키워드(예: chat, instruct, lab)|
  |Version (옵션)|vMajor.Minor 형식의 버전 문자열|
  |Encoding|Q4_K_M과 같은 양자화 유형|
  |Type (옵션)|GGUF 파일의 유형|
* 모델 이름 예: merlinite-7b-lab-Q4_K_M.gguf
  + BaseName: Merlinite
  + Size: 7B(billion) 패러미터
  + FineTune 태스크: LAB (Large-scale Alignment for chatBots)
  + Encoding Scheme: Q4_K_M

> [!NOTE]
> Podman AI Lab은 Hugging Face의 GGUF 형식으로 LLM의 기본 카탈로그를 제공합니다. 이러한 모델에 대한 자세한 내용을 보려면 Hugging Face 모델 카드를 방문하면 됩니다.

#### 1.2.4 다른 모델 타입 지원

Podman AI Lab은 ResNet 및 Whisper와 같은 LLM이 아닌 모델도 제공
* 그러나 이러한 모델에 대한 지원은 여전히 ​​제한적
* 예를 들어, Podman AI Lab을 사용하여 ResNet을 다운로드할 수는 있지만 실행할 수는 없음
<br>
<br>

## 2. Podman Desktop AI Lab

### 2.1 모델 다운로드

모델을 다운로드하려면 AI Lab 메뉴에서 Catalog를 클릭합니다. 그런 다음 목록에서 사용 가능한 모델을 선택하고 Download 버튼을 클릭합니다. Podman AI Lab은 각 모델을 실행하는 데 필요한 RAM의 추정치를 제공합니다.


<br>

### 2.2 양자화된 모델 실행


<br>

### 2.3 모델 실행


<br>

### 2.4 


<br>
<br>

## 4. 



<br>
<br>

## 5. 


<br>
<br>

<hr>

[차례](../README.md)
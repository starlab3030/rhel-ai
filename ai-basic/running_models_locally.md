# Podman Desktop을 통해 모델을 로컬에서 실행

**차례**
1. [Podman AI Lab 개요](running_models_locally.md#1-podman-ai-랩-개요)<br>
2. [Podman Desktop AI Lab 설명](running_models_locally.md#2-podman-desktop-ai-lab-설명)<br>
<br>
<br>


## 1. Podman AI 랩 개요

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

## 2. Podman Desktop AI Lab 설명

### 2.1 AI Lab의 모델 작업을 위한 메뉴

#### 2.1.1 Catalog

**모델 카탈로그**
* 다운로드하여 실행할 수 있는 모델 목록 제공
  + 기본적으로 여러 개의 오픈 소스 모델을 포함
  + 이러한 모델의 대부분은 GGUF 형식으로 양자화되어 워크스테이션에서 실행 가능
* 카탈로그에 자체 모델을 가져올 수도 있음

#### 2.1.2 Services

**모델 서비스**
* 추론 서버를 실행하는 컨테이너
* 모델을 실행하려면 다운로드한 모델로 다음 서비스를 만들어야 함
  + 이 서버는 모델을 실행하고 노출
* 모델은 필요한 서비스를 지시
  + 예를 들어, 모든 GGUF 모델은 llama.cpp 서비스를 사용
  + 서비스 섹션에는 만든 서비스가 나열됨

#### 2.1.3 Playgrourds

**모델 플레이그라운드**
* Podman Desktop에 내장된 채팅 창
* 이를 통해 서비스에 연결하고 모델을 실험
* 플레이그라운드 섹션에는 사용자가 만든 놀이터가 나열

> [!NOTE]
> Podman AI는 UI를 포함한 AI 애플리케이션을 만드는 데 필요한 템플릿인 레시피도 제공합니다.
<br>

### 2.2 모델 다운로드

<img src="./images/podman-desktop-model-download.png" title="100px" alt="모델 다운로드"/>

* AI Lab 메뉴에서 Catalog를 클릭
* 목록에서 사용 가능한 모델을 선택하고 Download 버튼을 클릭
* 각 모델을 실행하는 데 필요한 RAM의 추정치를 제공

**Podman AI Lab은 모델 파일**
* ~/.local/share/containers/podman-desktop/extensions-storage/redhat.ai-lab/models에 다운로드
* 기본 카탈로그에 포함된 대부분의 모델은 GGUF 형식의 양자화된 LLM
* ResNet과 같은 다른 기본 모델은 LLM이 아니며 PyTorch와 같은 다른 형식으로 다운로드
<br>

### 2.3 모델 실행

다운로드한 LLM을 실행하기 위해 서비스 생성
<img src="./images/podman-desktop-model-service.png" title="100px" alt="모델 다운로드"/>
 
* 서비스 생성
  + 다운로드한 모델에서 Create Model Service(rocket) 버튼을 클릭하여 서비스 생성
  + 또는 AI Lab 메뉴에서 Services를 클릭한 다음 New Model Service를 클릭하고 배포하려는 모델을 선택
* Podman AI Lab은 모델에 필요한 서비스 유형을 자동으로 선택
  + GGUF 형식의 LLM은 llama.cpp 서비스 백엔드를 사용
  + 실행 순서
    - 이 서비스를 실행하기 위해 Podman Desktop은 ghcr.io/containers/llamacpp_python 이미지로 컨테이너를 생성
    - 컨테이너의 /models 디렉터리에 모델 파일을 마운트
    - 이 컨테이너는 마운트된 모델을 실행
    - OpenAI 호환 API를 통해 노출하는 llama.cpp의 HTTP 서버를 실행
<br>

### 2.4 모델 서비스 조사

서비스 세부 정보 열기를 클릭하여 세부 정보 확인
<img src="./images/podman-desktop-model-service-detail-info.png" title="100px" alt="모델 서비스 상세 정보"/>

* 컨테이너 ID, 엔드포인트, 서비스가 실행 중인 모델과 같은 기본 정보를 제공
* 이 페이지는 또한 여러 언어로 된 예제 클라이언트 코드를 제공
  + 서비스에 요청을 하려면 선택한 언어로 예제 코드를 복사하여 실행
* 제공된 코드를 사용하지 않으려면 플레이그라운드를 만들어 모델 서비스를 테스트
  + 플레이그라운드를 만들려면 플레이그라운드를 클릭한 다음 새 플레이그라운드를 클릭
  + 플레이그라운드는 모델과 상호 작용하는 데 사용할 수 있는 채팅 인터페이스를 제공
<br>

### 2.5 모델 서비스 모니터링

**컨테이너로 실행되는 모델 서비스 모니터링**
* 일반 podman CLI 명령이나 Podman Desktop을 사용하여 검사하고 모니터링
* CLI를 통한 모니터링
  + podman logs, podman inspect, podman stats와 같은 명령을 사용
  + 로그를 보고, 컨테이너를 검사하고, 리소스 소비를 각각 모니터링
* Podman Desktop의 컨테이너 섹션
  <img src="./images/podman-desktop-container-summary.png" title="100px" alt="모델 서비스 모니터링"/>
  + 모델 서비스의 컨테이너를 검사
  + 컨테이너 세부 정보 페이지에는 컨테이너 로그와 세부 정보를 볼 수 있는 다양한 탭 제공
    - 이 페이지에는 실시간 CPU 및 메모리 소비도 표시
<br>
<br>

<hr>

[차례](../README.md)
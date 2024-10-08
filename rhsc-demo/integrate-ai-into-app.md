# AI를 보험 앱에 통합하기

이전 섹션에서는 InstructLab과 상호 작용하는 방법의 기본 사항을 보여주었습니다. 이제 예제 애플리케이션과 함께 InstructLab을 사용하여 한 단계 더 나아가 보겠습니다.
* RHEL AI를 사용하여 granite LLM을 활용
* 지식(knowledge) 및/또는 기술(skills) 형태로 추가 데이터를 더함
* 새로운 지식으로 모델을 학습
* 질문에 효과적으로 답할 수 있게 함
이는 보험 청구를 처리하는 가상 회사인 파라솔(parasol)의 맥락에서 수행됩니다.
<br>

**파라솔(parasol) 보험 시나리오**
파라솔에는 제출된 청구에 대한 수리 제안을 제공하는 AI(granite 모델)가 주입된 챗봇 애플리케이션이 있습니다.
* 목표
  - 이를 통해 파라솔은 보류 중인 다양한 청구를 신속하게 처리 가능
* 문제점 (Pain-Points / Challenges)
  - 하지만 현재 챗봇은 효과적인 수리 제안을 제공하지 않음
* 개선 방안
  - 여러가지 조건에서 수행된 다양한 수리를 포함하는 과거 청구 데이터를 사용하여 사용자가 이 지식을 granite 모델에 추가
  - 추가된 지식으로 모델을 학습
  - 권장 사항을 개선
<br>

## 파라솔 앱 사용

먼저 클레임 담당자가 챗봇과 상호작용할 때의 현재 경험을 살펴보겠습니다.

### 1. *Parasol*로 전환하여 브라우저에서 파라솔 회사의 클레임 신청서를 확인

<img src="images/parasol-view.png" title="100px" alt="파라솔_뷰"></img><br>
* 청구 담당자는 화면에서 청구 번호를 클릭하여 기존 청구를 탐색하고 볼 수 있음

### 2. *Marty McFly*가 제기한 청구인 **CLM195501**을 조사

해당 청구를 클릭
<img src="images/parasol-claim.png" title="100px" alt="파라솔_청구건_확인"></img><br>

* 이 페이지에서 청구 내용을 자세히 읽을 수 있음
* DeLorean 이미지를 확대하면 *Marty*가 자신의 차를 얼마나 심하게 파손했는지 확인할 수 있음
  - 바닥의 플럭스 커패시터에 주목

### 3. 챗봇 확인

청구를 읽은 후 페이지 오른쪽 하단에 있는 작은 파란색 아이콘을 사용하여 챗봇을 클릭

<img src="images/parasol-chat.webp" title="100px" alt="파라솔_챗"></img><br>

> [!NOTE]
> 챗봇은 이전에 제공한 Granite 모델에 의해 지원되므로 실행 중인 프로세스를 종료한 경우 다음을 실행하여 터미널에서 다시 시작해야 합니다.

### 4. 챗봇에 질문하기

청구 담당자로서 *Marty*의 DeLorean에서 플럭스 커패시터를 수리하는 데 드는 비용이 얼마인지 알고 싶다고 가정해 보겠습니다. 챗봇에 다음과 같이 입렵합니다.
```
How much does it cost to repair a flux capacitor?
```
<img src="images/parasol-chat-response.png" title="100px" alt="파라솔_챗봇_답변"></img><br>

> [!NOTE]
> 랩에서 한 것은, Prompt Engineering을 사용하여 LLM과의 각 대화에서 청구에 대한 맥락적 정보를 제공하는 것입니다. 하지만 안타깝게도 챗봇은 플럭스 커패시터를 수리하는 데 드는 비용이나 우리 조직의 도메인별 지식을 알지 못합니다.<br>
> <br>
> InstructLab과 RHEL AI를 사용하면 모델을 학습시켜 이를 바꿀 수 있습니다!
<br>

## 텍소노미(Taxonomy) 이해하기

InstructLab은 LLM에 대한 새로운 합성 데이터 기반 정렬 튜닝 방법을 사용합니다. InstructLab의 "**LAB**"은 대규모 채팅 봇 정렬(**L**arge-scale **A**lignment for Chat**B**ots)을 의미합니다. LAB 방법은 주로 수동으로 신중하게 생성되는 택소노미(taxonomy)에 의해 구동됩니다.

InstructLab은 새로운 *InstructLab* 오픈 소스 커뮤니티에서 지식(knowledge)과 기술(skills)이라는 두 가지 유형의 데이터를 수집하여 모델을 튜닝하고 개선하는 프로세스를 크라우드소싱합니다. 이러한 제출물은 합성 데이터 생성 프로세스에 사용되는 YAML 파일의 택소노미(taxonomy)에 수집됩니다.

택소노미(taxonomy)의 디렉토리 구조를 이해하는 데 도움이 되도록 다음 이미지를 참조하세요.

<img src="images/taxonomy.png" title="100px" alt="택소노미 구조"></img><br>

이제 분류 모델(taxonomy model)을 활용하여 조직의 공개(및 비공개) 내부 데이터 컬렉션에서 다루는 특정 차량과 그 세부 정보에 대한 모델 지식을 가르칠 것입니다.

### 1. 택소노미(taxonomy) 디렉터리 확인

```bash
cd ~/instructlab/
tree -F -L 1 taxonomy/
```

실행 결과
```
[instruct@bastion ~]$ cd ~/instructlab/

[instruct@bastion instructlab]$ tree -F -L 1 taxonomy/
taxonomy/
├── CODE_OF_CONDUCT.md
├── compositional_skills/
├── CONTRIBUTING.md
├── CONTRIBUTOR_ROLES.md
├── docs/
├── foundational_skills/
├── governance.md
├── knowledge/
├── LICENSE
├── MAINTAINERS.md
├── Makefile
├── README.md
├── scripts/
└── SECURITY.md

5 directories, 9 files
[instruct@bastion instructlab]$ tree -F -L 2 taxonomy/
taxonomy/
├── CODE_OF_CONDUCT.md
├── compositional_skills/
│   ├── arts/
│   ├── engineering/
│   ├── geography/
│   ├── grounded/
│   ├── history/
│   ├── linguistics/
│   ├── miscellaneous_unknown/
│   ├── philosophy/
│   ├── religion/
│   ├── science/
│   └── technology/
├── CONTRIBUTING.md
├── CONTRIBUTOR_ROLES.md
├── docs/
│   ├── assets/
│   ├── contributing_via_GH_UI.md
│   ├── knowledge-contribution-guide.md
│   ├── KNOWLEDGE_GUIDE.md
│   ├── README.md
│   ├── SKILLS_GUIDE.md
│   ├── taxonomy_diagram.md
│   ├── taxonomy_diagram.png
│   ├── template_qna.yaml
│   └── triaging/
├── foundational_skills/
│   └── reasoning/
├── governance.md
├── knowledge/
│   ├── arts/
│   ├── engineering/
│   ├── geography/
│   ├── history/
│   ├── linguistics/
│   ├── mathematics/
│   ├── miscellaneous_unknown/
│   ├── philosophy/
│   ├── religion/
│   ├── science/
│   └── technology/
├── LICENSE
├── MAINTAINERS.md
├── Makefile
├── README.md
├── scripts/
│   ├── check-yaml.py*
│   └── requirements.txt
└── SECURITY.md

30 directories, 19 files
[instruct@bastion instructlab]$ 
```

### 2. 디렉터리 생성

Instructlab에서 지식을 올바르게 생성하는 방법을 보여주기 위해, 새로운 지식을 추가할 디렉토리를 만듭니다.
```bash
mkdir -pv ~/instructlab/taxonomy/knowledge/parasol/claims
tree -F ~/instructlab/taxonomy/knowledge/parasol/
```

실행 결과
```
(venv) [instruct@bastion instructlab]$ mkdir -pv ~/instructlab/taxonomy/knowledge/parasol/claims
mkdir: created directory '/home/instruct/instructlab/taxonomy/knowledge/parasol'
mkdir: created directory '/home/instruct/instructlab/taxonomy/knowledge/parasol/claims'

(venv) [instruct@bastion instructlab]$ tree -F ~/instructlab/taxonomy/knowledge/parasol/
/home/instruct/instructlab/taxonomy/knowledge/parasol/
└── claims/

1 directory, 0 files

(venv) [instruct@bastion instructlab]$
```

### 3. 새로운 지식을 통해 모델에 새로운 기능을 추가

택소노미(taxonomy) 접근 작업이 작동하는 방식
* 질문과 답변의 샘플 데이터 세트가 포함된 ***qna.yaml***이라는 파일을 제공
* 이 데이터 세트는 모델의 출력에 완전히 영향을 미칠 만큼 많은 합성 데이터 예제를 만드는 과정에서 사용

***qna.yaml*** 파일
* 중요한 점은 InstructLab에서 합성적으로 더 많은 예제를 생성하기 위해, 이 파일이 특정 스키마를 따라야 함
* 해당 파일은 택소노미 디렉토리의 knowledge 하위 디렉토리 내의 폴더(~/taxonomy/knowledge/parasol/)에 저장
  - 데이터 토픽과 일치하는 적절한 이름의 폴더에 저장

### 4. 정보 입력

많은 정보를 직접 입력하는 대신 다음 명령을 실행하여 예시 ***qna.yaml*** 파일을 분류(taxonomy) 디렉토리에 복사
```bash
ls -lh ~/files/qna.yaml
yq -y . ~/files/qna.yaml
cp -av ~/files/qna.yaml ~/instructlab/taxonomy/knowledge/parasol/claims/
```

실행 결과
```
(venv) [instruct@bastion instructlab]$ ls -lh ~/files/qna.yaml 
-rw-r--r--. 1 instruct users 1.5K Oct  7 07:28 /home/instruct/files/qna.yaml

(venv) [instruct@bastion instructlab]$ yq -y . ~/files/qna.yaml 

...<snip>...

(venv) [instruct@bastion instructlab]$ cp -av ~/files/qna.yaml ~/instructlab/taxonomy/knowledge/parasol/claims/
'/home/instruct/files/qna.yaml' -> '/home/instruct/instructlab/taxonomy/knowledge/parasol/claims/qna.yaml'

(venv) [instruct@bastion instructlab]$ ls -lh ~/instructlab/taxonomy/knowledge/parasol/claims/qna.yaml 
-rw-r--r--. 1 instruct users 1.5K Oct  7 07:28 /home/instruct/instructlab/taxonomy/knowledge/parasol/claims/qna.yaml

(venv) [instruct@bastion instructlab]$
```

qna.yaml 파일
```yaml
created_by: Marty_McFly
domain: parasol
seed_examples:
  - answer: The DeLorean was manufactured from 1981 to 1983.
    question: When was the DeLorean manufactured?
  - answer: The DeLorean Motor Company manufactured the DeLorean DMC-12.
    question: Who manufactured the DeLorean DMC-12?
  - answer: Transmission Repair costs between $2,500 and $4,000 for the Delorean DMC-12.
    question: How much does it cost to repair the transmission on a DeLorean DMC-12?
  - answer: The top speed of the DeLorean DMC-12 was 110MPH and the 0-60 time was
      approximately 8.8 seconds.
    question: How fast was the Delorean DMC-12?
  - answer: The DeLorean DMC-12 weighs 2,712lb (1,230kg).
    question: How much does the DeLorean DMC-12 weigh?
  - answer: Maintenance on a DeLorean DMC-12 includes regular oil changes every 3,000
      miles or 3 months, brake fluid change every 2 years, transmission fluid changes
      every 30,000 miles, coolant change every 2 years, and regularly checking the
      battery for corrosion and proper connection.
    question: What does maintenance for a DeLorean DMC12 look like?
  - answer: It costs between $800 and $1000 to repair the suspension on a DeLorean
      DMC-12.
    question: How much does it cost to repair the supension on a DeLorean DMC-12?
task_description: Details on instructlab community project
document:
  repo: https://github.com/gshipley/backToTheFuture.git
  commit: 8bd9220c616afe24b9673d94ec1adce85320809c
  patterns:
    - data.md
```
* 해당 파일은 학습 모델이 학생 모델을 가르치는 데 사용할 Q&A 예제 목록으로 구성된 YAML 파일
* 또한 git의 텍스트 파일에 대한 특정 커밋으로 연결되는 소스 문서도 있음
  - 여기에는 플럭스 커패시터가 저렴한 $10,000,000이라는 내용이 포함되어 있음

**qna.yaml 파일 스키마**
|$\color{lime}{\texttt{섹션}}$|$\color{lime}{\texttt{설명}}$|
|:---|:---|
|`created_by`|기여한 작성자로, 일반적으로 GitHub 사용자 이름|
|`domain`|지식(knowledge)의 범주|
|`seed_examples`|제공된 지식(knowledge) 문서에서 가져온 5개 이상의 예로 모델에 대한 **질문(question)**과 원하는 **응답(response)**을 나타냄|
|`task_description`|특정 지식(knowledge) 기여를 쉽게 이해하기 위한 선택적 설명|
|`document`|지식(knowledge) 마크다운 파일을 가리키는 **저장소(repo)** URL과 특정 파일을 포함하는 **커밋(commit)** SHA로 구성된 지식(knowledge) 기여의 소스|
|`patterns`|저장소(repository)에 있는 마크다운 파일을 지정하는 글로브 패턴 목록|

### 5. 시드 데이터가 올바르게 큐레이션되었는지 확인

InstructLab을 사용하여, 추가 데이터를 생성하기 전에 택소노미(taxonomy) 파일을 검증할 수 있습니다.

ilab 택소노미 diff 명령을 사용하여 YAML 파일 검증
```bash
ilab taxonomy diff
```

실행 결과
```
(venv) [instruct@bastion instructlab]$ ilab taxonomy diff
knowledge/parasol/claims/qna.yaml
Taxonomy in taxonomy is valid :)

(venv) [instruct@bastion instructlab]$ 
```
<br>

## 합성 데이터 생성

<br>

## 모델 학습 및 제공

<br>

## 앱 검증

<br>
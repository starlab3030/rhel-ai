# Podman Desktop 

**차례**
1. 
2. 
3. 
<br>
<br>


## 1. RHEL에 Podman-Desktop 설치 및 구성

### 1.1 RHEL 구성 및 설치 준비

#### 1.1.1 리포지토리 설정

실행 명령어
```bash
subscription-manager repos --enable codeready-builder-for-rhel-9-$(arch)-rpms
dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm
```

실행 결과
```
[root@rhel94-pd ~]# subscription-manager repos --enable codeready-builder-for-rhel-9-$(arch)-rpms

[root@rhel94-pd ~]# dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm

...<snip>...

[root@rhel94-pd ~]#
```

#### 1.1.2 RDP 설치 및 구성

실행 명령어
```bash
dnf search xrdp
dnf install -y xrdp
```

실행 결과
```
[root@rhel94-pd ~]# dnf search xrdp
서브스크립션 관리 저장소를 최신화하기.
마지막 메타자료 만료확인(0:00:53 이전): 2025년 04월 05일 (토) 오후 04시 44분 14초.
========================= 이름과 정확히 일치하는 항목: xrdp =========================
xrdp.x86_64 : Open source remote desktop protocol (RDP) server
========================= 이름 & 요약과 일치하는 항목: xrdp =========================
xorgxrdp.x86_64 : Implementation of xrdp backend as Xorg modules
xorgxrdp-glamor.x86_64 : Implementation of xrdp backend as Xorg modules with glamor
xrdp-devel.x86_64 : Headers and pkg-config files needed to compile xrdp backends
xrdp-selinux.x86_64 : SELinux policy module required tu run xrdp

[root@rhel94-pd ~]# dnf install -y xrdp

...<snip>...

[root@rhel94-pd ~]#
```

#### 1.1.3 방화벽 설정

실행 명령어
```bash
sudo firewall-cmd --add-port=3386/tcp --permanent
sudo firewall-cmd --reload
```

실행 결과
```
[root@rhel94-pd ~]# sudo firewall-cmd --add-port=3386/tcp --permanent
success

[root@rhel94-pd ~]# sudo firewall-cmd --reload
success

[root@rhel94-pd ~]#
```

#### 1.1.4 RDP 서비스 시작 및 활성화

실행 명령어
```bash
systemctl enable xrdp
systemctl start xrdp
```

실행 결과
```
[root@rhel94-pd ~]# systemctl enable xrdp
Created symlink /etc/systemd/system/multi-user.target.wants/xrdp.service → /usr/lib/systemd/system/xrdp.service.

[root@rhel94-pd ~]# systemctl start xrdp

[root@rhel94-pd ~]#
```
<br>

### 1.2 Podman-Desktop 설치

#### 1.2.1 *FlatHub* 리포지토리 추가 및 활성화

실행 결과
```bash
flatpak remote-add --if-not-exists --user flathub https://flathub.org/repo/flathub.flatpakrepo
```

실행 명령어
```
[root@rhel94-pd ~]# flatpak remote-add --if-not-exists --user flathub https://flathub.org/repo/flathub.flatpakrepo

[root@rhel94-pd ~]#
```

#### 1.2.2 Podman Desktop 설치

실행 명령어
```bash
flatpak install --user flathub io.podman_desktop.PodmanDesktop
```

실행 결과
```
[root@rhel94-pd ~]# flatpak install --user flathub io.podman_desktop.PodmanDesktop
Looking for matches…
Required runtime for io.podman_desktop.PodmanDesktop/x86_64/stable (runtime/org.freedesktop.Platform/x86_64/24.08) found in remote flathub
Do you want to install it? [Y/n]: y

io.podman_desktop.PodmanDesktop permissions:
    ipc                   network              x11      dri
    file access [1]       dbus access [2]

    [1] /run/docker.sock, home, xdg-run/containers/auth.json, xdg-run/podman:create
    [2] org.freedesktop.Flatpak, org.freedesktop.Notifications,
        org.freedesktop.secrets, org.kde.StatusNotifierWatcher, org.kde.kwalletd6


        ID                                  Branch     Op Remote  Download
 1. [✓] org.freedesktop.Platform.GL.default 24.08      i  flathub 156.3 MB / 156.8 MB
 2. [✓] org.freedesktop.Platform.GL.default 24.08extra i  flathub  25.2 MB / 156.8 MB
 3. [✓] org.freedesktop.Platform.Locale     24.08      i  flathub   2.4 MB / 380.4 MB
 4. [✓] org.freedesktop.Platform.openh264   2.5.1      i  flathub 913.7 kB / 971.4 kB
 5. [✓] org.freedesktop.Platform            24.08      i  flathub 210.8 MB / 264.5 MB
 6. [✓] io.podman_desktop.PodmanDesktop     stable     i  flathub 133.6 MB / 140.0 MB

Installation complete.

[root@rhel94-pd ~]#
```

#### 1.2.3 Podman-Desktop 설치 확인

실행 명령어
```bash
flatpak run io.podman_desktop.PodmanDesktop --no-sandbox
```

실행 결과
```
[root@rhel94-pd ~]# flatpak run io.podman_desktop.PodmanDesktop
[0405/171736.869730:FATAL:electron_main_delegate.cc(288)] Running as root without --no-sandbox is not supported. See https://crbug.com/638180.
/app/bin/run.sh: 줄 3:     3 추적/중단점 함정 (코어 덤프됨) zypak-wrapper.sh /app/main/podman-desktop "$@"

[root@rhel94-pd ~]# flatpak run io.podman_desktop.PodmanDesktop --no-sandbox
[3:0405/171812.944298:ERROR:bus.cc(407)] Failed to connect to the bus: Failed to connect to socket /run/dbus/system_bus_socket: 그런 파일이나 디렉터리가 없습니다
Gtk-Message: 17:18:13.807: Failed to load module "canberra-gtk-module"
Gtk-Message: 17:18:13.807: Failed to load module "pk-gtk-module"
Gtk-Message: 17:18:13.809: Failed to load module "canberra-gtk-module"
Gtk-Message: 17:18:13.809: Failed to load module "pk-gtk-module"

...<snip>...

Activating extension (podman-desktop.podman) ended in 437 milliseconds
Activating extension (podman-desktop.registries) with max activation time of 20 seconds
Activating extension (podman-desktop.registries) ended in 1 milliseconds
PluginSystem: initialization done.
Autostarting podman-desktop.podman container engine
[kind] kind extension is active
[kind] kind extension is active
[podman] Podman extension: Could not find the socket at /run/user/0/podman/podman.sock after 5s. The command podman system service --time=0 did not work to start the podman socket.

[root@rhel94-pd ~]#
```

#### 1.2.4 Podman-Desktop 실행 확인

<img src="./images/podman-desktop.png" title="100px" alt="포드맨-데스크탑"></img>
<br>

### 1.3 Podman AI Extension 설치

#### 1.3.1 AI Lab 설치

포드맨 AI 랩 설치 후 확인

<img src="./images/podman-ai-lab.png" title="100px" alt="포드맨 AI 랩"></img>

#### 1.3.2 AI 랩의 **Catalog** 

다운로드하여 실행할 수 있는 모델 목록
<img src="./images/ai-lab-models-catalog.png" title="100px" alt="모델 확인 및 다운로드"></img>

* 포드맨 AI Lab에는 기본적으로 여러 개의 오픈 소스 모델이 포함
* 이러한 모델의 대부분은 GGUF 형식으로 양자화되어 워크스테이션에서 실행 가능
* 카탈로그에 자체 모델을 가져올 수도 있음


#### 1.3.3 AI 랩의 **Services**

모델을 실행하려면 먼저 모델을 다운로드한 다음 서비스를 만들어야 함
<img src="./images/ai-lab-models-service.png" title="100px" alt="서비스 중인 모델"></img>

* 모델 서비스는 추론 서버를 실행하는 컨테이너
* 이 서버는 모델을 실행하고 노출
* 모델은 필요한 서비스를 지시
  + 예를 들어, 모든 GGUF 모델은 llama.cpp 서비스를 사용
  + 서비스 섹션에는 만든 서비스가 나열

> [!NOTE]
> 포드맨 AI 랩은 아직 ResNet을 위한 서비스를 제공하지 않음

#### 1.3.4 AI 랩의 **Playgrouds**

Playgroud는 Podman Desktop에 내장된 채팅 창
<img src="./images/ai-lab-models-playgrouds.png" title="100px" alt="실행 중인 채팅을 위한 플레이그라운드 나열"></img>

* 이를 통해 서비스에 연결하고 모델을 실험 가능
* Podman AI의 *playgroud* 섹션에는 사용자가 만든 놀이터가 나열

> [!NOTE]
> 포드맨 AI는, 또한, UI를 포함한 AI 앱 생성을 위한 템플릿인 레시피를 제공합니다.
<br>

### 1.4 모델 관리

#### 1.4.1 모델 다운로드

<img src="./images/podman-desktop-model-download.png" title="100px" alt="모델 다운로드"></img>

*  ~/.local/share/containers/podman-desktop/extensions-storage/redhat.ai-lab/models에 다운로드
* 기본 카탈로그에 포함된 대부분의 모델은 GGUF 형식의 양자화된 LLM
* ResNet과 같은 다른 기본 모델은 LLM이 아니며 PyTorch와 같은 다른 형식으로 다운로드
* 모델 파일을 다운로드한 후 모델 서비스를 만들거나 파일 시스템에서 모델 파일을 볼 수 있음

#### 1.4.2 다운로드한 모델 확인

실행 명령어
```bash
tree -F .local/share/containers/podman-desktop/extensions-storage/redhat.ai-lab/
```

실행 결과
```
[root@rhel94-pd ~]# tree -F .local/share/containers/podman-desktop/extensions-storage/redhat.ai-lab/
.local/share/containers/podman-desktop/extensions-storage/redhat.ai-lab/
└── models/
    └── hf.ibm-research.granite-3.2-8b-instruct-GGUF/
        └── granite-3.2-8b-instruct-Q4_K_M.gguf

2 directories, 1 file

[root@rhel94-pd ~]# 
```

#### 1.4.3 모델 실행

**다운로드한 LLM 실행을 위해 서비스 생성**
<img src="./images/podman-desktop-model-service.png" title="100px" alt="모델 서비스"></img>

* 다운로드한 모델에서 ***Create Model Service(rocket)*** 버튼을 클릭하여 서비스를 만듦
* 또는 AI Lab 메뉴에서 Services를 클릭한 다음 New Model Service를 클릭하고 배포하려는 모델을 선택
* Podman AI Lab은 모델에 필요한 서비스 유형을 자동으로 선택
* GGUF 형식의 LLM은 llama.cpp 서비스 백엔드를 사용
  + 이 서비스를 실행하기 위해 Podman Desktop은 ghcr.io/containers/llamacpp_python 이미지로 컨테이너를 만들고 컨테이너의 /models 디렉터리에 모델 파일을 마운트
  + 이 컨테이너는 마운트된 모델을 실행하고 OpenAI 호환 API를 통해 노출하는 llama.cpp HTTP 서버를 실행

**생성된 모델 확인**
<img src="./images/podman-desktop-model-service-created.png" title="100px" alt="모델 서비스"></img>

#### 1.4.4 모델 리스트 확인

<img src="./images/podman-desktop-model-service-list.png" title="100px" alt="모델 서비스 리스트"></img>

#### 1.4.5 모델 테스트

실행 명령어
```bash
curl --location 'http://localhost:41035/v1/chat/completions' --header 'Content-Type: application/json' --data '{
  "messages": [
    {
      "content": "You are a helpful assistant.",
      "role": "system"
    },
    {
      "content": "What is the capital of France?",
      "role": "user"
    }
  ]
}' | jq '.'
```

실행 결과
```
[seulee@rhel94-pd ~]$ curl --location 'http://localhost:41035/v1/chat/completions' --header 'Content-Type: application/json' --data '{
  "messages": [
    {
      "content": "You are a helpful assistant.",
      "role": "system"
    },
    {
      "content": "What is the capital of France?",
      "role": "user"
    }
  ]
}' | jq '.'
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   557  100   365  100   192    200    105  0:00:01  0:00:01 --:--:--   305
{
  "id": "chatcmpl-10b2d8b4-51c7-4ec2-b8f1-a4f64fec7a02",
  "object": "chat.completion",
  "created": 1743851990,
  "model": "/models/granite-3.2-8b-instruct-Q4_K_M.gguf",
  "choices": [
    {
      "index": 0,
      "message": {
        "content": "\nThe capital of France is Paris.",
        "role": "assistant"
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 60,
    "completion_tokens": 9,
    "total_tokens": 69
  }
}

[seulee@rhel94-pd ~]$ 
```

JSON 질의
```json
{
  "messages": [
    {
      "content": "You are a helpful assistant.",
      "role": "system"
    },
    {
      "content": "What is the capital of France?",
      "role": "user"
    }
  ]
}
```

JSON 응답
```json
{
  "id": "chatcmpl-10b2d8b4-51c7-4ec2-b8f1-a4f64fec7a02",
  "object": "chat.completion",
  "created": 1743851990,
  "model": "/models/granite-3.2-8b-instruct-Q4_K_M.gguf",
  "choices": [
    {
      "index": 0,
      "message": {
        "content": "\nThe capital of France is Paris.",
        "role": "assistant"
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 60,
    "completion_tokens": 9,
    "total_tokens": 69
  }
}
```

#### 1.4.6 모델 서비스 조사

**세부 정보**
<img src="./images/podman-desktop-model-service-detail-info.png" title="100px" alt="모델 서비스 조사"></img>

* 서비스 세부 정보 열기를 클릭하여 확인
* 서비스 세부 정보 페이지는 컨테이너 ID, 엔드포인트, 서비스가 실행 중인 모델과 같은 기본 정보를 제공
* 서비스에 요청을 하려면 선택한 언어로 예제 코드를 복사하여 실행
* ***Inference Endpoint URL***: 추론 모델 서비스 엔드포인트 URL
<br>

### 1.5 플레이그라운드

#### 1.5.1 플레이그라운드 생성

<img src="./images/ai-lab-models-playgrouds.png" title="100px" alt="모델 플레이그라운드 생성"></img>

* 제공된 코드를 사용하지 않으려면 플레이그라운드를 만들어 모델 서비스를 테스트할 수 있음
  + 플레이그라운드를 만들려면 플레이그라운드를 클릭한 다음 새 플레이그라운드를 클릭
  + 플레이그라운드는 모델과 상호 작용하는 데 사용할 수 있는 채팅 인터페이스를 제공

#### 1.5.2 플레이그라운드 리스트

<img src="./images/podman-desktop-model-playgroud-list.png" title="100px" alt="모델 플레이그라운드 리스트"></img>

#### 1.5.3 플레이그라운드 테스트

<img src="./images/podman-desktop-model-playgroud-test.png" title="100px" alt="모델 플레이그라운드 테스트"></img>

<br>

### 1.6 모델 서비스 모니터링

#### 1.6.1 컨테이너 리스트

<img src="./images/podman-desktop-container-list.png" title="100px" alt="컨테이너 리스트"></img>

#### 1.6.2 해당 컨테이너의 요약

<img src="./images/podman-desktop-container-summary.png" title="100px" alt="컨테이너 요약"></img>

#### 1.6.3 컨테이너 앱 YAML

<img src="./images/podman-desktop-container-kube.png" title="100px" alt="컨테이너 K8S 앱"></img>
<br>

### 1.7 모델 서비스에 질의 및 응답

#### 1.7.1 **~/model-query** 폴더 및 파일 리스트

[~/model-query](./src/model-query/) 폴더
```
[seulee@rhel94-pd ~]$ tree -F model-query/
app/
├── assistant.py
├── config.py
├── database.py
├── main.py
└── requirements.txt

1 directory, 5 files

[seulee@rhel94-pd ~]$
```

#### 1.7.2 **~/model-query/main.py** 주요 내용

[~/model-query/main.py](./src/model-query/main.py)
```py
query = generate_query(user_input) #1
click.secho(query, fg="cyan", italic=True)
result = run_query(query)
click.echo(result) #2
```
1. 사용자 요청을 읽고, SQL 문을 생성하는 *generate_query()*를 호출
2. SQL 문 실행을 위해 *run_query()*를 호출

#### 1.7.3 **~/model-query/assistant.py** 주요 내용

[~/model-query/assistant.py](./src/model-query/assistant.py)
```py
llm = OpenAI(base_url=model_url, api_key="not-needed", temperature=0.1) #1
prompt_template = PromptTemplate.from_template(template)

def generate_query(user_input: str):
    table_definitions = get_db_tables_schema()
    # TODO: add parameters
    prompt = prompt_template.invoke(
        {"tables": table_definitions, "user_input": user_input} #2
    )
    return llm.invoke(prompt)
```
1. **OpenAI()**에서 *base_url* 인수로 모델의 URL 전달
2. *tables*와 *user_input* 변수를 가지고 템플릿 제공

#### 1.7.4 파이썬 가상화 환경

실행 명령어
```bash
python -m venv .venv && source .venv/bin/activate
```

```실행 결과
[seulee@rhel94-pd ~]$ python -m venv .venv && source .venv/bin/activate

(.venv) [seulee@rhel94-pd ~]$
```

#### 1.7.5 필요한 패키지 설치

실행 명령어 - [~/model-query/requirements.txt](./src/model-query/requirements.txt)
```bash
pip install -r model-query/requirements.txt
```

실행 결과
```
(.venv) [seulee@rhel94-pd ~]$ pip install -r model-inquery/requirements.txt
Defaulting to user installation because normal site-packages is not writeable
Collecting aiohappyeyeballs==2.4.0
  Downloading aiohappyeyeballs-2.4.0-py3-none-any.whl (12 kB)
Collecting aiohttp==3.10.5
  Downloading aiohttp-3.10.5-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (1.2 MB)
     |████████████████████████████████| 1.2 MB 9.8 MB/s
Collecting aiosignal==1.3.1
  Downloading aiosignal-1.3.1-py3-none-any.whl (7.6 kB)

...<snip>...

  WARNING: Value for scheme.platlib does not match. Please report this to <https://github.com/pypa/pip/issues/10151>
  distutils: /home/seulee/.local/lib/python3.9/site-packages
  sysconfig: /home/seulee/.local/lib64/python3.9/site-packages
  WARNING: Additional context:
  user = True
  home = None
  root = None
  prefix = None
    Running setup.py install for dotenv-python ... done
Successfully installed GitPython-3.1.43 PyYAML-6.0.2 Pygments-2.18.0 SQLAlchemy-2.0.32 aiohappyeyeballs-2.4.0 
...<snip>...
typing-extensions-4.12.2 typing-inspect-0.9.0 urllib3-2.2.2 uvicorn-0.23.2 wheel-0.44.0 yarl-1.9.6

(.venv) [seulee@rhel94-pd ~]$
```

#### 1.7.6 데이터베이스 확인

실행 명령어
```bash
podman ps -a
podman start movies_db
podman ps -a
```

실행 결과
```
(.venv) [student@workstation app]$ podman ps -a
CONTAINER ID  IMAGE                                     COMMAND         CREATED      STATUS                     PORTS                   NAMES
3614639d4078  registry.redhat.io/rhel9/postgresql-13:1  run-postgresql  2 hours ago  Exited (0) 42 minutes ago  0.0.0.0:5432->5432/tcp  movies_db

(.venv) [student@workstation app]$ podman start movies_db
movies_db

(.venv) [student@workstation app]$ podman ps -a
CONTAINER ID  IMAGE                                     COMMAND         CREATED      STATUS        PORTS                   NAMES
3614639d4078  registry.redhat.io/rhel9/postgresql-13:1  run-postgresql  2 hours ago  Up 4 seconds  0.0.0.0:5432->5432/tcp  movies_db

(.venv) [student@workstation app]$ 
```

#### 1.7.7 데이터베이스 연결

실행 명령어
```bash
podman exec -it movies_db /bin/bash --
psql
\c
\list
\q
exit
```

실행 결과
```
(.venv) [student@workstation app]$ podman exec -it movies_db /bin/bash --
bash-5.1$ psql

postgres=# \c
You are now connected to database "postgres" as user "postgres".

postgres-# \list
                                 List of databases
   Name    |  Owner   | Encoding |  Collate   |   Ctype    |   Access privileges   
-----------+----------+----------+------------+------------+-----------------------
 movies    | student  | UTF8     | en_US.utf8 | en_US.utf8 | 
 postgres  | postgres | UTF8     | en_US.utf8 | en_US.utf8 | 
 template0 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
 template1 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
(4 rows)

postgres-# \q

bash-5.1$ exit
exit

(.venv) [student@workstation app]$ 
```

#### 1.7.8 데이터베이스 외부 연결

실행 명령어
```
podman exec movies_db   psql -U student -d movies   -c "SELECT title FROM Movies"
```

실행 결과
```
(.venv) [student@workstation app]$ podman exec movies_db   psql -U student -d movies   -c "SELECT title FROM Movies"
       title        
--------------------
 The Infinite Chase
 Parallel Universes
 Podman Forever
 The Silent Forest
 Quantum Paradox
(5 rows)

(.venv) [student@workstation app]$ 
```

#### 1.7.9 환경 변수 설정

실행 명령어
```bash
export MODEL_URL="http://localhost:41035/v1"
```

실행 결과
```
(.venv) [student@workstation app]$ export MODEL_URL="http://localhost:41035/v1"

(.venv) [student@workstation app]$ echo $MODEL_URL
http://localhost:41035/v1

(.venv) [student@workstation app]$ 
```

#### 1.7.10 데이터베이스에 질의 요청

실행 명령어
```bash
python main.py
Give me a list of movie titles
```

실행 결과
```
(.venv) [student@workstation app]$ python main.py
Movie Database Assistant. Type 'exit' to quit.

> Give me a list of movie titles

SELECT title FROM Movies;
+--------------------+
| title              |
+====================+
| The Infinite Chase |
+--------------------+
| Parallel Universes |
+--------------------+
| Podman Forever     |
+--------------------+
| The Silent Forest  |
+--------------------+
| Quantum Paradox    |
+--------------------+

> Give me a query to get the actors for the movie titled "Podman Forever".
SELECT Actors.name 
FROM Movies_Actors 
JOIN Movies ON Movies_Actors.movie_id = Movies.id 
JOIN Actors ON Movies_Actors.actor_id = Actors.id 
WHERE Movies.title = 'Podman Forever';
+------------+
| name       |
+============+
| Zara Quill |
+------------+
| Finn Lyric |
+------------+

> exit
Bye...

(.venv) [student@workstation app]$ 
```
* 질의에 대한 응답은 모델이 시간이 걸림

> [!NOTE]
> 사용된 모델은 특정 사용 사례에 미세 조정되지 않은 사전 학습된 코딩 LLM을 사용합니다. 예를 들어 모델이 쿼리에 소개 텍스트를 제공하거나 복잡한 조인 쿼리를 시도하는 경우 응용 프로그램이 실패할 수 있습니다.
<br>
<br>

## 2. 클라이언트 앱과 모델 연결

### 2.1 사전 훈련된 LLM 사용

사전 훈련된 LLM을 사용할 때, 자연어를 사용하여 LLM의 동작을 사용 사례에 맞게 조정 가능할 수 있습니다.
* LLM에 무엇을 해야 하는지 설명
* 어떻게 해야 하는지에 대한 맥락을 제공
* LLM에 응답에 필요한 톤이나 형식을 알림
<br>

### 2.2 프롬프트 엔진니어링

#### 2.2.1 프로픔트 엔진니어링

**프롬프트 엔진니어링**
* 쓰기 기법과 텍스트 패턴을 사용하여 LLM이 작업을 수행하도록 전문화하는 것
* LLM의 동작을 변경하는 가장 간단하고 저렴한 방법

**프롬프트**
* LLM에 대한 지침이나 질문이 포함된 텍스트 메시지
* 시스템 메시지나 시스템 프롬프트를 사용하여 LLM이 특정 방식으로 응답하도록 연결
* 시스템 메시지는 대화를 시작할 때 한 번 제공하는 프롬프트이며 이후 상호 작용을 위해 LLM을 구성

**프롬프트의 일반적인 구성 요소**
* 명확한 작업 설명 또는 질문
* 모델이 작업을 수행하는 데 도움이 되는 상황 정보
* 모델이 처리할 입력 데이터
* 톤이나 형식과 같은 출력 지침

#### 2.2.2 프롬프트 예

```
고대 그리스 철학의 맥락에서 #1
다음 인용문에 대한 설명을 제공하세요. #2

"나는 아테네인도 아니고 그리스인도 아니지만, 세계 시민입니다." #3

설명은 짧고 이해하기 쉬워야 합니다. #4
```
1. 맥락 정보
2. 과제 (태스크)
3. 입력 정보
4. 출력 지침

> [!NOTE]
> LLM은 비결정적이므로 LLM이 프롬프트의 지시를 완벽하게 따르지 않거나 거짓 진술이나 환각을 생성할 가능성이 있습니다. LLM은 아키텍처, 훈련 데이터 및 훈련 프로세스가 다릅니다.<br>
> 따라서 동일한 프롬프트 엔지니어링 기술이 다른 모델에서 다르게 수행될 수 있습니다. 프롬프트 엔지니어링이 잘 수행되지 않으면 벡터 데이터베이스와 검색 증강 생성(RAG) 아키텍처를 사용하거나 모델을 미세 조정하여 프롬프트의 컨텍스트 정보를 개선하는 것을 살펴볼 수 있습니다.
<br>

### 2.3 프롬프트를 정의한는 일반적인 패턴

#### 2.3.1 Persona Pattern 

* 모델에 역할을 채택하거나 특정 페르소나로 행동하도록 지시하여 LLM과의 상호 작용을 더 잘 맥락화
  + 예를 들어, *"당신은 전문 해양 생물학자입니다…​"*라고 하면 모델이 특정 지식과 어조를 사용
* 또한 페르소나를 사용하여 프롬프트의 대상을 맥락화
  + 예를 들어, *"제가 5살인 것처럼 설명해 주세요…​"*와 같은 문장은 모델이 명확하고 기술적이지 않은 응답을 생성하도록 안내

#### 2.3.2 Zero-shot / Few-shot prompts

프롬프트가 원하는 응답의 예를 제공하는지 여부
* Few-shot 프롬프트
  + 하나 이상의 예를 제공
  + LLM은 이를 일반화하여 새로운 작업을 수행하는 능력과 결합
* Zero-shot 프롬프트
  + 모델의 지식만 사용
  + 이 때문에 예가 없음
  
프롬프트 예 - LLM에 텍스트에서 특정 형식의 JSON으로 정보를 추출하는 방법을 알려줌
```
입력 문장이 주어지면 다음 형식의 JSON 객체를 생성합니다.
{"이름": "사람 이름", 취미: ["취미1", "취미2", ...]}

예: "영희는 하이킹, 음악, 고양이를 좋아합니다."
출력: {"이름": "영희", 취미: ["하이킹", "음악", "고양이"]}
예: "철수는 달리기를 좋아하지만 헬스장은 좋아하지 않습니다."
출력: {"이름": "철수", 취미: ["달리기"]}
```

#### 2.3.3 Chain of Thought (CoT)

**CoT 기술**
* LLM이 해결책을 찾을 수 있도록 잘 설명된 단계가 있는 샘플 문제를 제공
* 과제를 해결하기 위한 모델을 보여줌
* LLM이 일반적으로 어려움을 겪는 기본 산술 계산과 같은 구조화된 문제에 유용

CoT 예
```
주어진 옵션에서 목적지까지 가장 빠른 경로를 계산합니다.

옵션 A: 2시간 비행을 타고 55분 동안 걷습니다.
옵션 B: 6시간 기차를 타고 15분 동안 걷습니다.

경로를 선택하는 단계:
1. 모든 옵션의 시간 단위를 분으로 변환합니다.
2. 옵션의 분을 더합니다.
3. 분 수가 적은 옵션을 반환합니다.
```
* 이전 예시의 지침을 제거하면 모델은 가장 높은 번호의 옵션을 가장 느린 옵션으로 간주하여 옵션 B를 선택할 수 있음

#### 2.3.4 Prompt Format Patterns

**LLM은 텍스트의 구조를 이해**
* 일관된 구조로 프롬프트를 구성하면 프롬프트의 성능이 향상
* 일관성을 유지하는 한 마크다운, 글머리 기호, 번호 매기기 목록 또는 기타 임의의 형식을 사용 가능

예 - 다음 원샷 프롬프트에서 모델은 Q가 예제 입력에 사용되고 A가 예제 출력에 사용된다고 추론
```
# Task:
입력 국가가 주어지면 수도 이름으로 응답하세요.
# Output format:
출력 형식으로 JSON을 사용하여 응답하세요.
# Examples:
Q: 스페인
A: {"수도": "마드리드"}
```
<br>

### 2.4 모델 하이퍼-파라미터

**하이퍼파라미터 매개변수**
* LLM에 응답 길이를 제한하거나 응답 창의성을 구성하는 매개변수를 제공하여 LLM의 동작을 수정
* 추론 프로세스에 영향을 미치고 제어하기 위해 추론 요청의 일부로 보내는 구성 값

> [!NOTE]
> 추론을 위해 LLM을 구성하는 맥락에서 하이퍼파라미터라는 용어는 머신 러닝에서 모델을 학습하는 데 사용되는 매개변수와 다른 매개변수를 말합니다.

|$\color{lime}{\texttt{시스템}}$|$\color{lime}{\texttt{IP 주소}}$|
|:---|:---|
|Temperature|<ul><li>생성된 출력의 다양성을 제어</li><li>높은 값은 덜 일관된 출력을 생성할 위험이 있는 다양한 출력을 생성</li><li>낮은 값은 집중적이고 예측 가능한 출력을 생성</li><ul>|
|Top-p|텍스트를 생성할 때 단어 선택에 영향을 미침<br><ul><li>이 매개변수는 확률 범위에 있는 단어를 선택하는 값을 제공</li><li>예를 들어, 값 0.1은 상위 10% 확률에 있는 단어를 선택</li</ul>|
|Maximum tokens|모델이 생성할 수 있는 최대 토큰 수|

<br>

### 2.5 Podman AI Lab을 통한 모델 연결

<br>

### 2.6 LangChain을 통한 LLM 연결


<br>
<br>

------
[차례](../README.md)










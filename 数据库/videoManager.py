from moviepy import VideoFileClip
import os
import requests
import wave
import json
import psycopg2
from vosk import Model, KaldiRecognizer
from openai import OpenAI


# 语音识别模型
MODEL_PATH = "vosk-model-small-cn-0.22"
API_KEY = "sk-5e504a60c13a4a6a9dc1ca483d50b8d0"
URL = "https://api.deepseek.com/v1/chat/completions"

# 大模型的API
client = OpenAI(
    base_url="https://api.deepseek.com/",
    api_key="sk-5e504a60c13a4a6a9dc1ca483d50b8d0"
)

#  数据库信息
DB_CONFIG = {
    "database": "finance01",
    "user": "python01_user37",
    "password": "python01_user37@123",
    "host": "110.41.115.206",
    "port": 8000
}

chat_history = []


def extract_audio(video_path, audio_path="temp_audio.wav"):
    """提取音频"""
    video = VideoFileClip(video_path)
    # 使用ffmpeg参数转换格式
    video.audio.write_audiofile(
        audio_path,
        codec='pcm_s16le',
        ffmpeg_params=["-ar", "16000", "-ac", "1"]
    )
    return audio_path


def get_duration_from_moviepy(url):
    """ 获取视频时长 """
    clip = VideoFileClip(url)
    return clip.duration

def audio_to_text(audio_path):
    """使用Vosk进行本地语音识别"""
    # 检查模型是否存在
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"未找到语音模型 {MODEL_PATH}")

    try:
        # 初始化模型和识别器
        model = Model(MODEL_PATH)
        wf = wave.open(audio_path, "rb")

        # 验证音频格式是否符合要求
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            raise ValueError("音频格式不符合要求，需要单声道、16bit PCM格式")

        recognizer = KaldiRecognizer(model, wf.getframerate())

        results = []
        while True:
            data = wf.readframes(4000)  # 每次读取4000帧
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                res = json.loads(recognizer.Result())
                results.append(res.get("text", ""))

        # 获取最终结果
        final_res = json.loads(recognizer.FinalResult())
        results.append(final_res.get("text", ""))

        return "".join(results).strip()

    except Exception as e:
        return f"识别失败：{str(e)}"

def analyze_info(news_content: str) -> str:
    """使用大模型总结视频内容"""
    try:
        completion = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "用户将提供一段视频的语音识别内容，内容较为粗糙，请你分析这段内容，并提取其中的关键信息，以严格规范的JSON格式输出。JSON需包含主题、关键字、事件概要，其中事件概要不超过200字"
                },
                {
                    "role": "user",
                    "content": news_content
                }
            ],
            temperature=0.3,  # 降低随机性确保格式正确
            response_format={  # 明确要求返回JSON格式
                "type": "json_object"
            }
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"API请求失败: {str(e)}"

def get_ai_response(user_input, api_key, scenario):
    global chat_history

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 构建完整消息队列
    messages = [
        {"role": "system", "content": scenario},
        *chat_history[-30:],
        {"role": "user", "content": user_input}
    ]

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 400
    }

    try:
        response = requests.post(URL, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        if 'choices' not in data or len(data['choices']) == 0:
            return "未能获取有效响应，请重试"

        ai_reply = data['choices'][0]['message']['content']

        # 更新对话历史（限制最多保留3轮）
        chat_history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": ai_reply}
        ])
        chat_history = chat_history[-30:]  # 保留最近3轮对话

        return ai_reply

    except requests.exceptions.HTTPError as e:
        return f"HTTP错误: {e.response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"网络连接异常: {str(e)}"
    except KeyError:
        return "响应解析失败"
    except Exception as e:
        return f"未知错误: {str(e)}"

def chat_loop(SCENARIO_PROMPT):
    print("=== 问答系统 ===")
    print("输入 'exit' 退出对话\n")

    while True:
        try:
            user_input = input("你: ")
            if user_input.lower() in ['exit', 'quit']:
                print("\n对话已结束")
                break

            if not user_input.strip():
                print("请输入有效内容")
                continue

            response = get_ai_response(user_input, API_KEY, SCENARIO_PROMPT)
            print(f"\n回答: {response}\n")

        except KeyboardInterrupt:
            print("\n检测到中断，退出对话")
            break

def count_check():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 查询数据条数的SQL语句
    count_query = """ 
        SELECT COUNT(*) FROM video_info;
    """

    cursor.execute(count_query)
    count = cursor.fetchone()[0]  # 获取查询结果中的计数值
    conn.close()
    return count

def get_data(id):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 查询指定ID数据的SQL语句
    select_query = """ 
        SELECT * FROM {} 
        WHERE video_id = %s;
    """.format("video_info")
    cursor.execute(select_query, (id,))
    record = cursor.fetchone()
    conn.close()
    record = f"第{id}条视频的内容为：{record}\n"
    return record

# 示例使用
if __name__ == "__main__":
    video_path = "video_2.mp4"
    SCENARIO_PROMPT = '我将在下面给出有关视频的总结（id,主题，时长，摘要，主题），你只能根据总结的内容进行对话，总结若提问与这个无关，请回答“问题无法识别”\n'
    # 提取音频
    audio_path = extract_audio(video_path)
    print("音频提取成功，开始识别...")

    # 语音识别
    video_text = audio_to_text(audio_path)

    # 清理临时文件
    os.remove(audio_path)

    print("提取的文本：\n", video_text)

    result = analyze_info(video_text)
    print("分析结果：")
    print(result)
    print("传入到数据库中")
    data = json.loads(result)

    # 提取内容到变量
    id = count_check() + 1
    theme = data["主题"]
    keywords = data["关键字"]
    summary = data["事件概要"]
    times = get_duration_from_moviepy(video_path)

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO video_info (video_id, title, time, keywords, summary) VALUES (%s, %s, %s, %s, %s)",
        (id, theme, times, keywords, summary)
    )
    conn.commit()
    conn.close()
    print("传入完成")

    cnt = id
    while cnt > 0:
        SCENARIO_PROMPT += get_data(cnt)
        cnt -= 1

    chat_loop(SCENARIO_PROMPT)
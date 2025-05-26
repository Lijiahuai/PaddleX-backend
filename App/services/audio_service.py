import os
import uuid
import json
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer
from flask import current_app
import io


class AudioService:
    def __init__(self):
        """初始化语音服务类"""
        self.speech_model = None
        self.sample_rate = 16000

    def _initialize_speech_model(self):
        """初始化语音识别模型"""
        try:
            model_path = os.path.join(
                current_app.config.get('MODEL_FOLDER', 'models'),
                'vosk-model-cn-0.22'
            )
            self.speech_model = Model(model_path)
        except Exception as e:
            raise RuntimeError(f"语音模型加载失败: {str(e)}")

    def recognize_speech(self, paths):
        """
        识别多个音频文件中的语音
        :param paths: 音频文件路径列表
        :return: 列表，每个元素是 {'text': '对应识别文本'}
        """
        if not self.speech_model:
            self._initialize_speech_model()

        results = []

        try:
            for audio_path in paths:
                audio = AudioSegment.from_file(audio_path)
                audio = audio.set_channels(1).set_frame_rate(self.sample_rate)
                raw_audio = audio.raw_data

                recognizer = KaldiRecognizer(self.speech_model, self.sample_rate)

                text_parts = []
                chunk_size = 4000
                for i in range(0, len(raw_audio), chunk_size):
                    chunk = raw_audio[i:i + chunk_size]
                    if recognizer.AcceptWaveform(chunk):
                        result = json.loads(recognizer.Result())
                        text_parts.append(result['text'].replace(" ", ''))

                final_result = json.loads(recognizer.FinalResult())
                if final_result.get('text'):
                    text_parts.append(final_result['text'].replace(" ", ''))

                results.append({"text": "\n".join(text_parts)})

            return results

        except Exception as e:
            raise RuntimeError(f"语音识别失败: {str(e)}")

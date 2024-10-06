import json
import argparse
import os
import wave
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

from PIL import Image
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import requests

from logger_setup import setup_logger

logger = setup_logger()
load_dotenv()



class ContentUploader:
    def __init__(self):
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY')
        self.aws_secret_key = os.getenv('AWS_SECRET_KEY')
        self.s3_bucket_name = "quark-kick-preview-storage"

    def get_arg(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Kick Preview Content Uploader.")
        parser.add_argument('-wfp', '--wave-file-path', required=True, help='Wave Audio File Path. wave length must be under 1 second.')
        parser.add_argument('-ifp', '--image-file-path', required=True, help='Image File Path. image file must be JPG or PNG and at least 500x500 pixels.')
        parser.add_argument('-t',   '--title', required=True, help='Audio Title. Example : Artist Name - Track name')
        parser.add_argument('-l',   '--link', required=True, help='Audio info link. link must at least start with "http".')

        args = parser.parse_args()
        
        if not args.wave_file_path or not args.image_file_path or not args.title or not args.link:
            print("Error: Missing required arguments.")
            parser.print_help()
            sys.exit(1)
        
        return args

    def audio_check(self, wave_file_path : str) -> None:
        if not wave_file_path.lower().endswith('.wav'):
            raise ValueError('The Wave file path must end with ".wav"')
            
        try:
            with wave.open(wave_file_path, 'rb') as wave_file:
                # チャンネル数、サンプル幅、サンプルレート、フレーム数を取得
                channels = wave_file.getnchannels()
                sample_width = wave_file.getsampwidth()
                frame_rate = wave_file.getframerate()
                frame_count = wave_file.getnframes()

                # 再生時間を計算
                duration = frame_count / float(frame_rate)

                logger.info(f"File: {wave_file_path}")
                logger.info(f"Channels: {channels}")
                logger.info(f"Sample Width: {sample_width}")
                logger.info(f"Frame Rate: {frame_rate}")
                logger.info(f"Frame Count: {frame_count}")
                logger.info(f"Duration: {duration:.2f} seconds")

                # 1秒未満かどうかをチェック
                if duration >= 1.0:
                    raise wave.Error(f"Error: {wave_file_path} is {duration:.2f} seconds, which is not under 1 second.")
                    
                else:
                    logger.info(f"Success: {wave_file_path} is under 1 second.")
                    print("OK")
        except wave.Error as e:
            raise e
        except Exception as e:
            raise e
        
    def image_check(self, image_file_path: str) -> None:
        if not (image_file_path.lower().endswith('.jpg') or image_file_path.lower().endswith('.png')):
            raise ValueError('The image file must be in JPG or PNG format.')

        try:
            with Image.open(image_file_path) as img:
                width, height = img.size  # 画像の幅と高さを取得

                logger.info(f"File: {image_file_path}")
                logger.info(f"Image format: {img.format}")
                logger.info(f"Width: {width}px, Height: {height}px")

                # フォーマットの確認
                if img.format not in ['JPEG', 'PNG']:
                    raise ValueError(f"Error: {image_file_path} is not a valid JPG or PNG file.")
                
                # 500x500px以上かどうかをチェック
                if width < 500 or height < 500:
                    raise ValueError(f"Error: {image_file_path} is {width}x{height}px, which is less than 500x500px.")
                else:
                    logger.info(f"Success: {image_file_path} is at least 500x500px.")
        except ValueError as e:
            raise e
        except Exception as e:
            raise e

    def link_check(self, link : str) -> bool:
        if not (link.lower().startswith('http')):
            raise ValueError('Link must start with "http"')
        try:
            response = urlopen(link)
            if response.status == 200:
                logger.info(f"link exists: {link}")
                return None
        except HTTPError as e:
            raise Exception(f"HTTPError: {e.code} for link: {link}")
        except URLError as e:
            raise Exception(f"URLError: {e.reason} for link: {link}")
        except Exception as e:
            raise e
        
    def to_s3(self, file_path, s3_key_name) -> str:
        try:
            s3 = boto3.client('s3', aws_access_key_id=self.aws_access_key, aws_secret_access_key=self.aws_secret_key, region_name="ap-northeast-1")
            s3_uri = f"s3://{self.s3_bucket_name}/{s3_key_name}"
            
            # # ファイルが既に存在している場合エラー
            # try:
            #     s3.head_object(Bucket=self.s3_bucket_name, Key=s3_key_name)
            #     raise ValueError(f"ValueError: The object '{self.s3_bucket_name}' already exists in bucket '{s3_key_name}'.")
            # except ClientError as e:
            #     if e.response['Error']['Code'] == '404':
            #         pass
            #     else:
            #         raise
            
            s3.upload_file(file_path, Bucket=self.s3_bucket_name, Key=s3_key_name)
            logger.info(f"Upload successful: {s3_key_name}")
            return s3_uri
        except FileNotFoundError as e:
            raise e
        except NoCredentialsError as e:
            raise e
        except Exception as e:
            raise e

    def put_content(self, title, wave_file_uri, image_file_uri, link) -> None:
        url = "http://localhost:5000/api/put-content"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "title": f"{title}",
            "wave_file_uri": f"{wave_file_uri}",
            "image_file_uri": f"{image_file_uri}",
            "link": f"{link}",
        }
        result = requests.put(url, data=json.dumps(data), headers=headers)
        print(result)
        result.raise_for_status()
        logger.info("Put request succeeded.")
        return None

if __name__ == "__main__":
    UP = ContentUploader()
    args = UP.get_arg()
    title = args.title; wave_file_path = args.wave_file_path; image_file_path = args.image_file_path; link = args.link
    UP.audio_check(wave_file_path); UP.image_check(image_file_path); UP.link_check(link)
    wave_file_uri = UP.to_s3(wave_file_path, f"audios/{wave_file_path.split('/')[-1]}")
    image_file_uri = UP.to_s3(image_file_path, f"images/{image_file_path.split('/')[-1]}")
    UP.put_content(
        title,
        wave_file_uri,
        image_file_uri,
        link
    )
    
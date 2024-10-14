import csv
import subprocess

# コマンドのテンプレート
command_template = [
    "rye", "run", "python", "content_uploader.py",
    "-wfp", "{audio_path}",
    "-ifp", "{image_path}",
    "-t", '"{title}"',
    "-l", "{link}"
]

# CSVファイルの読み込み
csv_file = "import.csv"

with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        # CSVのカラムに対応するデータを取り出す
        title = row[0]
        audio_path = row[1]
        image_path = row[2]
        link = row[3]

        # コマンドを生成
        command = [part.format(audio_path=audio_path, image_path=image_path, title=title, link=link)
                   if '{' in part else part for part in command_template]

        # コマンドの実行（表示だけでなく実行する場合はsubprocess.runに置き換える）
        # print(" ".join(command))
        # 実際にコマンドを実行する場合は以下を有効化
        subprocess.run(" ".join(command), shell=True)

